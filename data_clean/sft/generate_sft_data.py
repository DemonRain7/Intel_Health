# -*- coding: utf-8 -*-
"""
SFT 数据生成脚本
使用 GPT-4.1 为 IntelHealth 各 Agent 生成训练数据（可通过 --model 指定）

Usage:
    # 生成 100 条测试数据（查看成本）
    python generate_sft_data.py --agent symptom_quality_grader --num_samples 100 --test_cost

    # 正式生成 5000 条数据
    python generate_sft_data.py --agent rag_relevance_grader --num_samples 5000

    # 生成所有可用 Agent 的数据（不含 diagnosis/drug）
    python generate_sft_data.py --agent all --num_samples 2000

Available agents:
    - symptom_normalizer: 症状结构化 (preprocessAndGuess)
    - symptom_quality_grader: 质量评分 (Critic_preprocess)
    - rag_relevance_grader: RAG 相关度评分 (checkRAG)
    - drug_evidence_grader: 诊断/用药证据评分 (drugRAGandScore)

Notes:
    - diagnosis_generator 走 DAPT/QA 数据（train_sft.jsonl），不再用 LLM 合成结构化 SFT。
    - drug_recommender 不做 SFT，仅走 RAG + Schema 约束。
"""

import os
import json
import argparse
import random
import time
from typing import List, Dict, Any
from openai import OpenAI
from tqdm import tqdm
from loguru import logger

try:
    from jsonschema import validate, ValidationError
except Exception:
    validate = None
    class ValidationError(Exception):
        pass


# ==================== 配置 ====================

# 身体部位列表
BODY_PARTS = [
    "头部", "眼睛", "耳朵", "鼻子", "口腔", "咽喉", "颈部",
    "胸部", "心脏", "肺部", "腹部", "胃部", "肝脏", "肾脏",
    "背部", "腰部", "四肢", "手臂", "腿部", "关节", "皮肤",
    "全身", "神经系统", "泌尿系统", "生殖系统"
]

# 症状严重程度
SEVERITY_LEVELS = [1, 2, 3, 4, 5]

# 持续时间选项
DURATION_OPTIONS = [
    "lessThan24Hours", "1To3Days", "4To7Days", "1To2Weeks", "moreThan2Weeks"
]

DURATION_CHINESE = {
    "lessThan24Hours": "24小时内",
    "1To3Days": "1至3天",
    "4To7Days": "4至7天",
    "1To2Weeks": "1至2周",
    "moreThan2Weeks": "超过2周"
}

# 症状与疾病种子数据（用于本地生成 seed 样本）
SYMPTOMS_BY_BODY_PART = {
    "头部": ["头痛", "头晕", "视物模糊", "恶心"],
    "咽喉": ["咽痛", "干咳", "喉咙痒", "声音嘶哑"],
    "胸部": ["胸闷", "胸痛", "气短", "心悸"],
    "腹部": ["肚子痛", "腹胀", "恶心", "拉肚子"],
    "胃部": ["胃痛", "反酸", "嗳气", "恶心"],
    "皮肤": ["瘙痒", "皮疹", "红肿", "脱屑"],
    "关节": ["关节痛", "肿胀", "晨僵", "活动受限"],
}

OTHER_SYMPTOMS_POOL = [
    "夜间加重", "进食后明显", "伴有低热", "偶有乏力", "睡眠受影响", "食欲下降"
]

SYMPTOM_MEDICAL_MAP = {
    "肚子痛": "腹痛",
    "拉肚子": "腹泻",
    "胃痛": "胃部疼痛",
    "喉咙痒": "咽喉瘙痒",
    "嗳气": "嗳气",
    "反酸": "胃酸反流",
    "干咳": "干咳",
    "胸闷": "胸闷",
    "气短": "气促",
    "心悸": "心悸",
    "皮疹": "皮疹",
    "红肿": "红肿",
}

CONDITION_BY_BODY_PART = {
    "头部": ["偏头痛", "紧张性头痛", "鼻窦炎"],
    "咽喉": ["上呼吸道感染", "咽炎", "过敏性咽喉炎"],
    "胸部": ["上呼吸道感染", "急性支气管炎", "肺部感染"],
    "腹部": ["急性胃肠炎", "功能性消化不良", "急性胃炎"],
    "胃部": ["急性胃炎", "消化性溃疡", "反流性食管炎"],
    "皮肤": ["过敏性皮炎", "湿疹", "接触性皮炎"],
    "关节": ["骨关节炎", "关节炎", "肌肉劳损"],
}

DRUG_RECOMMENDATIONS = {
    "急性胃肠炎": [
        {"name": "蒙脱石散", "usage": "每次1袋，每日3次", "notes": "注意补液，孕妇慎用"},
        {"name": "口服补液盐", "usage": "按说明冲服", "notes": "防止脱水"},
    ],
    "急性胃炎": [
        {"name": "奥美拉唑", "usage": "每日1次，餐前服用", "notes": "遵医嘱使用"},
        {"name": "铝碳酸镁", "usage": "每次1-2片，每日3次", "notes": "避免与其他药同服"},
    ],
    "上呼吸道感染": [
        {"name": "对乙酰氨基酚", "usage": "按说明服用", "notes": "肝功能不全慎用"},
        {"name": "右美沙芬", "usage": "每次10-20mg，每日3次", "notes": "避免与含酒精药物同用"},
    ],
    "过敏性皮炎": [
        {"name": "氯雷他定", "usage": "每日1次", "notes": "嗜睡者慎用"},
        {"name": "炉甘石洗剂", "usage": "外用每日2-3次", "notes": "避免破损皮肤"},
    ],
}

# 统一 instruction 模板


# JSON Schemas for validation (lightweight)
SCHEMAS = {
    "preprocess": {
        "type": "object",
        "required": ["input", "output"],
        "properties": {
            "input": {"type": "object"},
            "output": {
                "type": "object",
                "required": ["optimized_symptoms", "rag_keywords"],
                "properties": {
                    "optimized_symptoms": {"type": "string"},
                    "rag_keywords": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    },
    "critic": {
        "type": "object",
        "required": ["input", "output"],
        "properties": {
            "output": {
                "type": "object",
                "required": ["score", "comment", "isValid"],
                "properties": {
                    "score": {"type": "number"},
                    "comment": {"type": "string"},
                    "isValid": {"type": "boolean"}
                }
            }
        }
    },
    "check_rag": {
        "type": "object",
        "required": ["input", "output"],
        "properties": {
            "output": {
                "type": "object",
                "required": ["ragScore", "ragComment"],
                "properties": {
                    "ragScore": {"type": "number"},
                    "ragComment": {"type": "string"}
                }
            }
        }
    },
    "drug_evidence": {
        "type": "object",
        "required": ["input", "output"],
        "properties": {
            "output": {
                "type": "object",
                "required": ["diagnosisScore", "diagnosisComment"],
                "properties": {
                    "diagnosisScore": {"type": "number"},
                    "diagnosisComment": {"type": "string"}
                }
            }
        }
    },
    "diagnosis": {
        "type": "object",
        "required": ["input", "output"],
        "properties": {
            "output": {
                "type": "object",
                "required": ["results", "recommendations", "recomm_short"],
                "properties": {
                    "results": {"type": "array"},
                    "recommendations": {"type": "array"},
                    "recomm_short": {"type": "array"}
                }
            }
        }
    },
    "drug": {
        "type": "object",
        "required": ["input", "output"],
        "properties": {
            "output": {"type": "object", "required": ["drugs"]}
        }
    }
}

INSTRUCTIONS = {
    "preprocess": "请将以下用户症状信息转换为结构化的医学描述，并提取RAG检索关键词。",
    "critic": "请对以下症状结构化结果进行质量评分。",
    "check_rag": "请评估RAG返回的医学知识与用户症状的匹配度。",
    "drug_evidence": "请对诊断结果与药物证据进行合理性评分。",
    "diagnosis": "根据患者症状和医学背景知识，生成诊断结果。",
    "drug": "根据诊断结果和药物知识库，生成用药建议。",
}

# 外部 Agent 名称 -> 内部生成器名称
AGENT_ALIASES = {
    # 新命名
    "symptom_normalizer": "preprocess",
    "symptom_quality_grader": "critic",
    "rag_relevance_grader": "check_rag",
    "drug_evidence_grader": "drug_evidence",
    "diagnosis_generator": "diagnosis",
    "drug_recommender": "drug",
    # 兼容旧命名
    "preprocess": "preprocess",
    "critic": "critic",
    "check_rag": "check_rag",
    "drug_evidence": "drug_evidence",
    "diagnosis": "diagnosis",
    "drug": "drug",
}


def validate_item(agent: str, item: Dict[str, Any]) -> bool:
    """Validate a generated item with a lightweight JSON schema."""
    schema = SCHEMAS.get(agent)
    if not schema:
        return True
    if validate is None:
        return True
    try:
        validate(instance=item, schema=schema)
        return True
    except ValidationError as exc:
        logger.warning(f"Schema validation failed for agent {agent}: {exc}")
        return False

# ==================== Prompt 模板 ====================

PROMPTS = {
    # Agent 1: 症状结构化 (preprocessAndGuess)
    "preprocess": {
        "system": """你是一个医学数据生成助手。你需要生成用于训练"症状结构化"模型的数据。

任务说明：
- 输入：用户的原始症状描述（包括身体部位、主要症状、其他症状、严重程度、持续时间）
- 输出：结构化的医学描述 (optimized_symptoms) 和 RAG 检索关键词 (rag_keywords)

生成要求：
1. optimized_symptoms 应该是专业、完整的医学症状描述，包含所有关键信息
2. rag_keywords 必须更具体：包含身体部位 + 症状 + 关键修饰（例如“腰部外伤疼痛”“腰椎间盘突出放射痛”）
3. 将口语化描述转换为专业术语（如"肚子痛"→"腹痛"）
4. 严重程度用文字描述（1=轻微, 2=较轻, 3=中等, 4=较重, 5=严重）

请生成多样化、真实的医疗场景数据。""",

        "user_template": """请生成 {batch_size} 条"症状结构化"训练数据。

每条数据格式如下：
{{
  "input": {{
    "body_part": "身体部位",
    "symptoms": ["症状1", "症状2"],
    "other_symptoms": "其他症状描述",
    "severity": 1-5,
    "duration": "持续时间代码"
  }},
  "output": {{
    "optimized_symptoms": "专业的症状描述文本",
    "rag_keywords": ["关键词1", "关键词2", ...]
  }}
}}

要求：
1. 生成多样化的症状组合，覆盖不同身体部位
2. 输入使用口语化描述，输出使用专业医学术语
3. rag_keywords 必须细化到症状层面，不允许只有“身体部位”这种泛化词
4. 确保 output 是合理的医学转换结果
4. 直接返回 JSON 数组，不要加任何解释文字

请返回一个包含 {batch_size} 条数据的 JSON 数组："""
    },

    # Agent 2: 质量评分 (Critic_preprocess)
    "critic": {
        "system": """你是一个医学数据生成助手。你需要生成用于训练"诊断质量评分"模型的数据。

任务说明：
- 输入：结构化的症状描述 (optimized_symptoms) 和关键词 (rag_keywords)
- 输出：质量评分 (score: 0-5) 和评价意见 (comment)

评分标准（每项1分，满分5分）：
1. optimized_symptoms 格式规范，是完整通顺的医学描述
2. rag_keywords 包含身体部位关键词
3. rag_keywords 包含主要症状关键词
4. 术语使用专业准确
5. 信息完整，无遗漏重要内容

请生成各种质量等级（好/中/差）的样本。""",

        "user_template": """请生成 {batch_size} 条"质量评分"训练数据。

每条数据格式如下：
{{
  "input": {{
    "optimized_symptoms": "症状描述",
    "rag_keywords": ["关键词1", "关键词2"]
  }},
  "output": {{
    "score": 0-5,
    "comment": "评价意见",
    "isValid": true/false
  }}
}}

要求：
1. 生成不同质量等级的样本（差:0-1分, 中:2-3分, 好:4-5分）
2. comment 要具体说明扣分原因或优点
3. score < 3 时 isValid 为 false
4. 直接返回 JSON 数组

请返回一个包含 {batch_size} 条数据的 JSON 数组："""
    },

    # Agent 3: RAG 评审 (checkRAG)
    "check_rag": {
        "system": """你是一个医学数据生成助手。你需要生成用于训练"RAG内容评审"模型的数据。

任务说明：
- 输入：用户症状 (optimized_symptoms) 和 RAG 检索结果 (rag_docs)
- 输出：相关性评分 (ragScore: 0-5) 和评价意见 (ragComment)

评分标准（0-5）：
0: 完全无关或明显矛盾
1: 基本无关，仅有泛化信息
2: 弱相关（部分关键词重合但缺少核心症状/部位）
3: 部分相关（覆盖部分核心症状，但遗漏关键线索）
4: 高度相关（覆盖核心症状并提供有价值背景）
5: 极高相关（高度匹配且包含关键诊断提示/鉴别要点）

请生成不同相关度的样本，并包含负样本。""",

        "user_template": """请生成 {batch_size} 条"RAG评审"训练数据。

每条数据格式如下：
{{
  "input": {{
    "optimized_symptoms": "患者症状描述",
    "rag_docs": [
      {{"doc_id": "doc_001", "score": 0.78, "snippet": "检索摘要片段1"}},
      {{"doc_id": "doc_002", "score": 0.42, "snippet": "检索摘要片段2"}}
    ]
  }},
  "output": {{
    "ragScore": 0-5,
    "ragComment": "评价意见"
  }}
}}

要求：
1. 生成不同相关度的样本（低:0-2, 中:3, 高:4-5）
2. rag_docs 要模拟真实的医学知识库检索结果
3. 包含负样本与边缘样本（相近但不匹配）
4. 直接返回 JSON 数组

请返回一个包含 {batch_size} 条数据的 JSON 数组："""
    },

    # Agent 4: 药物证据评审 (drugRAGandScore)
    "drug_evidence": {
        "system": """你是一个医学数据生成助手。你需要生成用于训练"用药证据评审"模型的数据。

任务说明：
- 输入：诊断结果 results（含疾病名与概率）+ 药物相关的 RAG 检索摘要 rag_docs
- 输出：诊断/用药合理性评分 diagnosisScore (0-5) 与简短意见 diagnosisComment

评分标准（0-5）：
0: 明显不合理（证据与诊断无关或相矛盾）
1: 基本无关，仅有泛化药物知识
2: 弱相关（部分药物/禁忌提到，但与诊断契合度低）
3: 部分相关（有一定支持，但缺乏关键证据）
4: 高度相关（药物/禁忌与诊断匹配，证据充分）
5: 极高相关（证据充分且包含关键安全/禁忌提示）

请生成不同相关度的样本，并包含负样本。""",

        "user_template": """请生成 {batch_size} 条"用药证据评审"训练数据。

每条数据格式如下：
{{
  "input": {{
    "results": [
      {{"condition": "疾病1", "probability": 0.xx, "description": "疾病描述"}},
      {{"condition": "疾病2", "probability": 0.yy, "description": "疾病描述"}}
    ],
    "rag_docs": [
      {{"doc_id": "drug_doc_001", "score": 0.72, "snippet": "药理/禁忌相关摘要1"}},
      {{"doc_id": "drug_doc_002", "score": 0.40, "snippet": "药理/禁忌相关摘要2"}}
    ]
  }},
  "output": {{
    "diagnosisScore": 0-5,
    "diagnosisComment": "评价意见"
  }}
}}

要求：
1. 生成不同相关度的样本（低:0-2, 中:3, 高:4-5）
2. rag_docs 要模拟真实药物知识库检索结果
3. 包含负样本与边缘样本（相近但不匹配）
4. 直接返回 JSON 数组

请返回一个包含 {batch_size} 条数据的 JSON 数组："""
    },

    # Agent 5: 诊断生成 (generateDiagnosis) - 核心任务
    "diagnosis": {
        "system": """你是一个医学数据生成助手。你需要生成用于训练"诊断生成"模型的数据。

任务说明：
- 输入：患者症状 (optimized_symptoms) 和医学背景 (ragContext)
- 输出：诊断结果（3个可能疾病及概率）、健康建议、简化建议

输出格式：
- results: 3个诊断结果，每个包含 condition(疾病名), probability(概率), description(描述)
- recommendations: 3条详细健康建议（每条>=15字）
- recomm_short: 10条简化建议（每条<=10字）

请确保诊断结果符合医学常识。""",

        "user_template": """请生成 {batch_size} 条"诊断生成"训练数据。

每条数据格式如下：
{{
  "input": {{
    "optimized_symptoms": "患者的详细症状描述",
    "ragContext": "相关的医学背景知识"
  }},
  "output": {{
    "results": [
      {{"condition": "疾病1", "probability": 0.xx, "description": "疾病描述"}},
      {{"condition": "疾病2", "probability": 0.yy, "description": "疾病描述"}},
      {{"condition": "疾病3", "probability": 0.zz, "description": "疾病描述"}}
    ],
    "recommendations": ["详细建议1(>=15字)", "详细建议2", "详细建议3"],
    "recomm_short": ["简化1", "简化2", "简化3", "简化4", "简化5", "简化6", "简化7", "简化8", "简化9", "简化10"]
  }}
}}

要求：
1. 诊断结果要符合医学常识，概率之和约为1
2. 涵盖常见病和一些特殊情况
3. 建议要具体可操作
4. 直接返回 JSON 数组
5. 必须输出严格合法 JSON（只允许双引号，不要注释、不要 Markdown、不要额外文字）
6. 禁止使用省略号/占位符（例如 "..." 或 "recommendations": [...]）
7. recommendations 必须正好 3 条，recomm_short 必须正好 10 条

请返回一个包含 {batch_size} 条数据的 JSON 数组："""
    },

    # Agent 5: 用药建议 (generateDrugRecommendations)
    "drug": {
        "system": """你是一个医学数据生成助手。你需要生成用于训练"用药建议"模型的数据。

任务说明：
- 输入：诊断结果 (condition) 和药物知识库内容 (drugRagContext)
- 输出：用药建议列表

输出格式：
每个药物包含：name(药名), usage(用法用量), notes(注意事项)

请确保用药建议符合医学规范。""",

        "user_template": """请生成 {batch_size} 条"用药建议"训练数据。

每条数据格式如下：
{{
  "input": {{
    "condition": "诊断的疾病名称",
    "drugRagContext": "药物知识库检索结果"
  }},
  "output": {{
    "drugs": [{{
      "condition": "疾病名称",
      "recommended_drugs": [
        {{"name": "药品名", "usage": "用法用量", "notes": "注意事项"}},
        {{"name": "药品名2", "usage": "用法用量", "notes": "注意事项"}}
      ]
    }}]
  }}
}}

要求：
1. 药物名称使用标准名
2. 用法用量要具体
3. 注意事项要包含禁忌症
4. 直接返回 JSON 数组
5. 必须输出严格合法 JSON（只允许双引号，不要注释、不要 Markdown、不要额外文字）
6. 禁止使用省略号/占位符（例如 "..." 或 "recommended_drugs": [...]）

请返回一个包含 {batch_size} 条数据的 JSON 数组："""
    }
}


# ==================== 数据生成类 ====================

class SFTDataGenerator:
    def __init__(
        self,
        api_key: str,
        base_url: str = None,
        model: str = "gpt-4.1",
        input_price_per_million: float = 0.0,
        output_price_per_million: float = 0.0
    ):
        """
        初始化数据生成器

        Args:
            api_key: OpenAI API Key
            base_url: API Base URL (可选，用于代理)
            model: 使用的模型名称
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.total_tokens = 0
        self.total_cost = 0.0

        # 价格（per 1M tokens），可通过命令行传入
        self.input_price = float(input_price_per_million) / 1_000_000
        self.output_price = float(output_price_per_million) / 1_000_000

    def generate_batch(self, agent: str, batch_size: int = 10, max_retries: int = 2) -> List[Dict]:
        """
        生成一批数据

        Args:
            agent: Agent 类型
            batch_size: 每批生成数量

        Returns:
            生成的数据列表
        """
        if agent not in PROMPTS:
            raise ValueError(f"Unknown agent: {agent}")

        prompt_config = PROMPTS[agent]

        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": prompt_config["system"]},
                        {"role": "user", "content": prompt_config["user_template"].format(batch_size=batch_size)}
                    ],
                    temperature=0.8,
                    max_tokens=4000,
                )
                # 统计 token 使用
                usage = response.usage
                input_tokens = usage.prompt_tokens
                output_tokens = usage.completion_tokens
                self.total_tokens += input_tokens + output_tokens

                # 计算成本
                cost = input_tokens * self.input_price + output_tokens * self.output_price
                self.total_cost += cost

                # 解析返回的 JSON
                content = response.choices[0].message.content.strip()

                # 尝试提取 JSON 数组
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]

                data = json.loads(content)
                data_list = data if isinstance(data, list) else [data]
                filtered = [d for d in data_list if validate_item(agent, d)]
                if filtered:
                    return filtered
                logger.warning("Schema validation produced empty batch, retrying...")
            except json.JSONDecodeError as e:
                logger.warning(f"JSON 解析失败 (attempt {attempt + 1}): {e}")
                logger.debug(f"原始内容: {content[:500]}...")
            except Exception as e:
                logger.error(f"API 调用失败 (attempt {attempt + 1}): {e}")

            if attempt < max_retries:
                time.sleep(0.5)
                continue
            return []

    def generate_dataset(
        self,
        agent: str,
        num_samples: int,
        batch_size: int = 10,
        output_file: str = None,
        output_format: str = "instruction"
    ) -> List[Dict]:
        """
        生成完整数据集

        Args:
            agent: Agent 类型
            num_samples: 总样本数
            batch_size: 每批大小
            output_file: 输出文件路径

        Returns:
            所有生成的数据
        """
        all_data = []
        num_batches = (num_samples + batch_size - 1) // batch_size

        logger.info(f"开始生成 {agent} 数据集: {num_samples} 条，分 {num_batches} 批")

        for i in tqdm(range(num_batches), desc=f"Generating {agent}"):
            current_batch_size = min(batch_size, num_samples - len(all_data))

            batch_data = self.generate_batch(agent, current_batch_size)
            all_data.extend(batch_data)

            # 避免 rate limit
            if i < num_batches - 1:
                time.sleep(0.5)

        logger.info(f"生成完成: {len(all_data)} 条数据")
        logger.info(f"总 Token: {self.total_tokens:,}")
        logger.info(f"预估成本: ${self.total_cost:.4f}")

        # 转换为训练格式并保存
        if output_file:
            training_data = self.convert_to_training_format(all_data, agent, output_format=output_format)
            self.save_jsonl(training_data, output_file)
            logger.info(f"已保存到: {output_file}")

        return all_data

    def convert_to_training_format(self, data: List[Dict], agent: str, output_format: str = "instruction") -> List[Dict]:
        """
        转换为 SFT 训练格式

        Args:
            data: 原始数据
            agent: Agent 类型

        Returns:
            训练格式数据
        """
        if output_format == "conversations":
            output_format = "conversation"
        if output_format not in {"instruction", "conversation"}:
            raise ValueError(f"Unknown output_format: {output_format}")

        training_data = []

        for item in data:
            if "input" not in item or "output" not in item:
                continue

            if output_format == "conversation":
                human_content = self._build_human_prompt(item["input"], agent)
                gpt_content = json.dumps(item["output"], ensure_ascii=False)
                training_item = {
                    "conversations": [
                        {"from": "human", "value": human_content},
                        {"from": "gpt", "value": gpt_content}
                    ]
                }
            else:
                training_item = {
                    "instruction": INSTRUCTIONS.get(agent, ""),
                    "input": item["input"],
                    "output": item["output"],
                }
            training_data.append(training_item)

        return training_data

    def _build_human_prompt(self, input_data: Dict, agent: str) -> str:
        """根据 agent 类型构建用户输入"""
        if agent == "preprocess":
            return f"""请将以下症状信息转换为结构化的医学描述：
身体部位: {input_data.get('body_part', '')}
主要症状: {', '.join(input_data.get('symptoms', []))}
其他症状: {input_data.get('other_symptoms', '')}
严重程度: {input_data.get('severity', 3)}
持续时间: {input_data.get('duration', '')}

请输出 JSON 格式：{{"optimized_symptoms": "...", "rag_keywords": [...]}}"""

        elif agent == "critic":
            return f"""请对以下症状结构化结果进行评分：
{json.dumps(input_data, ensure_ascii=False, indent=2)}

请输出 JSON 格式：{{"score": 0-5, "comment": "...", "isValid": true/false}}"""

        elif agent == "check_rag":
            return f"""请评估 RAG 返回内容与症状的相关性：
【症状】{input_data.get('optimized_symptoms', '')}
【RAG检索摘要】{json.dumps(input_data.get('rag_docs', []), ensure_ascii=False)}

请输出 JSON 格式：{{"ragScore": 0-5, "ragComment": "..."}}"""

        elif agent == "diagnosis":
            return f"""请根据以下信息生成诊断结果：
【症状】{input_data.get('optimized_symptoms', '')}
【医学背景】{input_data.get('ragContext', '')}

请输出诊断 JSON。"""

        elif agent == "drug":
            return f"""请为以下疾病生成用药建议：
【诊断】{input_data.get('condition', '')}
【药物知识】{input_data.get('drugRagContext', '')}

请输出用药建议 JSON。"""

        elif agent == "drug_evidence":
            return f"""请评估诊断与药物证据的相关性：
【诊断结果】{json.dumps(input_data.get('results', []), ensure_ascii=False)}
【RAG检索摘要】{json.dumps(input_data.get('rag_docs', []), ensure_ascii=False)}

请输出 JSON 格式：{{"diagnosisScore": 0-5, "diagnosisComment": "..."}}"""

        return json.dumps(input_data, ensure_ascii=False)

    @staticmethod
    def save_jsonl(data: List[Dict], filepath: str):
        """保存为 JSONL 格式"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')


def _medicalize(symptom: str) -> str:
    return SYMPTOM_MEDICAL_MAP.get(symptom, symptom)


def _severity_text(severity: int) -> str:
    return ["轻微", "较轻", "中等", "较重", "严重"][max(0, min(4, severity - 1))]


def _pick_body_part(rng: random.Random) -> str:
    return rng.choice(list(SYMPTOMS_BY_BODY_PART.keys()))


def generate_seed_samples(agent: str, num_samples: int, seed: int = 42) -> List[Dict]:
    rng = random.Random(seed + hash(agent) % 1000)
    samples: List[Dict[str, Any]] = []

    for _ in range(num_samples):
        body_part = _pick_body_part(rng)
        symptoms = rng.sample(SYMPTOMS_BY_BODY_PART[body_part], k=2)
        other_symptoms = rng.choice(OTHER_SYMPTOMS_POOL)
        severity = rng.choice(SEVERITY_LEVELS)
        duration = rng.choice(DURATION_OPTIONS)
        duration_text = DURATION_CHINESE.get(duration, duration)

        if agent == "preprocess":
            medical_symptoms = [_medicalize(s) for s in symptoms]
            optimized_symptoms = (
                f"患者主诉{body_part}出现{ '、'.join(medical_symptoms) }，"
                f"伴有{other_symptoms}，症状程度{_severity_text(severity)}，持续{duration_text}。"
            )
            rag_keywords = [f"{body_part}{s}" for s in medical_symptoms]
            rag_keywords.append(f"{body_part}{other_symptoms}")
            rag_keywords.extend([_severity_text(severity), duration_text])
            samples.append({
                "input": {
                    "body_part": body_part,
                    "symptoms": symptoms,
                    "other_symptoms": other_symptoms,
                    "severity": severity,
                    "duration": duration,
                },
                "output": {
                    "optimized_symptoms": optimized_symptoms,
                    "rag_keywords": rag_keywords,
                }
            })

        elif agent == "critic":
            medical_symptoms = [_medicalize(s) for s in symptoms]
            optimized_symptoms = (
                f"患者{body_part}出现{ '、'.join(medical_symptoms) }，"
                f"程度{_severity_text(severity)}，持续{duration_text}。"
            )
            rag_keywords = [body_part] + medical_symptoms
            quality = rng.choice(["good", "medium", "bad"])
            if quality == "bad":
                optimized_symptoms = "肚子痛，感觉不舒服"
                rag_keywords = ["不舒服"]
                score = 1
            elif quality == "medium":
                rag_keywords = medical_symptoms
                score = 3
            else:
                score = 5
            samples.append({
                "input": {
                    "optimized_symptoms": optimized_symptoms,
                    "rag_keywords": rag_keywords,
                },
                "output": {
                    "score": score,
                    "comment": "结构化质量评估结果。",
                    "isValid": score >= 3,
                }
            })

        elif agent == "check_rag":
            optimized_symptoms = f"患者{body_part}出现{_medicalize(symptoms[0])}，伴{other_symptoms}"
            r = rng.random()
            if r < 0.15:
                rag_docs = [
                    {"doc_id": "doc_009", "score": 0.18, "snippet": "皮肤过敏常见表现为皮疹、瘙痒，与当前症状无关。"}
                ]
                rag_score = 0
                rag_comment = "内容与症状无关。"
            elif r < 0.3:
                rag_docs = [
                    {"doc_id": "doc_012", "score": 0.24, "snippet": "一般性健康科普内容，与当前症状关联很弱。"}
                ]
                rag_score = 1
                rag_comment = "几乎无关，仅有泛化信息。"
            elif r < 0.5:
                rag_docs = [
                    {"doc_id": "doc_015", "score": 0.30, "snippet": f"{body_part}不适可能与疲劳相关，但缺少具体症状描述。"}
                ]
                rag_score = 2
                rag_comment = "相关性较弱，缺少核心症状。"
            elif r < 0.7:
                rag_docs = [
                    {"doc_id": "doc_021", "score": 0.52, "snippet": f"{body_part}相关疾病可能包括{CONDITION_BY_BODY_PART[body_part][1]}，但与主要症状匹配不完整。"}
                ]
                rag_score = 3
                rag_comment = "部分相关，但缺少关键线索。"
            elif r < 0.9:
                rag_docs = [
                    {"doc_id": "doc_001", "score": 0.78, "snippet": f"{body_part}相关疾病可能包括{CONDITION_BY_BODY_PART[body_part][0]}，常见表现为{_medicalize(symptoms[0])}等。"}
                ]
                rag_score = 4
                rag_comment = "RAG内容与症状相关，具有参考价值。"
            else:
                rag_docs = [
                    {"doc_id": "doc_002", "score": 0.90, "snippet": f"{body_part}{_medicalize(symptoms[0])}是{CONDITION_BY_BODY_PART[body_part][0]}的典型表现，并需与{CONDITION_BY_BODY_PART[body_part][2]}鉴别。"}
                ]
                rag_score = 5
                rag_comment = "高度相关，且包含关键鉴别要点。"
            samples.append({
                "input": {
                    "optimized_symptoms": optimized_symptoms,
                    "rag_docs": rag_docs,
                },
                "output": {
                    "ragScore": rag_score,
                    "ragComment": rag_comment,
                }
            })

        elif agent == "diagnosis":
            optimized_symptoms = f"患者{body_part}出现{_medicalize(symptoms[0])}，伴{other_symptoms}，持续{duration_text}。"
            rag_context = f"{body_part}相关常见疾病包括{', '.join(CONDITION_BY_BODY_PART[body_part])}。"
            conditions = CONDITION_BY_BODY_PART[body_part]
            samples.append({
                "input": {
                    "optimized_symptoms": optimized_symptoms,
                    "ragContext": rag_context,
                },
                "output": {
                    "results": [
                        {"condition": conditions[0], "probability": 0.6, "description": "与症状匹配度较高的常见疾病。"},
                        {"condition": conditions[1], "probability": 0.25, "description": "可能性中等，需要结合进一步检查。"},
                        {"condition": conditions[2], "probability": 0.15, "description": "存在一定可能，需鉴别诊断。"},
                    ],
                    "recommendations": [
                        "建议保持清淡饮食，避免辛辣刺激食物。",
                        "注意休息并观察症状变化，如加重及时就医。",
                        "如症状持续超过一周建议到正规医院检查。",
                    ],
                    "recomm_short": ["清淡饮食", "注意休息", "及时就医", "观察变化", "避免刺激", "保持水分", "规律作息", "适度活动", "按时复诊", "遵医嘱"],
                }
            })

        elif agent == "drug_evidence":
            conditions = CONDITION_BY_BODY_PART[body_part]
            results = [
                {"condition": conditions[0], "probability": 0.6, "description": "与症状匹配度较高的常见疾病。"},
                {"condition": conditions[1], "probability": 0.3, "description": "可能性中等，需要结合进一步检查。"},
            ]
            r = rng.random()
            if r < 0.15:
                rag_docs = [
                    {"doc_id": "drug_doc_008", "score": 0.18, "snippet": "皮肤外用药物的注意事项，与当前诊断无关。"},
                ]
                diagnosis_score = 0
                diagnosis_comment = "证据与诊断无关。"
            elif r < 0.3:
                rag_docs = [
                    {"doc_id": "drug_doc_009", "score": 0.25, "snippet": "一般性用药安全说明，与当前诊断联系很弱。"},
                ]
                diagnosis_score = 1
                diagnosis_comment = "几乎无关，仅有泛化药物信息。"
            elif r < 0.5:
                rag_docs = [
                    {"doc_id": "drug_doc_010", "score": 0.32, "snippet": "对症药的常见不良反应概述，但未提及具体疾病。"},
                ]
                diagnosis_score = 2
                diagnosis_comment = "相关性弱，缺少关键用药信息。"
            elif r < 0.7:
                rag_docs = [
                    {"doc_id": "drug_doc_013", "score": 0.55, "snippet": f"{conditions[1]}可能使用的药物提要，但缺乏禁忌或适应证细节。"},
                ]
                diagnosis_score = 3
                diagnosis_comment = "部分相关，但证据不充分。"
            elif r < 0.9:
                rag_docs = [
                    {"doc_id": "drug_doc_001", "score": 0.76, "snippet": f"{conditions[0]}的常用治疗药物包括对症药和基础支持治疗。"},
                ]
                diagnosis_score = 4
                diagnosis_comment = "证据与诊断结果相关，合理。"
            else:
                rag_docs = [
                    {"doc_id": "drug_doc_002", "score": 0.88, "snippet": f"{conditions[0]}的一线用药建议及禁忌提示，适用于当前诊断。"},
                ]
                diagnosis_score = 5
                diagnosis_comment = "高度相关，包含关键安全信息。"
            samples.append({
                "input": {
                    "results": results,
                    "rag_docs": rag_docs,
                },
                "output": {
                    "diagnosisScore": diagnosis_score,
                    "diagnosisComment": diagnosis_comment,
                }
            })

        elif agent == "drug":
            condition = rng.choice(CONDITION_BY_BODY_PART[body_part])
            drug_list = DRUG_RECOMMENDATIONS.get(condition, [
                {"name": "请咨询医生", "usage": "根据具体情况用药", "notes": "需专业医生指导"}
            ])
            rag_context = f"{condition}常用药物包括：{', '.join([d['name'] for d in drug_list])}。"
            samples.append({
                "input": {
                    "condition": condition,
                    "drugRagContext": rag_context,
                },
                "output": {
                    "drugs": [{
                        "condition": condition,
                        "recommended_drugs": drug_list,
                    }]
                }
            })

    return samples


# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(description="SFT 数据生成脚本")
    parser.add_argument("--agent", type=str, required=True,
                        choices=[
                            "symptom_normalizer", "symptom_quality_grader", "rag_relevance_grader",
                            "drug_evidence_grader",
                            "preprocess", "critic", "check_rag", "drug_evidence",
                            "diagnosis_generator", "drug_recommender",
                            "diagnosis", "drug",
                            "all"
                        ],
                        help="要生成数据的 Agent 类型")
    parser.add_argument("--num_samples", type=int, default=100,
                        help="生成样本数量")
    parser.add_argument("--batch_size", type=int, default=10,
                        help="每批生成数量")
    parser.add_argument("--api_key", type=str, default=None,
                        help="OpenAI API Key (也可通过环境变量 OPENAI_API_KEY 设置)")
    parser.add_argument("--base_url", type=str, default=None,
                        help="API Base URL (可选)")
    parser.add_argument("--model", type=str, default="gpt-4.1",
                        help="使用的模型（默认 gpt-4.1，避免 gpt-4o）")
    parser.add_argument("--price_in", type=float, default=0.0,
                        help="输入token价格（每1M tokens），用于成本估算")
    parser.add_argument("--price_out", type=float, default=0.0,
                        help="输出token价格（每1M tokens），用于成本估算")
    parser.add_argument("--output_dir", type=str, default="./",
                        help="输出目录")
    parser.add_argument("--resume", action="store_true",
                        help="如果输出文件已存在，则继续追加生成")
    parser.add_argument("--test_cost", action="store_true",
                        help="测试模式，只打印预估成本")
    parser.add_argument("--seed_mode", action="store_true",
                        help="启用本地 seed 数据生成（不调用 API）")
    parser.add_argument("--synthetic_mode", action="store_true",
                        help="启用 API 合成数据生成")
    parser.add_argument("--seed", type=int, default=42,
                        help="seed 模式随机种子")
    parser.add_argument("--output_format", type=str, default="instruction",
                        choices=["instruction", "conversation"],
                        help="输出格式：instruction 或 conversation")

    args = parser.parse_args()

    if not args.seed_mode and not args.synthetic_mode:
        args.synthetic_mode = True

    generator = None
    if args.synthetic_mode:
        api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("请提供 OpenAI API Key (--api_key 或环境变量 OPENAI_API_KEY)")
            return
        generator = SFTDataGenerator(
            api_key=api_key,
            base_url=args.base_url,
            model=args.model,
            input_price_per_million=args.price_in,
            output_price_per_million=args.price_out
        )

    # 确定要生成的 Agent 列表
    if args.agent == "all":
        agents = ["symptom_quality_grader", "rag_relevance_grader", "drug_evidence_grader"]
    else:
        agents = [args.agent]

    # 生成数据
    for agent in agents:
        resolved_agent = AGENT_ALIASES.get(agent)
        if not resolved_agent:
            logger.error(f"Unknown agent: {agent}")
            continue
        output_file = os.path.join(args.output_dir, f"{agent}_sft_data.jsonl")
        seed_output_file = os.path.join(args.output_dir, f"{agent}_seed.jsonl")

        logger.info(f"\n{'='*50}")
        logger.info(f"生成 {agent} 数据集")
        logger.info(f"{'='*50}")

        if args.seed_mode:
            seed_data = generate_seed_samples(resolved_agent, args.num_samples, seed=args.seed)
            seed_training = []
            if generator:
                seed_training = generator.convert_to_training_format(seed_data, resolved_agent, output_format=args.output_format)
            else:
                temp_gen = SFTDataGenerator(api_key="seed-only", base_url=args.base_url, model=args.model)
                seed_training = temp_gen.convert_to_training_format(seed_data, resolved_agent, output_format=args.output_format)
            if args.resume and os.path.exists(seed_output_file):
                with open(seed_output_file, 'a', encoding='utf-8') as f:
                    for item in seed_training:
                        f.write(json.dumps(item, ensure_ascii=False) + '\n')
            else:
                SFTDataGenerator.save_jsonl(seed_training, seed_output_file)
            logger.info(f"Seed 数据已保存到: {seed_output_file}")

        data = []
        if args.synthetic_mode and generator:
            if args.resume and os.path.exists(output_file):
                # 估算已存在样本数
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_count = sum(1 for _ in f)
                remaining = max(args.num_samples - existing_count, 0)
                if remaining == 0:
                    logger.info(f"{output_file} 已存在 {existing_count} 条，跳过生成")
                else:
                    logger.info(f"{output_file} 已存在 {existing_count} 条，继续生成 {remaining} 条")
                    data = generator.generate_dataset(
                        agent=resolved_agent,
                        num_samples=remaining,
                        batch_size=args.batch_size,
                        output_file=None,
                        output_format=args.output_format
                    )
                    if data:
                        training_data = generator.convert_to_training_format(
                            data, resolved_agent, output_format=args.output_format
                        )
                        with open(output_file, 'a', encoding='utf-8') as f:
                            for item in training_data:
                                f.write(json.dumps(item, ensure_ascii=False) + '\n')
            else:
                data = generator.generate_dataset(
                    agent=resolved_agent,
                    num_samples=args.num_samples,
                    batch_size=args.batch_size,
                    output_file=output_file,
                    output_format=args.output_format
                )

        if args.test_cost and generator:
            logger.info(f"\n📊 成本估算:")
            logger.info(f"   - 总 Token: {generator.total_tokens:,}")
            logger.info(f"   - 预估成本: ${generator.total_cost:.4f}")
            logger.info(f"   - 每条成本: ${generator.total_cost/max(len(data),1):.6f}")

            # 推算 5000 条的成本
            estimated_5k = (5000 / max(args.num_samples, 1)) * generator.total_cost
            logger.info(f"   - 5000条预估: ${estimated_5k:.2f}")


if __name__ == "__main__":
    main()
