# LoRA Rank Ablation Results

> Note (2026-02-17): 当前表格来自旧版 notebook 的一次异常评估，不可用于 rank 优劣判断。旧版存在两个问题：`max_new_tokens=300` 导致 Qwen3 `<think>...</think>` 挤占输出并截断 JSON；训练显存在父进程统计，导致 `Train VRAM(GB)=0.0`。请用已修复的 `notebooks/ablation_lora_rank.ipynb` 重跑后再更新本表。

## 实验配置
- Agent: diagnosis_generator (Qwen3-1.7B)
- Data: ~800 SFT samples
- Epochs: 2, LR: 1e-4, Batch: 2×8=16
- Alpha = Rank × 2 (固定比值 2.0)
- 测试样本: 20 条

## 结果对比

| Rank | Alpha | Final Loss | JSON Valid | Results≥3 | Prob≈1.0 | Tok/s | Train VRAM(GB) |
|------|-------|-----------|-----------|----------|---------|-------|---------------|
| 64 | 128 | 0.8062 | 0% | 0% | 0% | 23.6 | 0.0 |
