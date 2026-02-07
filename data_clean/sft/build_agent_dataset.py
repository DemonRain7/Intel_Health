# -*- coding: utf-8 -*-
"""Rule-first dataset builder for agent SFT data."""
import argparse
from pathlib import Path
from typing import List, Dict

from generate_sft_data import generate_seed_samples, SFTDataGenerator, AGENT_ALIASES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", type=str, required=True,
                        help="symptom_normalizer|symptom_quality_grader|rag_relevance_grader|drug_evidence_grader")
    parser.add_argument("--num_samples", type=int, default=500)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--output_format", type=str, default="instruction")
    args = parser.parse_args()

    resolved = AGENT_ALIASES.get(args.agent)
    if not resolved:
        raise ValueError(f"Unknown agent: {args.agent}")
    seed_data: List[Dict] = generate_seed_samples(resolved, args.num_samples)
    gen = SFTDataGenerator(api_key="dummy")
    training = gen.convert_to_training_format(seed_data, resolved, output_format=args.output_format)

    out_path = Path(args.output or f"{args.agent}_seed.jsonl")
    gen.save_jsonl(training, str(out_path))
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
