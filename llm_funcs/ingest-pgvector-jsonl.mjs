import fs from "fs";
import path from "path";
import readline from "readline";
import { fileURLToPath } from "url";
import { createClient } from "@supabase/supabase-js";
import { OpenAIEmbeddings } from "@langchain/openai";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DEFAULT_PATH = path.resolve(__dirname, "../datasets/rag/diagnosis/诊断学.txt");
const INPUT_PATHS = (process.env.RAG_DOCS_PATHS || process.env.RAG_DOCS_PATH || DEFAULT_PATH)
  .split(",")
  .map(p => p.trim())
  .filter(Boolean);
const BATCH_SIZE = Number(process.env.RAG_BATCH_SIZE || 20);
const LIMIT = Number(process.env.RAG_LIMIT || 0);
const RAG_EMBEDDING_MODEL = process.env.RAG_EMBEDDING_MODEL || "text-embedding-ada-002";
const RAG_DOCS_CORPUS = process.env.RAG_DOCS_CORPUS || "";
const TEXT_CHUNK_SIZE = Number(process.env.RAG_TEXT_CHUNK_SIZE || 1200);
const RESUME = process.env.RAG_RESUME === "1";
const STATE_PATH = process.env.RAG_STATE_PATH || path.resolve(__dirname, "rag_ingest_state.json");

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  throw new Error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY for ingestion.");
}

if (!process.env.OPENAI_API_KEY) {
  throw new Error("Missing OPENAI_API_KEY for embedding generation.");
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { persistSession: false }
});

const embeddings = new OpenAIEmbeddings({
  openAIApiKey: process.env.OPENAI_API_KEY,
  model: RAG_EMBEDDING_MODEL
});

const buildContent = (item) => {
  if (item.content) return String(item.content);
  const question = item.question ? `Question: ${item.question}` : "";
  let options = "";
  if (item.options && typeof item.options === "object") {
    options = Object.entries(item.options)
      .map(([key, value]) => `${key}. ${value}`)
      .join("\n");
    if (options) options = `Options:\n${options}`;
  }
  const answer = item.answer ? `Answer: ${item.answer}` : "";
  return [question, options, answer].filter(Boolean).join("\n\n");
};

const buildMetadata = (item, source) => {
  const metadata = {};
  if (item && item.meta_info) metadata.meta_info = item.meta_info;
  if (source) metadata.source = source;
  if (RAG_DOCS_CORPUS) metadata.corpus = RAG_DOCS_CORPUS;
  return Object.keys(metadata).length ? metadata : null;
};

const loadState = () => {
  if (!RESUME || !fs.existsSync(STATE_PATH)) return {};
  try {
    return JSON.parse(fs.readFileSync(STATE_PATH, "utf-8"));
  } catch {
    return {};
  }
};

const saveState = (state) => {
  if (!RESUME) return;
  fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2));
};

async function flushBuffer(buffer) {
  if (buffer.length === 0) return;
  const { error } = await supabase.from("rag_documents").insert(buffer);
  if (error) {
    throw new Error(`Supabase insert failed: ${error.message}`);
  }
  console.log(`Inserted batch: ${buffer.length}`);
}

async function ingestJsonl(filePath, state) {
  const stream = fs.createReadStream(filePath, { encoding: "utf-8" });
  const rl = readline.createInterface({ input: stream, crlfDelay: Infinity });

  let buffer = [];
  let count = 0;
  let lineIndex = 0;
  const resumeFrom = state[filePath] || 0;

  for await (const line of rl) {
    lineIndex += 1;
    if (RESUME && lineIndex <= resumeFrom) {
      continue;
    }
    if (!line.trim()) continue;
    if (LIMIT && count >= LIMIT) break;

    let item;
    try {
      item = JSON.parse(line);
    } catch (err) {
      console.warn("Skip invalid JSON line.");
      continue;
    }

    const content = buildContent(item);
    if (!content) continue;

    const vector = await embeddings.embedQuery(content);
    buffer.push({
      content,
      metadata: buildMetadata(item, path.basename(filePath)),
      embedding: vector
    });

    count += 1;
    if (buffer.length >= BATCH_SIZE) {
      await flushBuffer(buffer);
      buffer = [];
      state[filePath] = lineIndex;
      saveState(state);
    }
  }

  await flushBuffer(buffer);
  state[filePath] = lineIndex;
  saveState(state);
  return count;
}

async function ingestTxt(filePath, state) {
  const stream = fs.createReadStream(filePath, { encoding: "utf-8" });
  const rl = readline.createInterface({ input: stream, crlfDelay: Infinity });

  let buffer = [];
  let count = 0;
  let chunk = "";
  let lineIndex = 0;
  const resumeFrom = state[filePath] || 0;

  const pushChunk = async () => {
    if (!chunk.trim()) return;
    const vector = await embeddings.embedQuery(chunk);
    buffer.push({
      content: chunk,
      metadata: buildMetadata(null, path.basename(filePath)),
      embedding: vector
    });
    count += 1;
    chunk = "";

    if (LIMIT && count >= LIMIT) {
      await flushBuffer(buffer);
      buffer = [];
      return true;
    }
    if (buffer.length >= BATCH_SIZE) {
      await flushBuffer(buffer);
      buffer = [];
    }
    return false;
  };

  for await (const line of rl) {
    lineIndex += 1;
    if (RESUME && lineIndex <= resumeFrom) {
      continue;
    }
    const trimmed = line.trim();
    if (!trimmed) {
      if (chunk) {
        const stop = await pushChunk();
        if (stop) break;
      }
      continue;
    }
    if ((chunk + "\n" + trimmed).length > TEXT_CHUNK_SIZE) {
      const stop = await pushChunk();
      if (stop) break;
      chunk = trimmed;
    } else {
      chunk = chunk ? `${chunk}\n${trimmed}` : trimmed;
    }
  }

  if (!LIMIT || count < LIMIT) {
    await pushChunk();
  }

  await flushBuffer(buffer);
  state[filePath] = lineIndex;
  saveState(state);
  return count;
}

async function ingest() {
  const state = loadState();
  let total = 0;
  for (const inputPath of INPUT_PATHS) {
    if (!fs.existsSync(inputPath)) {
      throw new Error(`Input not found: ${inputPath}`);
    }
    const ext = path.extname(inputPath).toLowerCase();
    console.log(`Ingesting ${inputPath} (corpus=${RAG_DOCS_CORPUS || "default"})`);
    if (ext === ".jsonl") {
      total += await ingestJsonl(inputPath, state);
    } else if (ext === ".txt") {
      total += await ingestTxt(inputPath, state);
    } else {
      throw new Error(`Unsupported file type: ${ext}`);
    }
  }
  console.log(`Done. Total inserted: ${total}`);
}

ingest().catch((err) => {
  console.error(err);
  process.exit(1);
});
