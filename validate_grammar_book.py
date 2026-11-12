"""Validate reusable grammar content and representative consumer behavior.
Requires jsonschema. Optional --source verification also requires lxml.
Run: python validate_grammar_book.py --self-test
"""
import copy, hashlib, json, re, sys, zipfile
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
FILE = ROOT / "GRAMMAR_BOOK_EDITED.json"
SOURCE_FILE = None

def validate(book):
    Draft202012Validator.check_schema(book["schema"])
    Draft202012Validator(book["schema"]).validate(book)
    nodes = {}
    def visit(n):
        assert n["id"] not in nodes, ("duplicate block", n["id"])
        nodes[n["id"]] = n
        for c in n.get("children", []): visit(c)
        for row in n.get("rows", []):
            for c in row["cells"]:
                for child in c["blocks"]: visit(child)
    for n in book["source_blocks"]: visit(n)
    if SOURCE_FILE:
        from lxml import etree
        source = Path(SOURCE_FILE)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == book["source"]["sha256"]
        with zipfile.ZipFile(source) as z:
            xml = etree.fromstring(z.read("word/document.xml"))
        ns = xml.nsmap
        w = "{" + ns["w"] + "}"
    positions = [n["source"]["body_block"] for n in book["source_blocks"]]
    assert positions == sorted(set(positions)), "source order"
    assert all(p > 30 for p in positions), "noninstructional front matter"
    assert not re.search(r"dreaming in english|creative commons|creativecommons|copyright|licensing|open source textbook|project core team|learning supplement series", json.dumps(book), re.I), "removed identity metadata"
    for n in nodes.values():
        if SOURCE_FILE:
            found = xml.xpath(n["source"]["xpath"], namespaces=ns)
            assert len(found) == 1, ("source location", n["id"])
        if n["kind"] != "paragraph": continue
        if SOURCE_FILE:
            out = []
            for child in found[0].iter():
                if child is found[0]: continue
                nearest = next((a for a in child.iterancestors() if a.tag == w+"p"), None)
                if nearest is not found[0]: continue
                local = etree.QName(child).localname
                if local == "t": out.append(child.text or "")
                elif local == "tab": out.append("\t")
                elif local == "br": out.append("\f" if child.get(w+"type") == "page" else "\n")
                elif local == "sym": out.append({"F0FC":"✓", "F0FB":"✗"}.get(child.get(w+"char", ""), ""))
            assert "".join(out) == n["source_text"], ("source text", n["id"])
        for f in n["formatting"]:
            assert 0 <= f["start"] < f["end"] <= len(n["text"]), ("format", n["id"])
    chains = {}
    change_ids = set()
    for c in book["editorial_changes"]:
        assert c["id"] not in change_ids
        change_ids.add(c["id"])
        n = nodes[c["target_id"]]
        previous = chains.get(n["id"], n.get("source_text"))
        assert previous == c["before"], ("change chain", c["id"])
        chains[n["id"]] = c["after"]
    for n in nodes.values():
        if n["kind"] == "paragraph":
            assert chains.get(n["id"], n["source_text"]) == n["text"]
    keys = {}
    key_ids = set()
    for k in book["answer_key"]["entries"]:
        assert k["item_id"] not in keys and k["id"] not in key_ids, "duplicate key"
        keys[k["item_id"]] = k
        key_ids.add(k["id"])
    items = {}
    fields = set()
    activity_ids = set()
    lesson_ids = set()
    def check_ref(r):
        n = nodes[r["block_id"]]
        if r["row"] is not None:
            assert n["kind"] == "table" and 1 <= r["row"] <= len(n["rows"])
    for section in book["sections"]:
        for lesson in section["lessons"]:
            assert lesson["id"] not in lesson_ids
            lesson_ids.add(lesson["id"])
            presented = set(lesson["teaching_block_ids"])
            for bid in presented: assert bid in nodes
            for a in lesson["activities"]:
                assert a["id"] not in activity_ids and a["items"]
                activity_ids.add(a["id"])
                assert a["instruction"] == nodes[a["instruction_block_id"]]["text"]
                presented.update([a["instruction_block_id"]]+a["content_block_ids"])
                for bid in a["content_block_ids"]: assert bid in nodes
                for i in a["items"]:
                    assert i["id"] not in items
                    items[i["id"]] = i
                    k = keys[i["id"]]
                    assert k["id"] == i["answer_key_id"] and k["activity_id"] == a["id"]
                    assert k["response_mode"] == i["response_mode"]
                    assert k["instruction_block_id"] == i["instruction_block_id"]
                    assert i["instruction_block_id"] in nodes
                    assert k["context_block_ids"] == i["context_block_ids"]
                    for bid in i["context_block_ids"]+i["word_bank_block_ids"]: assert bid in nodes
                    for r in i["content_refs"]+i["source_solution_refs"]: check_ref(r)
                    assert len(i["response_fields"]) == len(k["parts"])
                    for index, (f, part) in enumerate(zip(i["response_fields"], k["parts"]), 1):
                        assert f["id"] not in fields
                        fields.add(f["id"])
                        assert part["position"] == f["answer_part_position"] == index
                        assert part["response_field_id"] == f["id"]
                        assert f["answer_key_id"] == k["id"]
                        assert part["answer"] or part["is_empty_answer"]
                        assert bool(part["answer"]) != part["is_empty_answer"]
                        assert f["editable"] == (i["role"] != "worked_example")
                        if f["target"]:
                            t = f["target"]; text = nodes[t["block_id"]]["text"]
                            assert 0 <= t["start"] < t["end"] <= len(text)
                            if f["placement"] == "replace_span":
                                assert re.fullmatch(r"_{2,}", text[t["start"]:t["end"]])
                        else:
                            assert f["placement"] in ("after_prompt", "read_only_example")
                    if i["role"] == "worked_example":
                        assert i["response_mode"] == "worked_example"
                        if i["example_origin"] == "editor_authored":
                            assert k["provenance"] == "editor_authored" and not k["source_worked_example"]
                        else:
                            assert k["provenance"] == "editor_reviewed_source_example"
                            assert i["source_solution_refs"]
                    expected = k["answer_type"] == "model_response" or any(p["acceptable_alternatives"] for p in k["parts"])
                    assert i["allow_multiple_valid_responses"] == expected
                assert a["response_contract"]["allow_multiple_valid_responses"] == any(i["allow_multiple_valid_responses"] for i in a["items"])
            lo, hi = lesson["source_body_range"]
            for n in book["source_blocks"]:
                if lo <= n["source"]["body_block"] <= hi and n["kind"] == "paragraph" and n["text"].strip():
                    assert n["id"] in presented, ("presentation omission", lesson["id"], n["id"])
    assert set(items) == set(keys)
    assert len(change_ids) == book["validation"]["editorial_change_records"]
    for n in nodes.values():
        assert set(n.get("editorial_change_ids", [])) == {c["id"] for c in book["editorial_changes"] if c["target_id"] == n["id"]}
    assert len(items) == book["validation"]["indexed_items"]
    assert len(keys) == book["validation"]["answer_key_entries"]
    assert len(lesson_ids) == book["validation"]["lessons"]
    assert sum(i["role"]=="worked_example" for i in items.values()) == book["validation"]["worked_examples_identified"]
    return nodes, items, keys

def preview_item(book, item_id):
    """Minimal read-only consumer contract: separate prompt and responses."""
    nodes, items, keys = validate(book)
    i = items[item_id]
    return {"instruction": nodes[i["instruction_block_id"]]["text"],
            "prompt_refs": i["content_refs"], "context": [nodes[x]["text"] for x in i["context_block_ids"]],
            "inputs": [f for f in i["response_fields"] if f["editable"]],
            "example_refs": i["source_solution_refs"] if i["role"]=="worked_example" else [],
            "key": keys[item_id]}

def self_test(book):
    results = []
    tests = {
        "missing_key": lambda b: b["answer_key"]["entries"].pop(),
        "duplicate_key": lambda b: b["answer_key"]["entries"].append(copy.deepcopy(b["answer_key"]["entries"][0])),
        "empty_activity": lambda b: b["sections"][0]["lessons"][0]["activities"][0].update(items=[]),
        "bad_key_reference": lambda b: b["sections"][0]["lessons"][0]["activities"][0]["items"][0].update(answer_key_id="missing"),
        "bad_block_reference": lambda b: b["sections"][0]["lessons"][0]["activities"][0]["items"][0]["content_refs"][0].update(block_id="missing"),
        "collapsed_multipart": lambda b: b["sections"][1]["lessons"][4]["activities"][0]["items"][0]["response_fields"].pop(),
        "false_source_provenance": lambda b: next(k for k in b["answer_key"]["entries"] if k["item_id"]=="s01-l06-activity-02-item-01").update(provenance="editor_reviewed_source_example"),
        "invalid_empty_answer": lambda b: b["answer_key"]["entries"][0]["parts"][0].update(answer="",is_empty_answer=False)
    }
    for name, mutate in tests.items():
        damaged = copy.deepcopy(book); mutate(damaged)
        try: validate(damaged)
        except (AssertionError, KeyError, ValueError, IndexError): results.append(name)
        except Exception as exc:
            if exc.__class__.__name__ == "ValidationError": results.append(name)
            else: raise
        else: raise AssertionError(("negative test accepted", name))
    nodes, items, keys = validate(book)
    assert len(items["s02-l05-activity-01-item-01"]["response_fields"]) == 5
    assert items["s11-l01-activity-02-item-01"]["response_fields"][0]["action"] == "circle"
    assert items["s03-l06-activity-02-item-08"]["context_block_ids"] == ["b1111"]
    assert keys["s14-l06-activity-02-item-05"]["parts"][0]["is_empty_answer"]
    assert items["s01-l10-activity-01-item-06"]["instruction_block_id"] == "b0443"
    assert items["s07-l01-activity-02-item-01"]["content_refs"][0]["row"] == 1
    assert items["s14-l15-activity-02-item-06"]["word_bank_block_ids"]
    assert not any(f["editable"] for f in items["s12-l06-activity-02-item-01"]["response_fields"])
    return results

if __name__ == "__main__":
    if "--source" in sys.argv:
        SOURCE_FILE = sys.argv[sys.argv.index("--source") + 1]
    book = json.loads(FILE.read_text(encoding="utf-8"))
    nodes, items, keys = validate(book)
    tested = self_test(book) if "--self-test" in sys.argv else []
    print(json.dumps({"schema":"passed","semantic_checks":"passed","source_integrity":"passed" if SOURCE_FILE else "not_requested",
        "items":len(items),"keys":len(keys),"fields":sum(len(i["response_fields"]) for i in items.values()),
        "negative_tests_rejected":tested,"consumer_cases":"passed" if tested else "not_run",
        "artifact_sha256":hashlib.sha256(FILE.read_bytes()).hexdigest()}, indent=2))
