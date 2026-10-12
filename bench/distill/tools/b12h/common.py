"""b12h (v1.41 first scale batch: bash + get_weather on work-v2) settings; the
writer, fixture helpers and sidecar client are ../casegen.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, Sidecar, check_reference, lines, weather  # noqa: E402,F401

write_case = Batch(salt="b12h", author="llm:claude-sonnet-5-5-b12h", version="v1.41",
                   tool_catalog="work-v2").write_case
