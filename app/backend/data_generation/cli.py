import argparse
import json
import sys
from pathlib import Path

try:
    from .params import GenerationParams
    from .generator import DataGenerator
    from .validators import validate_and_summarize
except Exception:
    CURRENT_DIR = Path(__file__).resolve().parent
    if str(CURRENT_DIR) not in sys.path:
        sys.path.insert(0, str(CURRENT_DIR))
    from params import GenerationParams
    from generator import DataGenerator
    from validators import validate_and_summarize


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="data-generation", add_help=True)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--semester", type=str, default="2024-2025-1")
    p.add_argument("--academic-year", type=str, default="2024-2025")
    p.add_argument("--num-buildings", type=int, default=3)
    p.add_argument("--num-classrooms", type=int, default=40)
    p.add_argument("--num-teachers", type=int, default=40)
    p.add_argument("--num-courses", type=int, default=120)
    p.add_argument("--days-per-week", type=int, default=5)
    p.add_argument("--timeslots-per-day", type=int, default=8)
    p.add_argument("--weeks-total", type=int, default=16)
    p.add_argument("--utilization-level", type=str, choices=["low", "medium", "high"], default="medium")
    p.add_argument("--conflict-rate", type=float, default=0.0)
    p.add_argument("--include-weekend", action="store_true")
    p.add_argument("--output", type=str, default=None)
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    params = GenerationParams(
        seed=args.seed,
        semester=args.semester,
        academic_year=args.academic_year,
        num_buildings=args.num_buildings,
        num_classrooms=args.num_classrooms,
        num_teachers=args.num_teachers,
        num_courses=args.num_courses,
        days_per_week=args.days_per_week,
        timeslots_per_day=args.timeslots_per_day,
        weeks_total=args.weeks_total,
        utilization_level=args.utilization_level,
        conflict_rate=args.conflict_rate,
        include_weekend=args.include_weekend,
        output=args.output,
    )

    generator = DataGenerator(params)
    dataset = generator.generate()
    dataset = validate_and_summarize(dataset)

    if params.output:
        out_path = Path(params.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
    else:
        json.dump(dataset, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
