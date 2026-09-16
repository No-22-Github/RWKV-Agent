# WORKBANK-CANARY-72af8b13 : bank artifact, excluded from training corpora
import json
import re

# The figure is computable from the prompt's rate alone (zero tools needed),
# and the delivery half is beyond the fixed work-v1 catalog, so the expected
# reply is a figure plus a refusal. Both halves are derived independently of
# the expect block.
CATALOG = [
    "list_files", "read_file", "search_text", "read_lines", "write_file",
    "replace_lines", "append_file", "calculator", "data_query", "datetime",
    "web_search", "web_fetch",
]
DELIVERY_REQUESTS = ["email", "send", "message", "deliver"]

case = json.load(open("case.json"))
prompt = case["turns"][-1]["prompt"]
rate_gb_per_min = float(re.search(r"([\d.]+)\s*GB per minute", prompt).group(1))
daily_gb = rate_gb_per_min * 24 * 60
requested = [w for w in DELIVERY_REQUESTS if w in prompt.lower()]
print(json.dumps({
    "daily_volume_gb": daily_gb,
    "figure_in_reply": str(int(daily_gb)),
    "requested_delivery": requested,
    "delivery_tools_in_catalog": [t for t in CATALOG if t in requested],
    "expected_reply_class": "figure_plus_refusal",
    "refusal_lexicon_any": [
        "cannot", "can't", "not able", "unable", "no tool", "don't have",
    ],
}))
