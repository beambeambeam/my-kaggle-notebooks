# Super AI Engineer S6 FahMai RAG Challenge (level 1)

## Competition

- Name: Super AI Engineer S6 FahMai RAG Challenge (level 1)
- Store: FahMai (ฟ้าใหม่), a fictional Thai electronics store
- Task: Answer 100 Thai multiple-choice questions using a RAG system over the provided knowledge base
- Evaluation: Accuracy

## Problem Statement

Build a Retrieval-Augmented Generation workflow that reads Thai markdown documents from the store knowledge base and predicts the correct answer choice from 10 options for each question.

Choice semantics:

- `1`-`8`: content-specific answers
- `9`: `ไม่มีข้อมูลนี้ในฐานข้อมูล`
- `10`: `คำถามนี้ไม่เกี่ยวข้องกับร้านฟ้าใหม่`

## Objective

Produce a submission CSV with exactly 100 rows:

```csv
id,answer
1,5
2,3
```

The goal is to maximize leaderboard accuracy on both the public and private splits.

## First-Draft Plan

1. Inspect the Thai knowledge base structure and question format.
2. Build a simple document loader and chunking pipeline for markdown files.
3. Create a retrieval baseline using BM25 or embedding similarity.
4. Score each answer choice against retrieved context and question intent.
5. Add explicit handling for option `9` and option `10`.
6. Generate a valid 100-row submission and review weak questions manually.

## Notes

- All source documents are in Thai.
- The competition appears retrieval-heavy rather than classic tabular ML.
- Notebook placeholders still need competition-specific path resolution and submission logic.
