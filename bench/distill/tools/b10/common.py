"""b10 pilot (v1.4 M2) settings; the writer itself is ../casegen.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

write_case = Batch(salt="b10-pilot", author="llm:claude-opus-5-5-b10", version="v1.4").write_case
