# LoRA Rank Training Tradeoff Report

- Metric scope: training-only (no inference-format metrics).
- Recommended rank: **64**
- Balance weights: loss=0.5, vram=0.5

## Core Metrics by Rank

| Rank | Alpha | Final Loss | Best Loss | Peak VRAM(GB) | Runtime(min) | Samples/s | Balance Score | Pareto |
|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 64 | 128 | 0.8062 | 0.7600 | 5.81 | 14.11 | 3.473 | 0.3880 | Y |
| 32 | 64 | 0.8858 | 0.8359 | 5.25 | 13.97 | 3.509 | 0.3900 | Y |
| 16 | 32 | 0.9467 | 0.8945 | 4.99 | 14.01 | 3.498 | 0.4343 | Y |
| 8 | 16 | 1.0012 | 0.9481 | 4.86 | 14.17 | 3.458 | 0.5000 | Y |
| 128 | 256 | 0.7251 | 0.6871 | 6.83 | 13.18 | 3.719 | 0.5000 | Y |

## 人话结论

- 128 的 loss 最好，但显存和模型体积成本明显更高。
- 64 的 loss 已经明显优于 8/16/32，同时显存压力比 128 小得多。
- 从工程角度看，64 是效果和成本的平衡点，适合作为默认 rank。

## 64 vs 128 Tradeoff（关键数字）

- Final Loss: 64 = 0.8062, 128 = 0.7251（128 更低，差值 0.0811）
- Peak VRAM: 64 = 5.81 GB, 128 = 6.83 GB（128 多 1.02 GB，约 +17.6%）
- Adapter Size: 64 = 266.1 MB, 128 = 532.1 MB（128 约 2 倍）
- Train Runtime: 64 = 14.11 min, 128 = 13.18 min（128 快约 0.93 min）

结论：128 提升了 loss，但资源成本上涨明显；如果目标是线上可用且成本可控，优先选 64。

## 本次 Ablation 的问题点（复盘）

1. 早期用 `json_valid` / `results>=3` 这类格式指标时，容易被解析噪声影响（如 `<think>`、提取 JSON 失败、尾部闭合问题），出现“模型可用但指标很差”的假阴性。
2. 这版报告改为只看训练硬指标（loss/VRAM/runtime/throughput），避免把解析器问题误判成 rank 问题。
3. 当前 5 个 rank 在 loss-vram 二维上都标成 `Pareto=Y`（单调 tradeoff 导致），所以不能只靠 Pareto 选型，仍需结合权重和业务预算。
