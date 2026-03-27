# Data Notes

## Dataset Summary

The dataset contains:

- `knowledge_base/products/`: product specs, pricing, and feature descriptions
- `knowledge_base/policies/`: return, warranty, shipping, membership, and related policies
- `knowledge_base/store_info/`: branch, contact, and promotion information
- `questions.csv`: 100 Thai multiple-choice questions with choices `1` through `10`
- `sample_submission.csv`: submission format reference

## Important Files

- Knowledge base markdown documents in `knowledge_base/`
- Questions table in `questions.csv`
- Expected output in `sample_submission.csv`

## Prediction Target

- `id`: integer question identifier from `1` to `100`
- `answer`: integer label from `1` to `10`

## Modeling Notes

- This looks like a multiple-choice QA task over Thai documents.
- Retrieval quality will likely matter more than a heavy generative stack for a first pass.
- We may want document-level metadata such as source folder and filename for debugging.
- Options `9` and `10` need explicit decision rules:
  - `9`: missing from knowledge base
  - `10`: unrelated to FahMai store

## Open Questions

- Exact competition slug for Kaggle API download still needs confirmation.
- Final notebook implementation should define local and Kaggle path resolution for these files.
- We still need to choose the first retrieval baseline and reranking approach.
