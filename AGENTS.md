# Coding agent instructions

## Purpose and provenance

This repository contains reusable English grammar content. Read README.md for the owner's account of its human origin and the role of AI. The original commissioned material was intended for Dreaming in English, which no longer exists.

`Grammar Book First Draft Complete.docx` is an immutable provenance artifact. Do not edit, re-save, or regenerate it. The authoritative application content is `GRAMMAR_BOOK_EDITED.json`. AI-generated answers and editorial additions must remain distinguishable from supplied material.

## Content changes

- Preserve stable section, lesson, activity, item, block, and response IDs unless a migration explicitly requires otherwise.
- Present `text`; preserve `source_text`, source locations, and source formatting for traceability.
- Record paragraph edits in `editorial_changes`, with a continuous before/after chain and matching block `editorial_change_ids`.
- Recalculate affected formatting and response target offsets when changing text. Offsets count Unicode code points, not UTF-16 units.
- Reconcile affected instructions, answer parts, alternatives, context, and word-bank references together.
- Preserve deliberate grammatical errors in correction exercises and distractors in choice exercises.
- Keep the authoritative answer key embedded in the JSON. The requested PDF includes a rendered answer-key appendix generated from those entries.
- Keep historical branding, attribution, publication front matter, and project identity out of the reusable JSON. The README and original Word file provide provenance. Ordinary exercise sentences about books or fictional people are instructional content and should remain.
- Keep the embedded schema and `GRAMMAR_BOOK_JSON_SPEC.md` synchronized when changing the format. Update declared counts and versions when appropriate.
- Do not add layout assumptions or automatic-grading claims to the content without an explicit implementation and validation plan.

## Checks

Install requirements.txt, then run:

```sh
python validate_grammar_book.py --self-test --source "Grammar Book First Draft Complete.docx"
```

For content changes, also inspect the affected lesson, its instructions, and its answer-key entries together. Passing schema validation alone does not establish instructional correctness.

Do not commit temporary renderings, old diagnostic PDFs, local environments, historical review snapshots, or credentials. The published practice PDF under output/pdf is an intentional deliverable. This is a data repository, not a complete exercise application.
