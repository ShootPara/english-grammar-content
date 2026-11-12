# English Grammar Content

Human-created English grammar teaching material, exercises, and examples, packaged as JSON for reuse in websites, learning tools, and games.

## Where this came from

I commissioned the original content for **Dreaming in English**, a project that no longer exists. The core grammar material was written by humans. Although some of it may appear derivative or resemble familiar grammar teaching material, its origin is human-created work that I commissioned.

This repository harvests useful assets from that project so they can become part of new projects. The original [Word document](<Grammar Book First Draft Complete.docx>) is included as the provenance record. It retains its historical wording and project information. The reusable JSON removes that front matter and project identity.

AI was used mainly to proofread the material, correct human mistakes, and generate the answer key. AI also produced the structured JSON representation and a small number of missing worked examples. Supplied examples and editorially generated answers are distinguished in the data. The core teaching content remains of human origin; the answer key and editorial additions should not be described as entirely human-authored.

The JSON is platform-neutral data that coding agents and platforms can ingest to add grammar exercises or games to a website. An application still needs to implement the rendering, interaction, and assessment behavior described below.

## What is here

| File | Purpose |
| --- | --- |
| [GRAMMAR_BOOK_EDITED.json](GRAMMAR_BOOK_EDITED.json) | Authoritative reusable content, format version 3.0.0, with the answer key embedded. |
| [GRAMMAR_BOOK_JSON_SPEC.md](GRAMMAR_BOOK_JSON_SPEC.md) | Reading contract and matching JSON Schema. |
| [Grammar Book First Draft Complete.docx](<Grammar Book First Draft Complete.docx>) | Unmodified original commissioned manuscript, retained for provenance. |
| [validate_grammar_book.py](validate_grammar_book.py) | Schema, reference, response-binding, editorial-history, and optional source-integrity checks. |
| [AGENTS.md](AGENTS.md) | Instructions for coding agents changing or consuming these assets. |
| [requirements.txt](requirements.txt) | Python dependencies for validation. |

The content contains **15 sections, 115 lessons, 231 indexed activities, 1,704 indexed items, 1,704 answer-key entries, and 1,841 response components**. There are 45 worked examples. An item can require several responses, so an item is not necessarily one sentence or one blank.

The historical filenames are retained for continuity. Version 3 is a reusable content collection, with no dependency on the original project's branding or page layout. Earlier drafts, temporary files, review reports, and the diagnostic PDF are excluded from this repository.

## Start here, coding agents

Read `reading_contract` in the JSON and the specification before building an importer. The JSON includes its own schema under `schema`.

1. Traverse `sections` and their `lessons` in order. Resolve teaching and activity block IDs through a recursively built index of `source_blocks`. Blocks can contain children or tables with `rows -> cells -> blocks`.
2. Render paragraph `text`, which is the corrected presentation text. Keep `source_text` for provenance and editorial comparison. Do not display both as duplicate content.
3. Preserve tables, cell spans, paragraph boundaries, and meaningful formatting. Formatting offsets use Unicode code points, with an exclusive end. JavaScript string offsets use UTF-16 code units, so convert when necessary.
4. Use each item's authoritative `instruction_block_id`, context references, and word-bank references. A combined activity can contain more than one instruction group.
5. Render every `response_field` according to its `placement`. `replace_span` supplies a gap replacement; `after_prompt` requires a separate complete response; `annotate_span` identifies text to mark; `read_only_example` is a supplied example, not an unanswered question.
6. Resolve `answer_key_id`, then match each answer part to its `response_field_id`. Never infer the number of expected responses from underscore runs or assume one answer per item.
7. Keep answers out of learner prompts until the application intentionally reveals them. Treat `is_empty_answer=true` as an intentional answer requiring no inserted word, not a missing key.

For a first integration, choose one lesson and implement its actual response types before generalizing across the collection. The validator's `preview_item` helper demonstrates resolution for a single item without prescribing an application framework.

## Assessment and editorial limits

Automatic grading is disabled in this content contract. Many responses admit alternatives, and model answers for open exercises are examples rather than exhaustive lists of correct responses. An application that adds scoring must define and test its own grading policy.

Intentionally incorrect sentences and distractors are part of some exercises. Do not automatically correct them. Keep the distinction between teaching examples, questions, and worked examples.

Validation checks structural integrity and declared relationships. It does not certify every grammatical judgment or eliminate every possible editorial improvement. Preserve the human-created material's variety while making targeted, recorded corrections.

## Validate locally

Use Python 3.12 or later. A virtual environment is recommended.

```sh
python -m pip install -r requirements.txt
python validate_grammar_book.py --self-test
python validate_grammar_book.py --self-test --source "Grammar Book First Draft Complete.docx"
```

The first validation command checks the self-contained JSON and deliberately corrupted variants. The second also verifies the original file's SHA-256, retained source locations, and original instructional wording. A consumer does not need the Word document to use the JSON.

Original Word document SHA-256:

```text
b366a1f1e938eba4002f9084eab5351d5e168300ddb4323a78c63f25d546bbbe
```

Source block IDs and `body_block` positions retain their original locations. They are intentionally not renumbered after removal of the front matter. Use explicit references rather than array-index arithmetic.
