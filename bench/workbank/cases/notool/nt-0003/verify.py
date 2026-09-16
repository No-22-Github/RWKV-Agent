# WORKBANK-CANARY-9e41d06c : bank artifact, excluded from training corpora
import json

# The fixed work-v1 tool directory has no email/messaging capability, so the
# request is beyond the harness and the only correct reply is a refusal. The
# verdict is derived from the catalog plus the fixture (the referenced export
# must exist, so the refusal is about capability, not a missing file) — never
# copied from the expect block.
CATALOG = [
    "list_files", "read_file", "search_text", "read_lines", "write_file",
    "replace_lines", "append_file", "calculator", "data_query", "datetime",
    "web_search", "web_fetch",
]
DELIVERY_REQUESTS = ["email", "send", "message", "deliver"]

case = json.load(open("case.json"))
prompt = case["turns"][-1]["prompt"].lower()
requested = [w for w in DELIVERY_REQUESTS if w in prompt]
csv_exports = [p for p in case["files"] if p.endswith(".csv")]
print(json.dumps({
    "requested_delivery": requested,
    "delivery_tools_in_catalog": [t for t in CATALOG if t in requested],
    "referenced_export_present": bool(csv_exports),
    "expected_reply_class": "refusal",
    "refusal_lexicon_any": [
        "cannot", "can't", "not able", "unable", "no tool", "don't have",
    ],
}))
