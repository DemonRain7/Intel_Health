import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import tiktoken
from openai import OpenAI
from supabase import create_client


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PATH = (SCRIPT_DIR / "../datasets/rag/diagnosis/诊断学.txt").resolve()

INPUT_PATHS = [
    p.strip()
    for p in (os.getenv("RAG_DOCS_PATHS") or os.getenv("RAG_DOCS_PATH") or str(DEFAULT_PATH)).split(",")
    if p.strip()
]
BATCH_SIZE = int(os.getenv("RAG_BATCH_SIZE", "20"))
LIMIT = int(os.getenv("RAG_LIMIT", "0"))
RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-ada-002")
RAG_DOCS_CORPUS = os.getenv("RAG_DOCS_CORPUS", "")
TEXT_CHUNK_SIZE = int(os.getenv("RAG_TEXT_CHUNK_SIZE", "1200"))
TOKEN_CHUNK_SIZE = int(os.getenv("RAG_TOKEN_CHUNK_SIZE", os.getenv("RAG_TEXT_CHUNK_SIZE", "700")))
TOKEN_CHUNK_OVERLAP = int(os.getenv("RAG_TOKEN_CHUNK_OVERLAP", "100"))
EMBED_MAX_TOKENS = int(os.getenv("RAG_EMBEDDING_MAX_TOKENS", "8191"))
RESUME = os.getenv("RAG_RESUME") == "1"
STATE_PATH = Path(os.getenv("RAG_STATE_PATH", str((SCRIPT_DIR / "rag_ingest_state.json").resolve())))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY for ingestion.")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY for embedding generation.")

if TOKEN_CHUNK_SIZE <= 0:
    raise RuntimeError("RAG_TOKEN_CHUNK_SIZE must be greater than 0.")
if TOKEN_CHUNK_OVERLAP < 0:
    raise RuntimeError("RAG_TOKEN_CHUNK_OVERLAP must be >= 0.")

TOKEN_CHUNK_SIZE = min(TOKEN_CHUNK_SIZE, EMBED_MAX_TOKENS)
if TOKEN_CHUNK_OVERLAP >= TOKEN_CHUNK_SIZE:
    TOKEN_CHUNK_OVERLAP = max(0, TOKEN_CHUNK_SIZE // 4)

try:
    TOKENIZER = tiktoken.encoding_for_model(RAG_EMBEDDING_MODEL)
except KeyError:
    TOKENIZER = tiktoken.get_encoding("cl100k_base")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def build_content(item: Dict[str, Any]) -> str:
    if item.get("content"):
        return str(item["content"])

    question = f"Question: {item['question']}" if item.get("question") else ""
    options = ""
    if isinstance(item.get("options"), dict):
        options_text = "\n".join(f"{key}. {value}" for key, value in item["options"].items())
        if options_text:
            options = f"Options:\n{options_text}"
    answer = f"Answer: {item['answer']}" if item.get("answer") else ""

    return "\n\n".join(part for part in [question, options, answer] if part)


def build_metadata(item: Optional[Dict[str, Any]], source: str) -> Optional[Dict[str, Any]]:
    metadata: Dict[str, Any] = {}
    if item and item.get("meta_info"):
        metadata["meta_info"] = item["meta_info"]
    if source:
        metadata["source"] = source
    if RAG_DOCS_CORPUS:
        metadata["corpus"] = RAG_DOCS_CORPUS
    return metadata or None


def load_state() -> Dict[str, int]:
    if not RESUME or not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state: Dict[str, int]) -> None:
    if not RESUME:
        return
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def token_count(text: str) -> int:
    return len(TOKENIZER.encode(text))


def split_by_tokens(text: str) -> List[str]:
    text = text.strip()
    if not text:
        return []

    token_ids = TOKENIZER.encode(text)
    if len(token_ids) <= TOKEN_CHUNK_SIZE:
        return [text]

    step = max(1, TOKEN_CHUNK_SIZE - TOKEN_CHUNK_OVERLAP)
    chunks: List[str] = []
    for start in range(0, len(token_ids), step):
        piece_ids = token_ids[start : start + TOKEN_CHUNK_SIZE]
        if not piece_ids:
            break
        piece = TOKENIZER.decode(piece_ids).strip()
        if piece:
            chunks.append(piece)
        if start + TOKEN_CHUNK_SIZE >= len(token_ids):
            break
    return chunks


def embed_text(text: str) -> List[float]:
    tok_len = token_count(text)
    if tok_len > EMBED_MAX_TOKENS:
        raise RuntimeError(
            f"Chunk still too large for embedding: {tok_len} tokens > {EMBED_MAX_TOKENS}. "
            "Lower RAG_TOKEN_CHUNK_SIZE."
        )
    res = openai_client.embeddings.create(model=RAG_EMBEDDING_MODEL, input=text)
    return res.data[0].embedding


def flush_buffer(buffer: List[Dict[str, Any]]) -> None:
    if not buffer:
        return
    supabase.table("rag_documents").insert(buffer).execute()
    print(f"Inserted batch: {len(buffer)}")


def resolve_path(input_path: str) -> Path:
    p = Path(input_path)
    if p.exists():
        return p
    repo_relative = (Path.cwd() / input_path).resolve()
    if repo_relative.exists():
        return repo_relative
    return p


def ingest_jsonl(file_path_raw: str, state: Dict[str, int]) -> int:
    file_path = resolve_path(file_path_raw)
    resume_from = state.get(file_path_raw, 0)

    buffer: List[Dict[str, Any]] = []
    count = 0
    line_index = 0

    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line_index += 1
            if RESUME and line_index <= resume_from:
                continue
            if not line.strip():
                continue
            if LIMIT and count >= LIMIT:
                break

            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                print("Skip invalid JSON line.")
                continue

            content = build_content(item)
            if not content:
                continue

            for chunk in split_by_tokens(content):
                if LIMIT and count >= LIMIT:
                    break
                vector = embed_text(chunk)
                buffer.append(
                    {
                        "content": chunk,
                        "metadata": build_metadata(item, file_path.name),
                        "embedding": vector,
                    }
                )
                count += 1
                if buffer and len(buffer) >= BATCH_SIZE:
                    flush_buffer(buffer)
                    buffer = []
                    state[file_path_raw] = line_index
                    save_state(state)

    flush_buffer(buffer)
    state[file_path_raw] = line_index
    save_state(state)
    return count


def ingest_txt(file_path_raw: str, state: Dict[str, int]) -> int:
    file_path = resolve_path(file_path_raw)
    resume_from = state.get(file_path_raw, 0)

    buffer: List[Dict[str, Any]] = []
    count = 0
    line_index = 0
    chunk = ""

    def push_chunk(current_chunk: str) -> bool:
        nonlocal buffer, count
        if not current_chunk.strip():
            return False

        for part in split_by_tokens(current_chunk):
            if LIMIT and count >= LIMIT:
                flush_buffer(buffer)
                buffer = []
                return True

            vector = embed_text(part)
            buffer.append(
                {
                    "content": part,
                    "metadata": build_metadata(None, file_path.name),
                    "embedding": vector,
                }
            )
            count += 1

            if LIMIT and count >= LIMIT:
                flush_buffer(buffer)
                buffer = []
                return True

            if len(buffer) >= BATCH_SIZE:
                flush_buffer(buffer)
                buffer = []
        return False

    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line_index += 1
            if RESUME and line_index <= resume_from:
                continue

            trimmed = line.strip()
            if not trimmed:
                if chunk:
                    stop = push_chunk(chunk)
                    chunk = ""
                    if stop:
                        break
                continue

            if len((chunk + "\n" + trimmed) if chunk else trimmed) > TEXT_CHUNK_SIZE:
                stop = push_chunk(chunk)
                if stop:
                    break
                chunk = trimmed
            else:
                chunk = f"{chunk}\n{trimmed}" if chunk else trimmed

    if (not LIMIT or count < LIMIT) and chunk:
        push_chunk(chunk)

    flush_buffer(buffer)
    state[file_path_raw] = line_index
    save_state(state)
    return count


def ingest() -> None:
    state = load_state()
    total = 0

    for input_path in INPUT_PATHS:
        file_path = resolve_path(input_path)
        if not file_path.exists():
            raise RuntimeError(f"Input not found: {input_path}")
        ext = file_path.suffix.lower()
        print(f"Ingesting {input_path} (corpus={RAG_DOCS_CORPUS or 'default'})")
        if ext == ".jsonl":
            total += ingest_jsonl(input_path, state)
        elif ext == ".txt":
            total += ingest_txt(input_path, state)
        else:
            raise RuntimeError(f"Unsupported file type: {ext}")

    print(f"Done. Total inserted: {total}")


if __name__ == "__main__":
    ingest()
