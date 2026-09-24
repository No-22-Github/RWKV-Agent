"""python3 -m scripts.corpus <command> ... (run from the repository root)."""

from __future__ import annotations

import argparse
import sys

from . import decontam, paths, render

COMMANDS = {"paths": paths, "render": render, "decontam": decontam}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m scripts.corpus", description=sys.modules[__package__].__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    for name, module in COMMANDS.items():
        sub = commands.add_parser(name, help=module.__doc__.splitlines()[0], description=module.__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
        module.add_arguments(sub)
        sub.set_defaults(handler=module.run, error=sub.error)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
