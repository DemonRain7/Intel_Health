# IntelHealth 推理显存 Benchmark

- **GPU**: NVIDIA A100-SXM4-40GB (39.5 GB)
- **精度**: float16
- **max_new_tokens**: 200

| Agent | Base Model | SFT | Params(MB) | Load(s) | Infer(s) | Tokens | Tok/s | VRAM Load(MB) | VRAM Peak(MB) |
|-------|-----------|-----|-----------|--------|--------|--------|-------|--------------|--------------|
| symptom_normalizer | Qwen/Qwen3-0.6B | Yes | 1433.6 | 22.2 | 5.1 | 83 | 16.4 | 1434.1 | 1469.2 |
| symptom_quality_grader | Qwen/Qwen3-0.6B | Yes | 1433.6 | 17.0 | 1.7 | 42 | 24.2 | 1442.3 | 1466.2 |
| rag_relevance_grader | Qwen/Qwen3-0.6B | Yes | 1433.6 | 14.5 | 0.8 | 19 | 24.0 | 1442.3 | 1463.7 |
| drug_evidence_grader | Qwen/Qwen3-0.6B | Yes | 1433.6 | 15.1 | 1.5 | 35 | 23.0 | 1442.3 | 1465.5 |
| diagnosis_generator | Qwen/Qwen3-1.7B | Yes | 3875.2 | 34.3 | 2.9 | 67 | 23.3 | 3883.4 | 3909.2 |
| drug_recommender | Qwen/Qwen3-0.6B | No (base) | 1433.6 | 13.6 | 8.4 | 200 | 23.9 | 1442.3 | 1483.5 |
| diagnosis_reviewer | Qwen/Qwen3-1.7B | No (base) | 3875.2 | 34.1 | 8.5 | 200 | 23.6 | 3883.4 | 3923.7 |