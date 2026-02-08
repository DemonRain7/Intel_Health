# -*- coding: utf-8 -*-
"""
Preprocess/Symptom Normalizer SFT builder (multi-stage).

Pipeline:
1) gpt-5-mini (seed model) generates a natural complaint narrative.
2) gpt-5-mini maps narrative to fixed fields (body_part/symptoms/duration/severity).
3) gpt-4.1 generates standardized output (optimized_symptoms + rag_keywords).

Output supports instruction or conversation format.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from typing import Dict, List, Any, Tuple

from openai import OpenAI
from loguru import logger

try:
    from jsonschema import validate, ValidationError
except Exception:
    validate = None
    class ValidationError(Exception):
        pass

import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_sft_data import (
    BODY_PARTS,
    SYMPTOMS_BY_BODY_PART,
    DURATION_OPTIONS,
)


SEED_SCHEMA = {
    "type": "object",
    "required": ["complaint"],
    "properties": {
        "complaint": {"type": "string"},
        "other_symptoms": {"type": "string"},
    },
}

STRUCT_SCHEMA = {
    "type": "object",
    "required": ["body_part", "symptoms", "other_symptoms", "severity", "duration"],
    "properties": {
        "body_part": {"type": "string"},
        "symptoms": {"type": "array", "items": {"type": "string"}},
        "other_symptoms": {"type": "string"},
        "severity": {"type": "number"},
        "duration": {"type": "string"},
    },
}

OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["optimized_symptoms", "rag_keywords"],
    "properties": {
        "optimized_symptoms": {"type": "string"},
        "rag_keywords": {"type": "array", "items": {"type": "string"}},
    },
}


def _safe_json(content: str) -> Any:
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```", 1)[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content)


def _validate(schema: Dict[str, Any], item: Dict[str, Any]) -> bool:
    if validate is None:
        return True
    try:
        validate(instance=item, schema=schema)
        return True
    except ValidationError as exc:
        logger.warning(f"Schema validation failed: {exc}")
        return False


def _build_human_prompt(input_data: Dict[str, Any]) -> str:
    return (
        "请将以下症状信息转换为结构化的医学描述，并提取更具体的RAG关键词：\n"
        f"身体部位: {input_data.get('body_part', '')}\n"
        f"主要症状: {', '.join(input_data.get('symptoms', []))}\n"
        f"其他症状: {input_data.get('other_symptoms', '')}\n"
        f"严重程度(1-5): {input_data.get('severity', 3)}\n"
        f"持续时间: {input_data.get('duration', '')}\n\n"
        "要求：\n"
        "1) optimized_symptoms 用专业医学术语\n"
        "2) rag_keywords 必须细化到症状层面（如“腰部外伤疼痛”“腰椎间盘突出放射痛”）\n"
        "只输出 JSON：{\"optimized_symptoms\":\"...\",\"rag_keywords\":[\"...\"]}"
    )


def _call_chat(client: OpenAI, model: str, messages: List[Dict[str, str]], max_tokens: int = 2048) -> Tuple[str, int, int]:
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        max_completion_tokens=max_tokens,
    )
    usage = resp.usage
    content = resp.choices[0].message.content
    if not content:
        refusal = getattr(resp.choices[0].message, "refusal", None)
        raise ValueError(f"Empty response (finish_reason={resp.choices[0].finish_reason}, refusal={refusal})")
    return content.strip(), usage.prompt_tokens, usage.completion_tokens


def _fmt_duration(seconds: float) -> str:
    sec = max(int(seconds), 0)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m{s:02d}s"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"


def generate_seed_case(client: OpenAI, model: str) -> Tuple[Dict[str, Any], int, int]:
    system = (
        "你是医学病例模拟器。请生成真实口语化的患者主诉，包含主要症状、伴随症状、持续时间和严重程度。"
        "只输出严格合法 JSON，不要 Markdown。"
    )
    user = (
        "输出 JSON：\n"
        "{\n"
        "  \"complaint\": \"患者口语化描述\",\n"
        "  \"other_symptoms\": \"补充症状（可为空）\"\n"
        "}"
    )
    content, in_toks, out_toks = _call_chat(
        client, model,
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=2048,
    )
    data = _safe_json(content)
    if not _validate(SEED_SCHEMA, data):
        raise ValueError("Seed schema invalid")
    return data, in_toks, out_toks


def map_to_struct(client: OpenAI, model: str, seed: Dict[str, Any]) -> Tuple[Dict[str, Any], int, int]:
    body_parts = ", ".join(BODY_PARTS)
    symptom_map = {k: v for k, v in SYMPTOMS_BY_BODY_PART.items()}
    system = (
        "你是医学结构化标注助手。请根据主诉选择固定字段。"
        "只输出严格合法 JSON，不要 Markdown。"
    )
    user = (
        f"主诉: {seed.get('complaint','')}\n"
        f"补充症状: {seed.get('other_symptoms','')}\n\n"
        f"可选身体部位: {body_parts}\n"
        f"可选症状(按部位): {json.dumps(symptom_map, ensure_ascii=False)}\n"
        f"可选持续时间代码: {', '.join(DURATION_OPTIONS)}\n\n"
        "请输出 JSON：\n"
        "{\n"
        "  \"body_part\": \"...\",\n"
        "  \"symptoms\": [\"...\", \"...\"],\n"
        "  \"other_symptoms\": \"...\",\n"
        "  \"severity\": 1-5,\n"
        "  \"duration\": \"lessThan24Hours|1To3Days|4To7Days|1To2Weeks|moreThan2Weeks\"\n"
        "}\n"
        "要求：symptoms 必须从可选症状里选择；若不匹配，选择最接近的。"
    )
    content, in_toks, out_toks = _call_chat(
        client, model,
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=2048,
    )
    data = _safe_json(content)
    if not _validate(STRUCT_SCHEMA, data):
        raise ValueError("Struct schema invalid")
    return data, in_toks, out_toks


def generate_output(client: OpenAI, model: str, input_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int, int]:
    system = (
        "你是医学数据生成助手。请输出 optimized_symptoms 和 rag_keywords。"
        "只输出严格合法 JSON，不要 Markdown。"
    )
    user = _build_human_prompt(input_data)
    content, in_toks, out_toks = _call_chat(
        client, model,
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=2048,
    )
    data = _safe_json(content)
    if not _validate(OUTPUT_SCHEMA, data):
        raise ValueError("Output schema invalid")
    return data, in_toks, out_toks


def to_conversation(input_data: Dict[str, Any], output_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "conversations": [
            {"from": "human", "value": _build_human_prompt(input_data)},
            {"from": "gpt", "value": json.dumps(output_data, ensure_ascii=False)},
        ]
    }


def to_instruction(input_data: Dict[str, Any], output_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "instruction": "请将以下用户症状信息转换为结构化的医学描述，并提取RAG检索关键词。",
        "input": input_data,
        "output": output_data,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_samples", type=int, default=500)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--seed_model", type=str, default="gpt-5-mini")
    parser.add_argument("--final_model", type=str, default="gpt-4.1")
    parser.add_argument("--api_key", type=str, default=None)
    parser.add_argument("--base_url", type=str, default=None)
    parser.add_argument("--output_format", type=str, default="conversation", choices=["conversation", "instruction"])
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--reset_output", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.3)
    parser.add_argument("--progress_every", type=int, default=10)
    parser.add_argument("--price_in_seed", type=float, default=0.0)
    parser.add_argument("--price_out_seed", type=float, default=0.0)
    parser.add_argument("--price_in_final", type=float, default=0.0)
    parser.add_argument("--price_out_final", type=float, default=0.0)
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY")

    client = OpenAI(api_key=api_key, base_url=args.base_url)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    output_abs = os.path.abspath(args.output)
    logger.info(f"Output file: {output_abs}")
    if args.reset_output and os.path.exists(args.output):
        os.remove(args.output)
        logger.info(f"Reset enabled. Removed existing output: {output_abs}")
    existing = 0
    if args.resume and os.path.exists(args.output):
        with open(args.output, "r", encoding="utf-8") as f:
            existing = sum(1 for _ in f)
        logger.info(f"Resume enabled. Existing: {existing}")

    total_in_seed = total_out_seed = 0
    total_in_final = total_out_final = 0

    target = max(args.num_samples - existing, 0)
    if target == 0:
        logger.info(f"Already have {existing} samples, nothing to generate.")
        return
    written = 0
    consecutive_errors = 0
    total_errors = 0
    start_ts = time.time()
    with open(args.output, "a" if args.resume else "w", encoding="utf-8") as f:
        while written < target:
            if args.progress_every > 0 and (written == 0 or (written + 1) % args.progress_every == 1):
                logger.info(f"Generating sample {written + 1}/{target} ...")
            try:
                seed, in_s, out_s = generate_seed_case(client, args.seed_model)
                struct, in_m, out_m = map_to_struct(client, args.seed_model, seed)
                output, in_f, out_f = generate_output(client, args.final_model, struct)
            except Exception as exc:
                consecutive_errors += 1
                total_errors += 1
                logger.warning(f"Skip ({consecutive_errors}): {exc}")
                if consecutive_errors >= 10:
                    logger.error("Too many consecutive errors, stopping.")
                    break
                time.sleep(1)
                continue
            consecutive_errors = 0

            total_in_seed += in_s + in_m
            total_out_seed += out_s + out_m
            total_in_final += in_f
            total_out_final += out_f

            if args.output_format == "conversation":
                record = to_conversation(struct, output)
            else:
                record = to_instruction(struct, output)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
            written += 1
            if args.progress_every > 0 and (written == 1 or written % args.progress_every == 0 or written == target):
                elapsed = max(time.time() - start_ts, 1e-9)
                rate = written / elapsed
                remain = max(target - written, 0)
                eta = remain / rate if rate > 0 else 0.0
                logger.info(
                    "Progress: {}/{} ({:.1f}%) | speed={:.2f}/s | elapsed={} | eta={} | errors={}".format(
                        written, target, (written / target) * 100.0, rate, _fmt_duration(elapsed), _fmt_duration(eta), total_errors
                    )
                )
            if args.sleep:
                time.sleep(args.sleep)

    def _cost(tokens: int, price: float) -> float:
        return tokens / 1_000_000 * price

    seed_cost = _cost(total_in_seed, args.price_in_seed) + _cost(total_out_seed, args.price_out_seed)
    final_cost = _cost(total_in_final, args.price_in_final) + _cost(total_out_final, args.price_out_final)
    logger.info(f"Saved {written} samples -> {output_abs}")
    logger.info(f"Seed model tokens: in={total_in_seed:,} out={total_out_seed:,} cost=${seed_cost:.4f}")
    logger.info(f"Final model tokens: in={total_in_final:,} out={total_out_final:,} cost=${final_cost:.4f}")


if __name__ == "__main__":
    main()
