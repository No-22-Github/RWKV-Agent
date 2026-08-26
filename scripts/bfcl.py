#!/usr/bin/env python3
import os
from importlib.metadata import version
from pathlib import Path

MODEL_NAME = "rwkv-agent-bfcl-ab-v1"
EVALUATOR_VERSION = "2026.3.23"
REPO_ROOT = Path(__file__).resolve().parents[1]

os.environ.setdefault("BFCL_PROJECT_ROOT", str(REPO_ROOT))

from bfcl_eval.constants.model_config import (
    MODEL_CONFIG_MAPPING,
    ModelConfig,
)  # noqa: E402
from bfcl_eval.model_handler.local_inference.base_oss_handler import (
    OSSHandler,
)  # noqa: E402
from overrides import override  # noqa: E402


class RWKVAgentDecodeOnlyHandler(OSSHandler):
    @override
    def inference(self, test_entry, include_input_log, exclude_state_log):
        raise RuntimeError("rwkv-agent BFCL handler is decode-only")

    @override
    def decode_execute(self, result, has_tool_call_tag):
        # The Go multi-turn harness persists already-decoded BFCL call strings
        # as one list per agent step. Single-turn artifacts remain raw strings
        # and continue through the pinned evaluator's normal decoder.
        if isinstance(result, list) and all(isinstance(call, str) for call in result):
            return result
        return super().decode_execute(result, has_tool_call_tag)


def register_decode_only_handler() -> None:
    installed_version = version("bfcl_eval")
    if installed_version != EVALUATOR_VERSION:
        raise RuntimeError(
            f"bfcl-eval {EVALUATOR_VERSION} required, found {installed_version}"
        )
    MODEL_CONFIG_MAPPING[MODEL_NAME] = ModelConfig(
        model_name=MODEL_NAME,
        display_name="RWKV-Agent BFCL A+B v1 (decode-only)",
        url="",
        org="RWKV-Agent",
        license="local evaluation only",
        model_handler=RWKVAgentDecodeOnlyHandler,
        input_price=None,
        output_price=None,
        is_fc_model=False,
        underscore_to_dot=False,
    )


def main() -> None:
    register_decode_only_handler()
    from bfcl_eval.__main__ import cli

    cli()


if __name__ == "__main__":
    main()
