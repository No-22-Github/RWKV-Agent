"""b20b builder: python3 build.py -> bench/distill/v2.0/cases/{notool,docs,...}/<id>/. Deterministic (no randomness)."""
import common
import t1
import t2
import t3


def main():
    cases = t1.CASES + t2.CASES + t3.CASES
    assert len(cases) == 40 and len({c["id"] for c in cases}) == 40
    for c in cases:
        common.build(c)
    print("wrote", len(cases), "cases")


if __name__ == "__main__":
    main()
