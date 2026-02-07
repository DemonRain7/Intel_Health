# -*- coding: utf-8 -*-
"""
Build diagnosis DAPT/QA dataset from train_sft.jsonl.
This dataset is used for domain-adaptive training (Q&A), not structured output SFT.
"""
from __future__ import annotations

import argparse
import json
import os
from typing import Dict, Any, List, Optional


DEFAULT_INSTRUCTION = (
    "你是医学选择题作答器。请根据题干和选项选择正确答案，"
    "只输出选项编号（A/B/C/D/E），不要解释。"
)


def _format_options(options: Dict[str, str]) -> str:
    parts = []
    for key in sorted(options.keys()):
        parts.append(f"{key}. {options[key]}")
    return "\n".join(parts)


def _resolve_answer_idx(item: Dict[str, Any]) -> Optional[str]:
    if item.get("answer_idx"):
        return str(item["answer_idx"]).strip()
    # fallback: match answer text to options
    answer = str(item.get("answer", "")).strip()
    opts = item.get("options") or {}
    for k, v in opts.items():
        if str(v).strip() == answer:
            return str(k).strip()
    return None


def build_record(item: Dict[str, Any], instruction: str) -> Optional[Dict[str, Any]]:
    q = str(item.get("question", "")).strip()
    opts = item.get("options") or {}
    if not q or not opts:
        return None
    answer_idx = _resolve_answer_idx(item)
    if not answer_idx:
        return None

    human = (
        f"{instruction}\n\n"
        f"题目：{q}\n"
        f"选项：\n{_format_options(opts)}"
    )
    return {
        "conversations": [
            {"from": "human", "value": human},
            {"from": "gpt", "value": answer_idx}
        ]
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--instruction", type=str, default=DEFAULT_INSTRUCTION)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    start = 0
    if args.resume and os.path.exists(args.output):
        with open(args.output, "r", encoding="utf-8") as f:
            start = sum(1 for _ in f)

    written = 0
    with open(args.input, "r", encoding="utf-8") as fin, open(args.output, "a" if args.resume else "w", encoding="utf-8") as fout:
        for line in fin:
            if args.limit and written >= args.limit:
                break
            if not line.strip():
                continue
            item = json.loads(line)
            record = build_record(item, args.instruction)
            if record is None:
                continue
            if start > 0:
                start -= 1
                continue
            fout.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1

    print(f"Saved {written} samples -> {args.output}")


if __name__ == "__main__":
    main()
