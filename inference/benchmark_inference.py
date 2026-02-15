# -*- coding: utf-8 -*-
"""
推理显存 & 时间 Benchmark 脚本

对比 CPU 与 GPU 推理的显存占用和延迟，生成 Markdown 表格。
每个 agent 对应一个 merged 模型或 base model，逐个加载、推理、记录。

用法:
    # CPU 推理
    python inference/benchmark_inference.py --device cpu

    # GPU 推理（需要 CUDA）
    python inference/benchmark_inference.py --device cuda

    # 指定输出文件
    python inference/benchmark_inference.py --device cuda --output docs/inference_benchmark.md
"""

from __future__ import annotations

import argparse
import gc
import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODELS_DIR = PROJECT_ROOT / "models" / "merged"

# agent 配置: agent_name → (base_model, has_sft)
AGENTS = {
    "symptom_normalizer":    ("Qwen/Qwen3-0.6B", True),
    "symptom_quality_grader":("Qwen/Qwen3-0.6B", True),
    "rag_relevance_grader":  ("Qwen/Qwen3-0.6B", True),
    "drug_evidence_grader":  ("Qwen/Qwen3-0.6B", True),
    "diagnosis_generator":   ("Qwen/Qwen3-1.7B", True),
    "drug_recommender":      ("Qwen/Qwen3-0.6B", False),
    "diagnosis_reviewer":    ("Qwen/Qwen3-1.7B", False),
    "output_formatter":      ("Qwen/Qwen3-0.6B", False),
}

# 测试 prompt（模拟真实 pipeline 输入）
TEST_MESSAGES = [
    {"role": "system", "content": "你是医学助理，请将用户口语症状整理为专业、结构化描述。只输出JSON。"},
    {"role": "user", "content": (
        "身体部位: 背部\n主要症状: 肩颈疼痛，脊椎僵硬\n"
        "其他症状: 洗碗久了腰就不舒服\n严重程度: 3\n持续时间: 超过4周\n\n"
        '输出格式：\n{"optimized_symptoms": "...", "rag_keywords": ["..."]}'
    )},
]


def get_gpu_mem_mb() -> float:
    """返回当前 GPU 显存占用 (MB)。"""
    if torch.cuda.is_available():
        return torch.cuda.memory_allocated() / 1024 / 1024
    return 0.0


def get_gpu_peak_mb() -> float:
    """返回 GPU 峰值显存占用 (MB)。"""
    if torch.cuda.is_available():
        return torch.cuda.max_memory_allocated() / 1024 / 1024
    return 0.0


def get_model_param_mb(model) -> float:
    """计算模型参数占用内存 (MB)。"""
    total_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
    return total_bytes / 1024 / 1024


def resolve_model_source(agent_name: str, models_dir: Path) -> str | Path:
    """确定模型来源。"""
    merged_path = models_dir / agent_name
    if merged_path.is_dir() and (
        any(merged_path.glob("*.safetensors")) or any(merged_path.glob("*.bin"))
    ):
        return merged_path
    base_model, _ = AGENTS[agent_name]
    return base_model


def benchmark_agent(agent_name: str, device: str, models_dir: Path, max_new_tokens: int = 200):
    """
    对单个 agent 做推理 benchmark。
    返回 dict: {agent, model_source, params_mb, load_time, infer_time, mem_after_load, mem_peak_infer}
    """
    source = resolve_model_source(agent_name, models_dir)
    dtype = torch.float16 if device == "cuda" else torch.float32

    # 清理
    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        mem_before = get_gpu_mem_mb()
    else:
        mem_before = 0.0

    # 加载模型
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(source, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        source,
        torch_dtype=dtype,
        device_map=device if device == "cuda" else "cpu",
        trust_remote_code=True,
    )
    model.eval()
    load_time = time.time() - t0

    params_mb = get_model_param_mb(model)

    if device == "cuda":
        mem_after_load = get_gpu_mem_mb()
    else:
        mem_after_load = params_mb  # CPU 下用参数大小近似

    # 构建输入
    text = tokenizer.apply_chat_template(TEST_MESSAGES, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt")
    if device == "cuda":
        inputs = {k: v.to("cuda") for k, v in inputs.items()}

    input_len = inputs["input_ids"].shape[1]

    # 推理
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()

    t1 = time.time()
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.2,
            top_p=0.9,
            do_sample=True,
        )
    infer_time = time.time() - t1

    output_tokens = output_ids.shape[1] - input_len

    if device == "cuda":
        mem_peak_infer = get_gpu_peak_mb()
    else:
        mem_peak_infer = params_mb  # CPU 无精确显存指标

    # 清理
    del model, tokenizer, inputs, output_ids
    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()

    base_model, has_sft = AGENTS[agent_name]
    return {
        "agent": agent_name,
        "base_model": base_model,
        "sft": "Yes" if has_sft else "No (base)",
        "source": str(source),
        "params_mb": round(params_mb, 1),
        "load_time_s": round(load_time, 1),
        "infer_time_s": round(infer_time, 1),
        "output_tokens": output_tokens,
        "mem_after_load_mb": round(mem_after_load, 1),
        "mem_peak_infer_mb": round(mem_peak_infer, 1),
    }


def main():
    parser = argparse.ArgumentParser(description="IntelHealth Inference Benchmark")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--models-dir", type=str, default=str(DEFAULT_MODELS_DIR))
    parser.add_argument("--output", type=str, default=None, help="Output markdown file path")
    parser.add_argument("--max-tokens", type=int, default=200)
    parser.add_argument("--agents", nargs="*", default=None, help="Specific agents to benchmark (default: all)")
    args = parser.parse_args()

    models_dir = Path(args.models_dir)
    device = args.device

    if device == "cuda" and not torch.cuda.is_available():
        print("CUDA not available, falling back to CPU")
        device = "cpu"

    agents_to_test = args.agents or list(AGENTS.keys())

    print(f"Device: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    print(f"Models dir: {models_dir}")
    print(f"Agents: {', '.join(agents_to_test)}")
    print("=" * 60)

    results = []
    for agent_name in agents_to_test:
        if agent_name not in AGENTS:
            print(f"Unknown agent: {agent_name}, skipping")
            continue
        print(f"\nBenchmarking {agent_name}...")
        try:
            r = benchmark_agent(agent_name, device, models_dir, args.max_tokens)
            results.append(r)
            print(f"  Params: {r['params_mb']} MB | Load: {r['load_time_s']}s | "
                  f"Infer: {r['infer_time_s']}s | Tokens: {r['output_tokens']} | "
                  f"Mem load: {r['mem_after_load_mb']} MB | Mem peak: {r['mem_peak_infer_mb']} MB")
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"agent": agent_name, "error": str(e)})

    # 生成 Markdown 报告
    lines = [
        f"# IntelHealth 推理 Benchmark",
        f"",
        f"- **设备**: {device.upper()}" + (f" ({torch.cuda.get_device_name(0)})" if device == "cuda" else ""),
        f"- **精度**: {'float16' if device == 'cuda' else 'float32'}",
        f"- **max_new_tokens**: {args.max_tokens}",
        f"- **时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"## 各 Agent 推理指标",
        f"",
        f"| Agent | Base Model | SFT | 参数量(MB) | 加载(s) | 推理(s) | 输出Tokens | 加载后显存(MB) | 推理峰值显存(MB) |",
        f"|-------|-----------|-----|-----------|--------|--------|-----------|--------------|----------------|",
    ]

    total_infer = 0
    for r in results:
        if "error" in r:
            lines.append(f"| {r['agent']} | - | - | ERROR | - | - | - | - | {r['error']} |")
            continue
        total_infer += r["infer_time_s"]
        lines.append(
            f"| {r['agent']} | {r['base_model']} | {r['sft']} | "
            f"{r['params_mb']} | {r['load_time_s']} | {r['infer_time_s']} | "
            f"{r['output_tokens']} | {r['mem_after_load_mb']} | {r['mem_peak_infer_mb']} |"
        )

    lines.extend([
        f"",
        f"**Pipeline 总推理时间（不含加载）**: {round(total_infer, 1)}s",
        f"",
        f"## 说明",
        f"",
        f"- **加载后显存**: 模型加载到 {'GPU' if device == 'cuda' else '内存'} 后的占用",
        f"- **推理峰值显存**: 推理过程中的最大 {'显存' if device == 'cuda' else '内存'} 占用（含 KV cache）",
        f"- CPU 模式下显存指标为参数量估算值",
        f"- 每个 agent 单独加载测试，实际部署时多个 agent 共存会叠加",
    ])

    report = "\n".join(lines)
    print("\n" + "=" * 60)
    print(report)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"\nReport saved to {out_path}")

    # 同时输出 JSON 格式
    json_path = Path(args.output).with_suffix(".json") if args.output else None
    if json_path:
        json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON saved to {json_path}")


if __name__ == "__main__":
    main()
