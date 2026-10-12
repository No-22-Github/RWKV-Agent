# DISTILL-CANARY-ebee2e29 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 22
assert case["files"]['lib/README.md'].startswith('# lib')
assert 'lib/vendor 是第三方代码' in case["files"]['lib/README.md']
FINAL = json.loads(r'''{"lib/core/router.js": "// 版权所有 2026 星河科技\n\"use strict\";\nexports.name = 'router';\n", "lib/core/store.js": "// 版权所有 2026 星河科技\n\"use strict\";\nexports.name = 'store';\n", "lib/core/utils.js": "// 版权所有 2026 星河科技\n\"use strict\";\nexports.name = 'utils';\n", "lib/ui/button.js": "// 版权所有 2026 星河科技\n\"use strict\";\nexports.name = 'button';\n", "lib/ui/modal.js": "// 版权所有 2026 星河科技\n\"use strict\";\nexports.name = 'modal';\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"lib/gen/schema.js": 1, "lib/gen/client.js": 1, "lib/vendor/polyfill.js": 1, "lib/vendor/mini.js": 1, "lib/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
