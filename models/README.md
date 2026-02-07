# Model Artifacts

Use this folder to store local model artifacts for inference and experiments.

- `base/`: optional local base models (if you do not load from remote provider).
- `adapters/`: LoRA/QLoRA adapter outputs by agent or profile.
- `merged/`: optional merged checkpoints for deployment.

Recommended layout:

```text
models/
  base/
  adapters/
    symptom_normalizer/
    diagnosis_generator/
    rag_relevance_grader/
    drug_evidence_grader/
  merged/
```

Do not commit large model weights to Git. Keep this file as a path convention only.

## Per-agent serving

Current `config/model_profiles.json` is configured for one local endpoint per agent.

- `symptom_normalizer` -> `models/merged/symptom_normalizer` -> `http://127.0.0.1:8101/v1`
- `symptom_quality_grader` -> `models/merged/symptom_quality_grader` -> `http://127.0.0.1:8102/v1`
- `rag_relevance_grader` -> `models/merged/rag_relevance_grader` -> `http://127.0.0.1:8103/v1`
- `diagnosis_generator` -> `models/merged/diagnosis_generator` -> `http://127.0.0.1:8104/v1`
- `drug_evidence_grader` -> `models/merged/drug_evidence_grader` -> `http://127.0.0.1:8105/v1`
- `drug_recommender` -> `models/merged/drug_recommender` -> `http://127.0.0.1:8106/v1`
- `output_formatter` -> `models/merged/output_formatter` -> `http://127.0.0.1:8107/v1`

You can also override with env vars:

- `${AGENT}_LOCAL_MODEL_PATH`
- `${AGENT}_LOCAL_URL`

Example prefix: `DIAGNOSIS_GENERATOR_LOCAL_MODEL_PATH`.
