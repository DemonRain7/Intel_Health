# -*- coding: utf-8 -*-
"""
本地推理服务器 — OpenAI 兼容 API

提供 /v1/chat/completions 和 /v1/models 端点，
每个 agent 对应一个 merged 模型（懒加载）。

用法:
    python inference/local_server.py --port 8000
    python inference/local_server.py --port 8000 --models-dir models/merged
"""

from __future__ import annotations

import argparse
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer

# ── 配置 ──────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODELS_DIR = PROJECT_ROOT / "models" / "merged"

# agent → base model 映射（未训练的 agent 使用 base model）
AGENT_BASE_MODELS: dict[str, str] = {
    "symptom_normalizer": "Qwen/Qwen3-0.6B",
    "symptom_quality_grader": "Qwen/Qwen3-0.6B",
    "rag_relevance_grader": "Qwen/Qwen3-0.6B",
    "diagnosis_generator": "Qwen/Qwen3-1.7B",
    "drug_evidence_grader": "Qwen/Qwen3-0.6B",
    "drug_recommender": "Qwen/Qwen3-0.6B",  # 无 adapter，用 base
    "output_formatter": "Qwen/Qwen3-0.6B",  # 无 adapter，用 base
}

# ── FastAPI app ───────────────────────────────────────

app = FastAPI(title="IntelHealth Local Inference Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 模型管理 ──────────────────────────────────────────

_loaded_models: dict[str, dict[str, Any]] = {}
_load_lock = Lock()
_models_dir: Path = DEFAULT_MODELS_DIR


def _resolve_model_source(model_name: str) -> str | Path:
    """确定模型来源: merged 目录优先，否则回退到 HuggingFace base model."""
    merged_path = _models_dir / model_name
    if merged_path.is_dir() and any(merged_path.glob("*.safetensors")) or any(
        merged_path.glob("*.bin")
    ):
        return merged_path
    # 回退到 base model
    base = AGENT_BASE_MODELS.get(model_name)
    if base:
        print(f"⚠️  {model_name}: merged 目录不存在，回退到 base model {base}")
        return base
    raise FileNotFoundError(
        f"找不到模型 {model_name}（merged 路径: {merged_path}，且无 base 映射）"
    )


def _load_model(model_name: str) -> dict[str, Any]:
    """懒加载模型和 tokenizer（线程安全）。"""
    with _load_lock:
        if model_name in _loaded_models:
            return _loaded_models[model_name]

        source = _resolve_model_source(model_name)
        print(f"Loading model '{model_name}' from {source} ...")
        t0 = time.time()

        tokenizer = AutoTokenizer.from_pretrained(
            source, trust_remote_code=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            source,
            torch_dtype=torch.float32,  # CPU 推理用 float32
            device_map="cpu",
            trust_remote_code=True,
        )
        model.eval()

        elapsed = time.time() - t0
        print(f"✅ '{model_name}' loaded in {elapsed:.1f}s")

        entry = {"model": model, "tokenizer": tokenizer, "source": str(source)}
        _loaded_models[model_name] = entry
        return entry


# ── Pydantic 请求/响应模型 ─────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    temperature: float = 0.2
    max_tokens: int = 1000
    top_p: float = 0.9


class ChatCompletionChoice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: str = "stop"


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:12]}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = ""
    choices: list[ChatCompletionChoice] = []
    usage: Usage = Field(default_factory=Usage)


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    owned_by: str = "local"


class ModelListResponse(BaseModel):
    object: str = "list"
    data: list[ModelInfo] = []


# ── 端点 ──────────────────────────────────────────────

@app.get("/v1/models")
def list_models() -> ModelListResponse:
    """列出所有可用模型（=已知 agent 名称）。"""
    models = [ModelInfo(id=name) for name in sorted(AGENT_BASE_MODELS.keys())]
    return ModelListResponse(data=models)


@app.post("/v1/chat/completions")
def chat_completions(req: ChatCompletionRequest) -> ChatCompletionResponse:
    """OpenAI 兼容的 chat completions 端点。"""
    model_name = req.model
    if not model_name:
        raise HTTPException(status_code=400, detail="model field is required")

    # 允许传入完整路径或仅 agent 名称
    # 如果传入的是绝对路径（如 diagnosis-graph 的 model_path 解析结果），提取最后部分
    model_key = Path(model_name).name if "/" in model_name or "\\" in model_name else model_name

    # 不在已知列表中也允许（可能是 base model 名称等）
    try:
        entry = _load_model(model_key)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    tokenizer = entry["tokenizer"]
    model = entry["model"]

    # 构建 chat prompt
    chat_messages = [{"role": m.role, "content": m.content} for m in req.messages]

    try:
        text = tokenizer.apply_chat_template(
            chat_messages, tokenize=False, add_generation_prompt=True
        )
    except Exception:
        # 回退：直接拼接
        text = "\n".join(
            f"<|im_start|>{m.role}\n{m.content}<|im_end|>" for m in req.messages
        ) + "\n<|im_start|>assistant\n"

    inputs = tokenizer(text, return_tensors="pt")
    input_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=req.max_tokens,
            temperature=max(req.temperature, 0.01),
            top_p=req.top_p,
            do_sample=req.temperature > 0,
        )

    new_tokens = output_ids[0][input_len:]
    generated_text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    # Qwen3 思考模式：去掉 <think>...</think> 标签
    if "<think>" in generated_text:
        import re
        generated_text = re.sub(
            r"<think>[\s\S]*?</think>\s*", "", generated_text
        ).strip()

    completion_tokens = len(new_tokens)

    return ChatCompletionResponse(
        model=model_name,
        choices=[
            ChatCompletionChoice(
                message=ChatMessage(role="assistant", content=generated_text)
            )
        ],
        usage=Usage(
            prompt_tokens=input_len,
            completion_tokens=completion_tokens,
            total_tokens=input_len + completion_tokens,
        ),
    )


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "loaded_models": list(_loaded_models.keys()),
        "models_dir": str(_models_dir),
    }


# ── 入口 ──────────────────────────────────────────────

def main():
    global _models_dir
    parser = argparse.ArgumentParser(description="IntelHealth Local Inference Server")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument(
        "--models-dir",
        type=str,
        default=str(DEFAULT_MODELS_DIR),
        help="Path to merged models directory",
    )
    args = parser.parse_args()
    _models_dir = Path(args.models_dir)
    print(f"Models directory: {_models_dir}")
    print(f"Starting server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
