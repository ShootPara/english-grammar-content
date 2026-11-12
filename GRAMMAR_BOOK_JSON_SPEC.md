# English Grammar Content JSON Specification

```json
{
  "specification_id": "english-grammar-content",
  "specification_version": "3.0.0",
  "purpose": "Reusable instructional content with explicit response bindings and an embedded editorial answer key.",
  "authoritative_artifact": "GRAMMAR_BOOK_EDITED.json",
  "reading_contract": {
    "primary_content": "sections -> lessons -> teaching_block_ids and activities -> content_block_ids; resolve IDs in source_blocks recursively.",
    "paragraph_text": "text is the edited text for presentation; source_text is provenance and must not also be rendered.",
    "tables": "Retain row/cell order, paragraph boundaries, column spans, and vertical merges.",
    "formatting": "Offsets use zero-based Unicode code points, end exclusive. Source formatting is retained separately. Edited formatting is mapped only where the source text still matches.",
    "responses": "Each response_field binds exactly one answer-key part. replace_span replaces its target range; after_prompt presents a separate complete response; annotate_span marks its target; read_only_example renders the supplied example without an input. Offsets are Unicode code points. Never fill worked-example underscore padding. For after_prompt fields, provide a distinct response control or writing area for each editable field. Labels describe the requested output.",
    "worked_examples": "Render worked_example items and their supplied solution content as read-only. Response fields with editable=false are not unanswered quiz inputs; underscore padding in such items must not produce new questions.",
    "answer_key": "Keys remain exclusively in answer_key.entries. Resolve item.answer_key_id and each part.response_field_id. Per-item response_mode and instruction_block_id are authoritative. Alternatives are not exhaustive; automatic grading remains disabled.",
    "scope": "Only instructional content is included. Technical source locations and original instructional wording support traceability; they are not presentation content."
  },
  "canonical_json_schema": {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:english-grammar-content:3.0.0",
    "type": "object",
    "required": [
      "format",
      "schema_version",
      "metadata",
      "source",
      "sections",
      "source_blocks",
      "editorial_changes",
      "validation",
      "answer_key"
    ],
    "properties": {
      "format": {
        "const": "english-grammar-content"
      },
      "schema_version": {
        "const": "3.0.0"
      },
      "metadata": {
        "type": "object"
      },
      "source": {
        "type": "object"
      },
      "sections": {
        "type": "array",
        "minItems": 15,
        "maxItems": 15,
        "items": {
          "type": "object",
          "required": [
            "id",
            "title",
            "lessons"
          ],
          "properties": {
            "id": {
              "type": "string"
            },
            "title": {
              "type": "string"
            },
            "lessons": {
              "type": "array",
              "minItems": 1,
              "items": {
                "type": "object",
                "required": [
                  "id",
                  "title",
                  "teaching_block_ids",
                  "activities"
                ],
                "properties": {
                  "id": {
                    "type": "string"
                  },
                  "title": {
                    "type": "string"
                  },
                  "teaching_block_ids": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    }
                  },
                  "activities": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                      "type": "object",
                      "required": [
                        "id",
                        "instruction",
                        "content_block_ids",
                        "response_contract",
                        "items"
                      ],
                      "properties": {
                        "id": {
                          "type": "string"
                        },
                        "instruction": {
                          "type": "string"
                        },
                        "content_block_ids": {
                          "type": "array",
                          "minItems": 1,
                          "items": {
                            "type": "string"
                          }
                        },
                        "items": {
                          "type": "array",
                          "minItems": 1,
                          "items": {
                            "type": "object",
                            "required": [
                              "id",
                              "content_refs",
                              "response_fields",
                              "answer_key_id",
                              "role",
                              "response_mode",
                              "instruction_block_id",
                              "review_status"
                            ],
                            "properties": {
                              "id": {
                                "type": "string"
                              },
                              "content_refs": {
                                "type": "array",
                                "minItems": 1,
                                "items": {
                                  "type": "object",
                                  "required": [
                                    "block_id",
                                    "row"
                                  ],
                                  "properties": {
                                    "block_id": {
                                      "type": "string"
                                    },
                                    "row": {
                                      "type": [
                                        "integer",
                                        "null"
                                      ],
                                      "minimum": 1
                                    }
                                  },
                                  "additionalProperties": false
                                }
                              },
                              "response_fields": {
                                "type": "array",
                                "minItems": 1,
                                "items": {
                                  "type": "object",
                                  "required": [
                                    "id",
                                    "kind",
                                    "editable",
                                    "answer_part_position",
                                    "answer_key_id",
                                    "placement",
                                    "target",
                                    "label"
                                  ],
                                  "properties": {
                                    "id": {
                                      "type": "string"
                                    },
                                    "kind": {
                                      "enum": [
                                        "text",
                                        "annotation"
                                      ]
                                    },
                                    "editable": {
                                      "type": "boolean"
                                    },
                                    "answer_part_position": {
                                      "type": "integer",
                                      "minimum": 1
                                    },
                                    "answer_key_id": {
                                      "type": "string"
                                    },
                                    "placement": {
                                      "enum": [
                                        "replace_span",
                                        "after_prompt",
                                        "annotate_span",
                                        "read_only_example"
                                      ]
                                    },
                                    "target": {
                                      "anyOf": [
                                        {
                                          "type": "object",
                                          "required": [
                                            "block_id",
                                            "start",
                                            "end"
                                          ],
                                          "properties": {
                                            "block_id": {
                                              "type": "string"
                                            },
                                            "start": {
                                              "type": "integer",
                                              "minimum": 0
                                            },
                                            "end": {
                                              "type": "integer",
                                              "minimum": 1
                                            }
                                          },
                                          "additionalProperties": false
                                        },
                                        {
                                          "type": "null"
                                        }
                                      ]
                                    },
                                    "label": {
                                      "type": "string"
                                    },
                                    "action": {
                                      "enum": [
                                        "underline",
                                        "circle"
                                      ]
                                    }
                                  },
                                  "additionalProperties": false
                                }
                              },
                              "answer_key_id": {
                                "type": "string"
                              },
                              "role": {
                                "enum": [
                                  "question",
                                  "worked_example"
                                ]
                              },
                              "response_mode": {
                                "enum": [
                                  "gap_replacements",
                                  "complete_responses",
                                  "select_option_text",
                                  "annotation",
                                  "classification",
                                  "judgment_and_correction",
                                  "worked_example"
                                ]
                              },
                              "instruction_block_id": {
                                "type": "string"
                              },
                              "review_status": {
                                "const": "reviewed"
                              },
                              "context_block_ids": {
                                "type": "array",
                                "items": {
                                  "type": "string"
                                }
                              },
                              "word_bank_block_ids": {
                                "type": "array",
                                "items": {
                                  "type": "string"
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
      "source_blocks": {
        "type": "array",
        "minItems": 4548,
        "maxItems": 4548,
        "items": {
          "type": "object",
          "required": [
            "id",
            "kind",
            "source"
          ],
          "properties": {
            "id": {
              "type": "string"
            },
            "kind": {
              "enum": [
                "paragraph",
                "table",
                "container",
                "layout"
              ]
            },
            "source": {
              "type": "object",
              "required": [
                "part",
                "xpath",
                "body_block"
              ]
            }
          }
        }
      },
      "editorial_changes": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "id",
            "target_id",
            "before",
            "after",
            "reason",
            "origin"
          ]
        }
      },
      "validation": {
        "type": "object"
      },
      "answer_key": {
        "type": "object",
        "required": [
          "id",
          "status",
          "source_key_status",
          "authorship",
          "coverage",
          "grading_policy",
          "entries"
        ],
        "properties": {
          "id": {
            "type": "string"
          },
          "status": {
            "const": "complete_for_indexed_items"
          },
          "entries": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "object",
              "required": [
                "id",
                "item_id",
                "activity_id",
                "answer_type",
                "provenance",
                "response_mode",
                "parts",
                "automatic_grading",
                "grading_guidance",
                "instruction_block_id"
              ],
              "properties": {
                "id": {
                  "type": "string"
                },
                "item_id": {
                  "type": "string"
                },
                "activity_id": {
                  "type": "string"
                },
                "answer_type": {
                  "enum": [
                    "gap_fill",
                    "completed_sentences",
                    "completed_phrases",
                    "option_text",
                    "annotation",
                    "classification",
                    "mixed",
                    "model_response"
                  ]
                },
                "provenance": {
                  "enum": [
                    "editor_authored",
                    "editor_reviewed_source_example"
                  ]
                },
                "response_mode": {
                  "enum": [
                    "gap_replacements",
                    "complete_responses",
                    "select_option_text",
                    "annotation",
                    "classification",
                    "judgment_and_correction",
                    "worked_example"
                  ]
                },
                "parts": {
                  "type": "array",
                  "minItems": 1,
                  "items": {
                    "type": "object",
                    "required": [
                      "position",
                      "answer",
                      "acceptable_alternatives",
                      "is_empty_answer",
                      "response_field_id"
                    ],
                    "properties": {
                      "position": {
                        "type": "integer",
                        "minimum": 1
                      },
                      "answer": {
                        "type": "string"
                      },
                      "acceptable_alternatives": {
                        "type": "array",
                        "items": {
                          "type": "string"
                        }
                      },
                      "is_empty_answer": {
                        "type": "boolean"
                      },
                      "response_field_id": {
                        "type": "string",
                        "minLength": 1
                      }
                    }
                  }
                },
                "automatic_grading": {
                  "const": false
                },
                "grading_guidance": {
                  "type": "string"
                },
                "instruction_block_id": {
                  "type": "string"
                }
              }
            }
          }
        }
      }
    }
  },
  "validation": {
    "command": "python validate_grammar_book.py --self-test",
    "optional_source_check": "Add --source followed by a local source document path to verify retained source locations and original instructional text.",
    "source_requirement": "The content is self-contained. A source document is optional and used only for provenance verification."
  },
  "compatibility": "Version 3 removes noninstructional front matter and identity metadata. Stable instructional IDs and answer bindings are retained. Source body positions are original locations, not contiguous array indexes."
}
```
