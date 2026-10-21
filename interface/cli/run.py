"""
Run one engine operating point and print it: performance and station tables, the same numbers as the dashboard
and the TUI (interface/tables.py).

Run from the repo root:
    .venv/Scripts/python -m interface.cli.run
    .venv/Scripts/python -m interface.cli.run --engine closed_cycle_nuclear_turbofan --set PR=4 --set T_tet=1300
    .venv/Scripts/python -m interface.cli.run --engine nuclear --inputs
"""
import argparse
import sys

from interface.gui.dashboard_view import EngineView
from interface.gui.engines import ENGINES
from interface.tables import performance_rows, station_header, station_rows


def _table(header: list[str] | None, rows: list[list[str]], right_from: int) -> str:
    """Columns padded to their widest cell; columns from right_from on are right-aligned (numbers)."""
    lines = ([header] if header else []) + rows
    widths = [max(len(line[i]) for line in lines) for i in range(len(lines[0]))]
    fmt = lambda line: "  ".join(c.rjust(w) if i >= right_from else c.ljust(w) for i, (c, w) in enumerate(zip(line, widths)))
    out = [fmt(line) for line in lines]
    if header:
        out.insert(1, "  ".join("-" * w for w in widths))
    return "\n".join("  " + line.rstrip() for line in out)


def print_inputs(view: EngineView) -> None:
    for group, items in view.inputs.items():
        print(f"\n{group}")
        rows = [[i.key, i.label, f"{i.default:g}" if not i.options else str(i.default),
                 " / ".join(i.options) if i.options else f"{i.lo:g} .. {i.hi:g}"] for i in items]
        print(_table(None, rows, right_from=2))


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")        # subscripts and Greek symbols on the Windows console
    parser = argparse.ArgumentParser(description="Run one engine operating point and print it.")
    parser.add_argument("--engine", default="conventional", choices=ENGINES)
    parser.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="input value (default: SKYF spec)")
    parser.add_argument("--inputs", action="store_true", help="list the engine's inputs and defaults, then exit")
    args = parser.parse_args(argv)
    view = ENGINES[args.engine][1]

    print(view.title, flush=True)      # before any error on stderr
    if args.inputs:
        print_inputs(view)
        return 0

    pairs = [p.partition("=") for p in args.set]
    if any(not sep or not v for _, sep, v in pairs):
        print(f"--set takes KEY=VALUE, got: {' '.join(args.set)}", file=sys.stderr)
        return 1
    try:
        values = view.defaults | view.check({k: v for k, _, v in pairs})
        snap = view.evaluate(values)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    except Exception as e:      # the model raising is an operating point it cannot run
        print(f"The model could not run this point: {e}", file=sys.stderr)
        return 1

    print(snap.subtitle, flush=True)
    if snap.error:
        print(f"\n{snap.error}", file=sys.stderr)
        return 1
    print("\nPerformance")
    print(_table(None, [list(r) for r in performance_rows(snap)], right_from=1))
    print("\nStations")
    print(_table(station_header(), station_rows(view, snap), right_from=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
