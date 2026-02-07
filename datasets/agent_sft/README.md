# Agent SFT 数据集目录
本目录用于存放不同 Agent 的 SFT 数据集，按 Agent 独立文件夹归档，避免混用。

建议结构：
- `datasets/agent_sft/symptom_normalizer/`
- `datasets/agent_sft/symptom_quality_grader/`
- `datasets/agent_sft/rag_relevance_grader/`
- `datasets/agent_sft/drug_evidence_grader/`

**说明：**
- `diagnosis_generator` 走 **DAPT/QA 数据**（来自 `train_sft.jsonl`），不再用 LLM 合成结构化 SFT。
- `drug_recommender` 不做 SFT，仅走 RAG + 规则/Schema 约束。

命名建议：
- `train.jsonl`
- `val.jsonl`
- `test.jsonl`
