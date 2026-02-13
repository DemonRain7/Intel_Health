# -*- coding: utf-8 -*-
"""
Build diagnosis_generator SFT dataset from train_sft.jsonl MCQ data.

Converts verified medical MCQ knowledge into diagnosis SFT training data
matching the pipeline's expected JSON output format:
  {results: [{condition, probability, description}], recommendations: [...], recomm_short: [...]}

Modes:
  --seed_mode:      Rule-based extraction from clinical MCQs (no API needed)
  --synthetic_mode: GPT-enhanced generation using MCQ as medical context

Usage:
    # Seed mode (no API, extracts clinical scenario MCQs):
    python build_diagnosis_sft.py \
      --input datasets/agent_sft/train_sft.jsonl \
      --output datasets/agent_sft/diagnosis_generator/diagnosis_sft.jsonl \
      --seed_mode

    # Synthetic mode (uses GPT, higher quality):
    python build_diagnosis_sft.py \
      --input datasets/agent_sft/train_sft.jsonl \
      --output datasets/agent_sft/diagnosis_generator/diagnosis_sft.jsonl \
      --synthetic_mode --num_samples 2000

    # Both modes combined:
    python build_diagnosis_sft.py \
      --input datasets/agent_sft/train_sft.jsonl \
      --output datasets/agent_sft/diagnosis_generator/diagnosis_sft.jsonl \
      --seed_mode --synthetic_mode --num_samples 3000
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import time
from typing import Dict, Any, List, Tuple


# ==================== Output format (matches diagnosis_generator.mjs) ====================

OUTPUT_FORMAT_SPEC = (
    '{\n'
    '  "results": [\n'
    '    {"condition": "...", "probability": 0.xx, "description": "..."}\n'
    '  ],\n'
    '  "recommendations": ["...","...","..."],\n'
    '  "recomm_short": ["..."x10]\n'
    '}'
)


# ==================== Clinical scenario detection ====================

_CLINICAL_PATTERNS = [
    re.compile(r'(男|女)[，,]\s*\d+岁'),
    re.compile(r'患者[，,]'),
    re.compile(r'(男|女)性?(患者|病人|儿童|婴儿|新生儿)'),
    re.compile(r'\d+岁(男|女)'),
    re.compile(r'(小儿|婴儿|新生儿).{0,5}(出生|生后|日龄|月龄)'),
]

_DIAGNOSIS_QUESTION_MARKERS = [
    "最可能的诊断", "诊断应首先考虑", "诊断为", "诊断是",
    "初步诊断", "该患者", "考虑诊断", "首先考虑",
    "最可能是", "应诊断为", "可能的疾病",
]

_SYMPTOM_KEYWORDS = [
    "疼痛", "发热", "咳嗽", "头痛", "腹痛", "恶心", "呕吐", "腹泻",
    "出血", "水肿", "肿胀", "乏力", "眩晕", "头晕", "胸闷", "气短",
    "瘙痒", "皮疹", "黄疸", "消瘦", "失眠", "心悸", "呼吸困难",
    "抽搐", "昏迷", "发绀", "浮肿", "尿频", "尿急", "血尿",
    "便血", "咯血", "呕血", "关节痛", "腰痛", "腹胀", "肿物",
    "包块", "溃疡", "糜烂", "坏死", "萎缩", "增生",
]

# Keywords that indicate the answer is a treatment/procedure (not a diagnosis)
_TREATMENT_ANSWER_KEYWORDS = [
    "治疗", "手术", "切除", "注射", "给予", "服用", "口服", "静注",
    "静脉", "肌注", "外用", "检查", "穿刺", "探查", "引流", "冲洗",
    "固定", "牵引", "缝合", "抗生素", "抗结核", "药物",
    "观察", "随访", "禁食", "补液", "输血", "吸氧", "气管插管",
    "透析", "放疗", "化疗", "激素", "阿托品", "吗啡", "肝素",
    "复位", "减压", "置换", "移植", "扩张", "造影", "活检",
    "DSA", "CT", "MRI", "PET", "EEG", "B超", "X线",
    "石膏", "夹板", "绷带", "悬吊",
]

# Keywords in the question that indicate it asks about treatment/test, not diagnosis
_TREATMENT_QUESTION_KEYWORDS = [
    "宜选用", "首选的治疗", "最适当的处理", "处理措施",
    "治疗方案", "如何处理", "应如何", "首选药物",
    "最佳治疗", "治疗原则", "用药", "给药",
    "治疗方法", "治疗是", "哪项检查", "应做",
    "检查方法", "哪种检查", "辅助检查",
]


def _is_clinical_scenario(question: str) -> bool:
    """Check if MCQ describes a patient scenario with symptoms."""
    for pat in _CLINICAL_PATTERNS:
        if pat.search(question):
            return True
    return sum(1 for kw in _SYMPTOM_KEYWORDS if kw in question) >= 2


def _is_treatment_question(question: str) -> bool:
    """Check if the question asks about treatment/procedure (not diagnosis)."""
    return any(kw in question for kw in _TREATMENT_QUESTION_KEYWORDS)


def _is_treatment_answer(answer: str) -> bool:
    """Check if the answer looks like a treatment/procedure rather than a disease."""
    return any(kw in answer for kw in _TREATMENT_ANSWER_KEYWORDS)


def _has_diagnosis_question(question: str) -> bool:
    """Check if the MCQ asks about diagnosis (not treatment/mechanism)."""
    return any(m in question for m in _DIAGNOSIS_QUESTION_MARKERS)


# ==================== Symptom extraction ====================

_QUESTION_CUTOFF_MARKERS = [
    "最可能的诊断", "诊断应首先考虑", "首选的治疗",
    "最适当的处理", "应首先", "该诊断", "其诊断",
    "首先考虑", "初步诊断", "下列哪项", "下述哪项",
    "下列哪种", "应如何", "如何处理", "最有意义的",
    "最有助于", "最重要的", "最常见的", "最可能出现",
]


def _extract_symptoms(question: str) -> str:
    """Extract patient presentation from the question, removing the actual question part."""
    q = question.strip()
    q = re.sub(r'^\d+[．.、]\s*', '', q)

    # Find the best cutoff point
    best_idx = len(q)
    for marker in _QUESTION_CUTOFF_MARKERS:
        idx = q.find(marker)
        if 15 < idx < best_idx:
            best_idx = idx

    q = q[:best_idx].rstrip("（。，,、？?）() ")
    return q


# ==================== Recommendation templates ====================

_RECOMMENDATIONS = {
    "default": {
        "long": [
            "建议尽早到正规医院就诊，配合必要的检查以明确诊断。",
            "注意休息，保持良好的作息习惯，避免过度劳累。",
            "如症状加重或出现新的不适，应立即就医。",
        ],
        "short": [
            "及时就医", "注意休息", "均衡饮食", "适量饮水",
            "避免劳累", "规律作息", "保持心情", "遵医嘱",
            "定期复查", "记录症状",
        ],
    },
    "外科": {
        "long": [
            "建议到外科就诊，必要时进行影像学检查明确诊断。",
            "受伤部位注意制动休息，避免再次损伤加重病情。",
            "密切观察症状变化，如疼痛加剧或功能障碍应立即就医。",
        ],
        "short": [
            "外科就诊", "影像检查", "局部制动", "冷敷消肿",
            "观察变化", "避免负重", "按时复诊", "遵医嘱",
            "注意伤口", "营养支持",
        ],
    },
    "内科": {
        "long": [
            "建议到内科就诊，完善血常规、生化等基础检查。",
            "注意饮食调理，清淡为主，避免辛辣刺激性食物。",
            "按医嘱规律服药，定期复查，监测病情变化。",
        ],
        "short": [
            "内科就诊", "清淡饮食", "规律服药", "定期复查",
            "监测指标", "避免刺激", "充足睡眠", "适度运动",
            "戒烟限酒", "控制情绪",
        ],
    },
    "妇产科": {
        "long": [
            "建议到妇产科就诊，完善妇科检查及B超等辅助检查。",
            "注意个人卫生，保持外阴清洁，避免不洁接触。",
            "如出现异常出血或腹痛加重，应立即就医。",
        ],
        "short": [
            "妇科就诊", "B超检查", "注意卫生", "避免劳累",
            "定期产检", "均衡营养", "充足休息", "观察出血",
            "记录月经", "遵医嘱",
        ],
    },
    "神经": {
        "long": [
            "建议到神经内科就诊，必要时行脑电图或头颅影像检查。",
            "保持规律作息，避免精神紧张和过度用脑。",
            "如出现意识障碍或肢体无力加重应立即急诊就医。",
        ],
        "short": [
            "神经科就诊", "影像检查", "规律作息", "避免紧张",
            "充足睡眠", "观察意识", "记录发作", "遵医嘱",
            "避免驾驶", "定期复查",
        ],
    },
    "儿科": {
        "long": [
            "建议到儿科就诊，注意监测体温变化和精神状态。",
            "保证充足的液体摄入，饮食以清淡易消化为主。",
            "密切观察病情，如高热不退或精神萎靡应立即就医。",
        ],
        "short": [
            "儿科就诊", "监测体温", "多饮水", "清淡饮食",
            "充足休息", "观察精神", "按时服药", "注意隔离",
            "记录症状", "定期复查",
        ],
    },
    "皮肤": {
        "long": [
            "建议到皮肤科就诊，必要时进行皮肤镜或活检明确诊断。",
            "避免搔抓患处，保持皮肤清洁干燥，穿棉质宽松衣物。",
            "遵医嘱用药，注意观察药物反应和皮损变化。",
        ],
        "short": [
            "皮肤科就诊", "避免搔抓", "保持清洁", "棉质衣物",
            "避免过敏原", "遵医嘱", "按时用药", "避免日晒",
            "清淡饮食", "定期复查",
        ],
    },
}

_CATEGORY_MAP = {
    "外科": "外科", "骨科": "外科", "运动系统": "外科",
    "内科": "内科", "消化": "内科", "呼吸": "内科", "循环": "内科",
    "心血管": "内科", "泌尿": "内科", "血液": "内科", "内分泌": "内科",
    "妇产": "妇产科", "女性生殖": "妇产科",
    "神经": "神经", "精神": "神经",
    "儿科": "儿科", "小儿": "儿科",
    "皮肤": "皮肤", "皮肤病": "皮肤",
}


def _get_category(meta_info: str) -> str:
    for keyword, cat in _CATEGORY_MAP.items():
        if keyword in meta_info:
            return cat
    return "default"


# ==================== Prompt builders ====================

def _build_human_prompt(symptoms: str, rag_context: str) -> str:
    """Build human prompt matching diagnosis_generator.mjs inference format."""
    rag_json = json.dumps(
        [{"doc_id": "doc_001", "score": 0.75, "snippet": rag_context}],
        ensure_ascii=False,
    )
    return (
        f"症状：{symptoms}\n"
        f"RAG文档：{rag_json}\n\n"
        f"输出格式：\n{OUTPUT_FORMAT_SPEC}"
    )


def _build_gpt_response(
    primary: str,
    primary_desc: str,
    alternatives: List[Tuple[str, str]],
    category: str,
    rng: random.Random,
) -> str:
    """Build GPT response JSON matching pipeline output format."""
    p1 = round(rng.uniform(0.40, 0.60), 2)
    remaining = round(1.0 - p1, 2)

    results = [{"condition": primary, "probability": p1, "description": primary_desc}]

    if len(alternatives) >= 2:
        p2 = round(rng.uniform(remaining * 0.45, remaining * 0.65), 2)
        p3 = round(remaining - p2, 2)
        results.append({"condition": alternatives[0][0], "probability": p2, "description": alternatives[0][1]})
        results.append({"condition": alternatives[1][0], "probability": p3, "description": alternatives[1][1]})
    elif len(alternatives) == 1:
        p2 = round(remaining * 0.65, 2)
        p3 = round(remaining - p2, 2)
        results.append({"condition": alternatives[0][0], "probability": p2, "description": alternatives[0][1]})
        results.append({"condition": "其他待查疾病", "probability": p3, "description": "需进一步检查排除其他可能。"})
    else:
        p2 = round(remaining * 0.6, 2)
        p3 = round(remaining - p2, 2)
        results.append({"condition": "待进一步检查", "probability": p2, "description": "需结合辅助检查明确。"})
        results.append({"condition": "其他可能", "probability": p3, "description": "不排除其他诊断的可能。"})

    rec = _RECOMMENDATIONS.get(category, _RECOMMENDATIONS["default"])
    output = {
        "results": results,
        "recommendations": rec["long"],
        "recomm_short": rec["short"],
    }
    return json.dumps(output, ensure_ascii=False)


# ==================== Seed mode ====================

def build_seed_samples(
    items: List[Dict[str, Any]],
    limit: int = 0,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """Build SFT samples from clinical scenario MCQs (no API needed)."""
    rng = random.Random(seed)
    samples = []
    skipped_not_clinical = 0
    skipped_short = 0
    skipped_no_answer = 0
    skipped_treatment = 0

    for item in items:
        if limit and len(samples) >= limit:
            break

        question = item.get("question", "").strip()
        options = item.get("options", {})
        answer = item.get("answer", "").strip()
        answer_idx = item.get("answer_idx", "").strip()
        meta_info = item.get("meta_info", "")

        # Must be a clinical scenario
        if not _is_clinical_scenario(question):
            skipped_not_clinical += 1
            continue

        if not answer or not options:
            skipped_no_answer += 1
            continue

        # Skip treatment/procedure questions (answer should be a disease, not a treatment)
        if _is_treatment_question(question) or _is_treatment_answer(answer):
            skipped_treatment += 1
            continue

        # Extract symptoms
        symptoms = _extract_symptoms(question)
        if len(symptoms) < 20:
            skipped_short += 1
            continue

        category = _get_category(meta_info)
        rag_context = f"{meta_info}领域相关知识参考。"

        # Primary diagnosis: use correct answer
        primary = answer.strip().rstrip("。")
        if len(primary) > 50:
            primary = primary[:50]
        primary_desc = f"根据临床表现，{primary}的可能性较大。"

        # Alternatives: other options (shuffle and pick 2)
        alts = []
        for k, v in options.items():
            if k != answer_idx:
                cond = v.strip().rstrip("。")
                if 2 < len(cond) <= 35:
                    alts.append((cond, "可能性较低，需鉴别诊断排除。"))
        rng.shuffle(alts)

        human = _build_human_prompt(symptoms, rag_context)
        gpt = _build_gpt_response(primary, primary_desc, alts, category, rng)

        samples.append({
            "conversations": [
                {"from": "human", "value": human},
                {"from": "gpt", "value": gpt},
            ]
        })

    print(
        f"Seed: {len(samples)} samples | skipped: "
        f"not_clinical={skipped_not_clinical} treatment={skipped_treatment} "
        f"short={skipped_short} no_answer={skipped_no_answer}",
        flush=True,
    )
    return samples


# ==================== Synthetic mode (GPT) ====================

_SYNTH_SYSTEM = """\
你是一个医学数据生成助手。对于给定的每道医学选择题，先判断它是否为临床诊断场景：

✓ 符合（生成数据）：题目描述了真实患者的症状/体征/检查结果，问的是"最可能的诊断"、\
"最可能患有什么病"等诊断类问题。
✗ 不符合（输出 null）：问的是治疗方案、用药选择、手术方式、辅助检查项目、病理机制、\
预防措施等非诊断类问题。

对于符合的题目，生成一条 SFT 数据：
{
  "input": {
    "optimized_symptoms": "患者症状描述，50-100字，包含年龄性别、主诉、体征",
    "ragContext": "相关医学背景知识，30-60字"
  },
  "output": {
    "results": [
      {"condition": "最可能疾病", "probability": 0.xx, "description": "15-30字描述"},
      {"condition": "次可能疾病", "probability": 0.yy, "description": "描述"},
      {"condition": "第三可能", "probability": 0.zz, "description": "描述"}
    ],
    "recommendations": ["详细建议1(>=15字)", "详细建议2(>=15字)", "详细建议3(>=15字)"],
    "recomm_short": ["简短1", "简短2", "简短3", "简短4", "简短5",
                      "简短6", "简短7", "简短8", "简短9", "简短10"]
  }
}

生成要求：
1. 症状描述真实具体，包含年龄性别
2. 概率之和约为1，符合医学常识
3. recommendations 正好 3 条（每条>=15字），recomm_short 正好 10 条（每条<=10字）
4. 只输出严格合法 JSON（双引号，无注释，无 Markdown）"""

_SYNTH_USER = """\
以下是 {n} 道医学选择题。对每道题先判断是否为临床诊断场景，\
符合则生成一条 SFT 数据，不符合则输出 null。{variation_hint}

{mcq_text}

返回格式（data 数组长度必须等于题目数 {n}，不符合题目位置填 null）：\
{{"data": [数据或null, ...]}}"""


def build_synthetic_samples(
    items: List[Dict[str, Any]],
    num_samples: int,
    batch_size: int = 5,
    api_key: str = "",
    base_url: str | None = None,
    model: str = "gpt-4.1",
    price_in: float = 0.0,
    price_out: float = 0.0,
) -> List[Dict[str, Any]]:
    """Build SFT samples using GPT with MCQ knowledge as context.

    Only processes clinical diagnosis MCQs (pre-filtered). Loops cyclically
    through valid items until num_samples is reached.
    """
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    total_tokens = 0
    total_cost = 0.0
    ip = price_in / 1_000_000
    op = price_out / 1_000_000
    json_format_ok = True

    rng = random.Random(42)
    shuffled = list(items)
    rng.shuffle(shuffled)

    samples: List[Dict[str, Any]] = []
    idx = 0        # current position in shuffled
    loop = 0       # how many times we've looped through all items
    bi = 0         # batch counter (for logging)
    skipped_by_gpt = 0
    start_ts = time.time()

    while len(samples) < num_samples:
        # Build next batch, cycling through shuffled as needed
        batch = []
        for _ in range(batch_size):
            if idx >= len(shuffled):
                idx = 0
                loop += 1
                rng.shuffle(shuffled)
            batch.append(shuffled[idx])
            idx += 1

        mcq_lines = []
        for i, it in enumerate(batch, 1):
            q = it.get("question", "")
            opts = it.get("options", {})
            ans_idx = it.get("answer_idx", "")
            opts_str = "\n".join(f"  {k}. {v}" for k, v in sorted(opts.items()))
            mcq_lines.append(f"第{i}题：{q}\n{opts_str}\n  正确答案：{ans_idx}")

        variation_hint = (
            f"（这是第{loop + 1}轮复用，请与之前生成不同年龄/性别/症状细节的患者场景）"
            if loop > 0 else ""
        )
        user_msg = _SYNTH_USER.format(
            n=len(batch),
            mcq_text="\n\n".join(mcq_lines),
            variation_hint=variation_hint,
        )
        bi += 1

        try:
            kwargs: Dict[str, Any] = dict(
                model=model,
                messages=[
                    {"role": "system", "content": _SYNTH_SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                max_completion_tokens=8000,
            )
            if json_format_ok:
                kwargs["response_format"] = {"type": "json_object"}

            try:
                resp = client.chat.completions.create(**kwargs)
            except Exception as e:
                if "response_format" in str(e).lower():
                    json_format_ok = False
                    kwargs.pop("response_format", None)
                    resp = client.chat.completions.create(**kwargs)
                else:
                    raise

            usage = resp.usage
            total_tokens += usage.prompt_tokens + usage.completion_tokens
            total_cost += usage.prompt_tokens * ip + usage.completion_tokens * op

            content = (resp.choices[0].message.content or "").strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            data = json.loads(content)
            if isinstance(data, dict):
                for key in ("data", "items", "results", "samples"):
                    if key in data and isinstance(data[key], list):
                        data = data[key]
                        break
                else:
                    data = [data]

            for d in data:
                if d is None:
                    skipped_by_gpt += 1
                    continue
                if not isinstance(d, dict) or "input" not in d or "output" not in d:
                    continue
                inp = d["input"]
                out = d["output"]
                if not all(k in out for k in ("results", "recommendations", "recomm_short")):
                    continue

                human = _build_human_prompt(
                    inp.get("optimized_symptoms", ""),
                    inp.get("ragContext", ""),
                )
                gpt = json.dumps(out, ensure_ascii=False)
                samples.append({
                    "conversations": [
                        {"from": "human", "value": human},
                        {"from": "gpt", "value": gpt},
                    ]
                })

            elapsed = time.time() - start_ts
            rate = len(samples) / max(elapsed, 1e-9)
            remaining = max(num_samples - len(samples), 0)
            eta = remaining / rate if rate > 0 else 0
            loop_str = f" loop={loop}" if loop > 0 else ""
            print(
                f"Batch {bi}: {len(samples)}/{num_samples} "
                f"({len(samples)/num_samples*100:.0f}%){loop_str} "
                f"skipped_by_gpt={skipped_by_gpt} "
                f"tokens={total_tokens:,} cost=${total_cost:.4f} "
                f"eta={eta:.0f}s",
                flush=True,
            )

            if len(samples) < num_samples:
                time.sleep(0.5)

        except Exception as e:
            print(f"Batch {bi} error: {e}", flush=True)
            continue

    print(
        f"Synthetic: {len(samples)} samples | "
        f"skipped_by_gpt={skipped_by_gpt} | "
        f"{total_tokens:,} tokens | ${total_cost:.4f}",
        flush=True,
    )
    return samples


# ==================== Main ====================

def main():
    parser = argparse.ArgumentParser(
        description="Build diagnosis SFT data from MCQs"
    )
    parser.add_argument("--input", type=str, required=True,
                        help="Path to train_sft.jsonl (raw MCQ data)")
    parser.add_argument("--output", type=str, required=True,
                        help="Output JSONL path")
    parser.add_argument("--seed_mode", action="store_true",
                        help="Template-based extraction (no API)")
    parser.add_argument("--synthetic_mode", action="store_true",
                        help="GPT-based generation")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max samples for seed mode (0=all)")
    parser.add_argument("--num_samples", type=int, default=2000,
                        help="Target samples for synthetic mode")
    parser.add_argument("--batch_size", type=int, default=5,
                        help="MCQs per GPT batch (synthetic mode)")
    parser.add_argument("--api_key", type=str, default=None)
    parser.add_argument("--base_url", type=str, default=None)
    parser.add_argument("--model", type=str, default="gpt-5.1")
    parser.add_argument("--price_in", type=float, default=0.0,
                        help="Input token price per 1M tokens")
    parser.add_argument("--price_out", type=float, default=0.0,
                        help="Output token price per 1M tokens")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--reset_output", action="store_true")
    parser.add_argument("--progress_every", type=int, default=100)
    args = parser.parse_args()

    if not args.seed_mode and not args.synthetic_mode:
        args.seed_mode = True

    # Load MCQ items
    print(f"Loading: {args.input}", flush=True)
    items: List[Dict[str, Any]] = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    print(f"Loaded {len(items)} MCQ items", flush=True)

    # Prepare output
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    output_abs = os.path.abspath(args.output)

    if args.reset_output and os.path.exists(args.output):
        os.remove(args.output)
        print(f"Reset: removed {output_abs}", flush=True)

    existing = 0
    if args.resume and os.path.exists(args.output):
        with open(args.output, "r", encoding="utf-8") as f:
            existing = sum(1 for _ in f)
        print(f"Resume: {existing} existing samples", flush=True)

    # ---- Generate ----
    samples: List[Dict[str, Any]] = []

    if args.seed_mode:
        samples = build_seed_samples(
            items, limit=args.limit or len(items), seed=args.seed
        )

    if args.synthetic_mode:
        api_key = args.api_key or os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            print("ERROR: --api_key or OPENAI_API_KEY required", flush=True)
            return
        target = max(args.num_samples - existing - len(samples), 0)
        if target > 0:
            synth = build_synthetic_samples(
                items, target,
                batch_size=args.batch_size,
                api_key=api_key,
                base_url=args.base_url,
                model=args.model,
                price_in=args.price_in,
                price_out=args.price_out,
            )
            samples.extend(synth)

    # ---- Write ----
    start_ts = time.time()
    mode = "a" if (args.resume and existing > 0) else "w"
    written = 0
    with open(args.output, mode, encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
            written += 1
            if args.progress_every > 0 and written % args.progress_every == 0:
                print(f"Writing: {written}/{len(samples)}", flush=True)

    elapsed = time.time() - start_ts
    print(
        f"Saved {written} samples -> {output_abs} "
        f"(total: {existing + written}) in {elapsed:.1f}s",
        flush=True,
    )


if __name__ == "__main__":
    main()
