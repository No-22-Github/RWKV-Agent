"""b12 pilot (v1.41: bash + get_weather on agent-tool-v2.0) settings; the writer,
fixture helpers and sidecar client are ../casegen.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, Sidecar, check_reference, lines, weather  # noqa: E402,F401

write_case = Batch(salt="b12-pilot", author="llm:claude-opus-5-5-b12", version="v1.41",
                   tool_catalog="agent-tool-v2.0").write_case
