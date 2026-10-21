"""
Build an engine report as PDF - one function for every front end (CLI below, TUI, web API).

Run from the repo root:
    .venv/Scripts/python -m reports.build
    .venv/Scripts/python -m reports.build --engine conventional --set V_0=230 --set PR=4 --sweep V_0 h_0 T_tet
Writes reports/output/<engine>.pdf (LaTeX sources and logs in reports/output/<engine>_build/).
"""
import argparse
import sys
import time
from pathlib import Path

from interface.gui.engines import ENGINES
from reports.engine_report import engine_report
from reports.report import Case, ReportError

OUTPUT = Path(__file__).parent / "output"
DEFAULT_SWEEPS = ["V_0"]
DEFAULT_POINTS = 25


def build_report(engine: str, values: dict, sweeps: list[str] = DEFAULT_SWEEPS, points: int = DEFAULT_POINTS,
                 pdf: Path | None = None) -> Path:
    """Evaluate the design point, run the sweeps, typeset; returns the PDF path. Raises ReportError."""
    if engine not in ENGINES:
        raise ReportError(f"Unknown engine '{engine}'. Known: {', '.join(ENGINES)}")
    view = ENGINES[engine][1]
    try:
        values = view.check(values)
    except ValueError as e:
        raise ReportError(str(e)) from None
    case = Case.evaluate(engine, view, values)
    try:
        report = engine_report(case, sweeps, points)
    except ValueError as e:
        raise ReportError(str(e)) from None
    return report.build(pdf or OUTPUT / f"{engine}.pdf")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a PDF engine report.")
    parser.add_argument("--engine", default="conventional", choices=ENGINES)
    parser.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="design-point input")
    parser.add_argument("--sweep", nargs="*", default=DEFAULT_SWEEPS, metavar="KEY", help="inputs to sweep (none: no sweep)")
    parser.add_argument("--points", type=int, default=DEFAULT_POINTS, help="points per sweep")
    parser.add_argument("--out", type=Path, help="PDF path (default reports/output/<engine>.pdf)")
    args = parser.parse_args(argv)

    start = time.perf_counter()
    try:
        pairs = [p.partition("=") for p in args.set]
        if any(not sep or not v for _, sep, v in pairs):
            raise ReportError(f"--set takes KEY=VALUE, got: {' '.join(args.set)}")
        pdf = build_report(args.engine, {k: v for k, _, v in pairs}, args.sweep, args.points, args.out)
    except ReportError as e:
        print(f"Report failed: {e}", file=sys.stderr)
        return 1
    print(f"Report written: {pdf}  ({time.perf_counter() - start:.1f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
