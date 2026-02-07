# IntelHealth Agent SFT 数据生成与训练指南

## 1. 快速开始

### 1.1 安装依赖
```bash
pip install openai tqdm loguru
```

### 1.2 生成测试数据（100条，查看成本）
```bash
# 设置 API Key
export OPENAI_API_KEY="your-api-key"

# 生成 100 条 preprocess 数据，测试成本
python generate_sft_data.py --agent preprocess --num_samples 100 --test_cost
```

### 1.2.1 仅生成本地 seed 数据（不调用 API）
```bash
# 生成 100 条 seed 数据（不消耗 API）
python generate_sft_data.py --agent preprocess --num_samples 100 --seed_mode
```

### 1.3 生成完整数据集
```bash
# 为 preprocess Agent 生成 5000 条数据
python generate_sft_data.py --agent preprocess --num_samples 5000

# 为所有 Agent 生成数据
python generate_sft_data.py --agent all --num_samples 2000
```

### 1.4 同时生成 seed + 合成数据
```bash
python generate_sft_data.py --agent all --num_samples 2000 --seed_mode --synthetic_mode
```

输出文件：
- 合成数据：`{agent}_sft_data.jsonl`
- Seed 数据：`{agent}_seed.jsonl`

---

## 2. SFT vs 增量预训练 vs LoRA 详解

### 2.1 三种训练方式对比

| 方式 | 全称 | 训练内容 | 数据格式 | 适用场景 |
|------|------|---------|---------|---------|
| **SFT** | Supervised Fine-Tuning | 学习"如何回答" | 对话格式 (instruction-response) | 特定任务指令遵循 |
| **增量预训练** | Continual Pre-training | 学习"领域知识" | 纯文本 (无格式要求) | 领域知识注入 |
| **LoRA** | Low-Rank Adaptation | 参数高效微调 | 同上两种 | 资源有限时的任何训练 |

### 2.2 什么时候用什么？

```
┌─────────────────────────────────────────────────────────────────┐
│                        训练策略决策树                            │
└─────────────────────────────────────────────────────────────────┘

你的目标是什么？
    │
    ├─► 让模型学会"做某个任务"（如：生成JSON格式诊断）
    │       └─► 用 SFT（有监督微调）
    │
    ├─► 让模型"理解某个领域"（如：医学知识）
    │       └─► 用 增量预训练（Continual Pre-training）
    │
    └─► 两者都需要
            └─► 先增量预训练，再 SFT

你的资源情况？
    │
    ├─► GPU 显存 < 16GB
    │       └─► 必须用 LoRA
    │
    ├─► GPU 显存 16-48GB
    │       └─► 小模型(0.5B-3B) 可全量，大模型用 LoRA
    │
    └─► GPU 显存 > 48GB (A100等)
            └─► 可以考虑全量微调
```

### 2.3 对于 IntelHealth 各 Agent 的建议

| Agent | 推荐训练方式 | 理由 |
|-------|-------------|------|
| `preprocess` | **SFT + LoRA** | 任务明确（结构化转换），需要学会特定输出格式 |
| `critic` | **SFT + LoRA** | 评分任务，需要学会打分逻辑 |
| `check_rag` | **SFT + LoRA** | 相关性判断，任务导向 |
| `diagnosis` | **增量预训练 + SFT + LoRA** | 核心任务，需要医学知识 + 诊断能力 |
| `drug` | **增量预训练 + SFT + LoRA** | 需要药物知识 + 推荐能力 |

---

## 3. 具体训练流程

### 3.1 简单任务（preprocess, critic, check_rag）

**只需要 SFT：**

```bash
# 1. 生成数据
python generate_sft_data.py --agent preprocess --num_samples 5000

# 2. 训练（在 MyMedicalGPT 目录下）
cd ../../MyMedicalGPT

python supervised_finetuning.py \
    --model_name_or_path Qwen/Qwen2.5-0.5B-Instruct \
    --train_file_dir ../IntelHealth/data_clean/sft/ \
    --output_dir outputs/loras/preprocess-agent \
    --per_device_train_batch_size 4 \
    --gradient_accumulation_steps 4 \
    --num_train_epochs 3 \
    --learning_rate 2e-4 \
    --use_lora True \
    --lora_rank 64 \
    --lora_alpha 128
```

### 3.2 复杂任务（diagnosis, drug）

**需要先增量预训练，再 SFT：**

```bash
# 步骤 1: 增量预训练（学习医学知识）
python pretraining.py \
    --model_name_or_path Qwen/Qwen2.5-0.5B-Instruct \
    --train_file_dir data/medical_corpus/ \
    --output_dir outputs/pretrained/medical-qwen \
    --per_device_train_batch_size 4 \
    --num_train_epochs 1 \
    --use_lora True

# 步骤 2: 合并 LoRA
python merge_peft_adapter.py \
    --base_model Qwen/Qwen2.5-0.5B-Instruct \
    --lora_model outputs/pretrained/medical-qwen \
    --output_dir outputs/merged/medical-qwen-pretrained

# 步骤 3: SFT（学习诊断任务）
python supervised_finetuning.py \
    --model_name_or_path outputs/merged/medical-qwen-pretrained \
    --train_file_dir ../IntelHealth/data_clean/sft/ \
    --output_dir outputs/loras/diagnosis-agent \
    --use_lora True
```

---

## 4. LoRA 详解

### 4.1 什么是 LoRA？

LoRA (Low-Rank Adaptation) 是一种**参数高效微调**方法：

```
┌──────────────────────────────────────────────────────────┐
│                    原始模型权重 W                         │
│                    (冻结，不更新)                         │
│                         │                                │
│                         ▼                                │
│              ┌─────────────────────┐                     │
│              │    W + ΔW           │                     │
│              │                     │                     │
│              │  ΔW = A × B         │  ◄── 只训练 A 和 B   │
│              │  (低秩分解)          │      参数量很小      │
│              └─────────────────────┘                     │
└──────────────────────────────────────────────────────────┘

全量微调: 更新所有参数 (数十亿)
LoRA:     只更新 A、B 矩阵 (数百万，约 1-5%)
```

### 4.2 LoRA 参数说明

```python
# 在 supervised_finetuning.py 中的参数
--use_lora True              # 启用 LoRA
--lora_rank 64               # 秩 (越大能力越强，显存越多)
--lora_alpha 128             # 缩放因子 (通常是 rank 的 2 倍)
--lora_dropout 0.05          # Dropout
--lora_target_modules q_proj,k_proj,v_proj,o_proj  # 要适配的层
```

### 4.3 LoRA 显存对比

| 模型大小 | 全量微调 | LoRA (rank=64) |
|---------|---------|----------------|
| 0.5B | ~8GB | ~4GB |
| 1.8B | ~16GB | ~8GB |
| 7B | ~60GB | ~16GB |
| 14B | ~120GB | ~24GB |

---

## 5. 增量预训练 vs SFT 数据格式

### 5.1 增量预训练数据格式

**纯文本，无特定格式：**

```text
急性胃炎是指由多种原因引起的急性胃黏膜炎症。临床上常见的病因包括药物、应激、
乙醇、缺血、胆汁反流等。主要表现为上腹部不适、疼痛、恶心、呕吐等症状...
```

### 5.2 SFT 输出格式说明

默认输出为 `instruction` 格式（更适合统一数据集）：
```jsonl
{"instruction":"...","input":{...},"output":{...}}
```

如需旧版对话格式：
```bash
python generate_sft_data.py --agent preprocess --num_samples 100 --output_format conversation
```

**文件格式**: `.txt` 或每行一个文档的 `.jsonl`

```jsonl
{"text": "急性胃炎是指由多种原因引起的急性胃黏膜炎症..."}
{"text": "慢性支气管炎是气管、支气管黏膜及周围组织的慢性非特异性炎症..."}
```

### 5.2 SFT 数据格式

**对话格式（你已有的格式）：**

```jsonl
{"conversations": [{"from": "human", "value": "问题"}, {"from": "gpt", "value": "回答"}]}
```

---

## 6. 各 Agent 数据量建议

| Agent | 最小量 | 推荐量 | 说明 |
|-------|-------|-------|------|
| preprocess | 1,000 | 5,000 | 结构化转换任务 |
| critic | 500 | 2,000 | 评分任务，需覆盖各分数段 |
| check_rag | 500 | 2,000 | 相关性判断 |
| diagnosis | 3,000 | 10,000+ | 核心任务，需要更多数据 |
| drug | 2,000 | 5,000 | 用药建议 |

---

## 7. 训练后测试

训练完成后，可以用以下方式测试：

```python
# 测试 preprocess agent
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("outputs/merged/preprocess-agent")
tokenizer = AutoTokenizer.from_pretrained("outputs/merged/preprocess-agent")

prompt = """请将以下症状信息转换为结构化的医学描述：
身体部位: 头部
主要症状: 头痛, 头晕
其他症状: 恶心想吐
严重程度: 3
持续时间: 1To3Days

请输出 JSON 格式："""

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0]))
```

---

## 8. 常见问题

### Q: 增量预训练也用 LoRA 吗？
**A:** 可以。增量预训练的目的是注入知识，LoRA 同样适用。如果资源有限，建议用 LoRA。

### Q: 为什么 diagnosis 需要增量预训练？
**A:** 因为诊断需要医学背景知识。基础模型（如 Qwen）的医学知识有限，增量预训练可以补充这部分知识。

### Q: 多个 Agent 可以共享同一个基础模型吗？
**A:** 可以。建议先用医学语料增量预训练一个基础模型，然后为每个 Agent 单独做 SFT。

### Q: 生成的数据质量不高怎么办？
**A:**
1. 增加 few-shot 示例
2. 人工审核和清洗
3. 使用更强的模型生成（如 GPT-4）

## ����: build_agent_dataset.py
- ������������ seed ���ݣ�֧�� output_format=conversations
- ʾ��:
  python build_agent_dataset.py --agent preprocess --num_samples 500 --output_format conversations
