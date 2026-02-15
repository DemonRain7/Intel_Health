# -*- coding: utf-8 -*-
"""
下载未 SFT 的 agent 所需的 base model 到 models/merged/ 目录。
这样所有 agent 的模型都在本地，不再依赖 HuggingFace cache。

用法:
    python inference/download_base_models.py
"""

from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MERGED_DIR = PROJECT_ROOT / "models" / "merged"

# 未 SFT 的 agent -> 需要下载的 base model
AGENTS_TO_DOWNLOAD = {
    "drug_recommender": "Qwen/Qwen3-0.6B",
    "output_formatter": "Qwen/Qwen3-0.6B",
    "diagnosis_reviewer": "Qwen/Qwen3-1.7B",
}


def download_and_save(agent_name: str, model_id: str):
    target_dir = MERGED_DIR / agent_name
    existing = list(target_dir.glob("*.safetensors")) if target_dir.is_dir() else []
    if existing:
        total_gb = sum(f.stat().st_size for f in existing) / (1024**3)
        threshold = 2.0 if "0.6B" in model_id else 5.0
        if total_gb < threshold:
            print(f"[OK] {agent_name} fp16 ok ({total_gb:.1f}GB), skip")
            return
        print(f"[!!] {agent_name} is fp32 ({total_gb:.1f}GB), re-saving as fp16...")

    print(f"[DL] Downloading {model_id} -> {target_dir} ...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        trust_remote_code=True,
    )

    target_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(target_dir)
    tokenizer.save_pretrained(target_dir)
    print(f"[OK] {agent_name} 保存完成: {target_dir}")


def main():
    print(f"目标目录: {MERGED_DIR}")
    print(f"需要下载 {len(AGENTS_TO_DOWNLOAD)} 个 base model\n")

    for agent, model_id in AGENTS_TO_DOWNLOAD.items():
        download_and_save(agent, model_id)

    print("\n全部完成！所有 agent 模型现在都在本地 models/merged/ 目录中。")
    print("你可以安全删除 HuggingFace cache 了（见下方说明）。")
    print()
    print("删除 HF cache 命令（PowerShell）:")
    print('  Remove-Item -Recurse -Force "$env:USERPROFILE\\.cache\\huggingface\\hub\\models--Qwen--Qwen3-0.6B"')
    print('  Remove-Item -Recurse -Force "$env:USERPROFILE\\.cache\\huggingface\\hub\\models--Qwen--Qwen3-1.7B"')


if __name__ == "__main__":
    main()
