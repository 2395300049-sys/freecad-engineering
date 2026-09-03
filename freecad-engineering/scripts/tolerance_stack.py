import argparse
import json
import math
import random
from pathlib import Path


def term_limits(term):
    nominal = float(term["nominal"])
    plus = float(term.get("plus_tolerance", 0.0))
    minus = float(term.get("minus_tolerance", 0.0))
    coefficient = float(term.get("coefficient", 1.0))
    endpoints = [coefficient * (nominal - minus), coefficient * (nominal + plus)]
    return coefficient * nominal, min(endpoints), max(endpoints), abs(coefficient) * max(plus, minus)


def sample_term(term, rng):
    nominal = float(term["nominal"])
    plus = float(term.get("plus_tolerance", 0.0))
    minus = float(term.get("minus_tolerance", 0.0))
    distribution = term.get("distribution", "uniform")
    if distribution == "normal":
        sigma = float(term.get("sigma", max(plus, minus) / 3.0 if max(plus, minus) else 0.0))
        value = rng.gauss(nominal, sigma)
        value = min(nominal + plus, max(nominal - minus, value))
    else:
        value = rng.uniform(nominal - minus, nominal + plus)
    return float(term.get("coefficient", 1.0)) * value


def percentile(sorted_values, fraction):
    if not sorted_values:
        return None
    position = fraction * (len(sorted_values) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def main():
    parser = argparse.ArgumentParser(description="Calculate functional tolerance stacks.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--skip-monte-carlo", action="store_true")
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    sample_count = int(data.get("monte_carlo_samples", 0))
    seed = int(data.get("random_seed", 0))
    stack_reports = []

    for stack in data.get("stacks", []):
        nominal = 0.0
        worst_min = 0.0
        worst_max = 0.0
        rss_squared = 0.0
        term_reports = []
        for term in stack.get("terms", []):
            term_nominal, term_min, term_max, half_width = term_limits(term)
            nominal += term_nominal
            worst_min += term_min
            worst_max += term_max
            rss_squared += half_width * half_width
            term_reports.append(
                {"name": term.get("name"), "nominal_contribution": term_nominal, "minimum_contribution": term_min, "maximum_contribution": term_max, "rss_half_width": half_width}
            )

        target_min = float(stack["target_min"])
        target_max = float(stack["target_max"])
        worst_pass = worst_min >= target_min and worst_max <= target_max
        rss_half = math.sqrt(rss_squared)
        rss_result = {"minimum": nominal - rss_half, "nominal": nominal, "maximum": nominal + rss_half}

        monte_carlo = None
        if not args.skip_monte_carlo and sample_count > 0:
            rng = random.Random(seed)
            samples = [sum(sample_term(term, rng) for term in stack.get("terms", [])) for _ in range(sample_count)]
            samples.sort()
            pass_count = sum(target_min <= value <= target_max for value in samples)
            monte_carlo = {
                "samples": sample_count,
                "minimum": samples[0],
                "p00135": percentile(samples, 0.00135),
                "mean": sum(samples) / sample_count,
                "p99865": percentile(samples, 0.99865),
                "maximum": samples[-1],
                "estimated_yield": pass_count / sample_count,
            }

        stack_reports.append(
            {
                "id": stack.get("id"),
                "description": stack.get("description"),
                "unit": stack.get("unit"),
                "target": {"minimum": target_min, "maximum": target_max},
                "terms": term_reports,
                "worst_case": {"minimum": worst_min, "nominal": nominal, "maximum": worst_max, "pass": worst_pass},
                "rss_estimate": rss_result,
                "monte_carlo": monte_carlo,
                "pass": worst_pass,
                "limitations": ["RSS is a screening estimate, not a guaranteed limit.", "Monte Carlo validity depends on supplied distributions and process control."],
            }
        )

    report = {
        "input": str(input_path),
        "stacks": stack_reports,
        "pass": bool(stack_reports) and all(item["pass"] for item in stack_reports),
    }
    report_path = (args.report or input_path.with_name(input_path.stem + "_results.json")).resolve()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "stacks": len(stack_reports)}, ensure_ascii=False))
    print(report_path)
    raise SystemExit(0 if report["pass"] else 2)


if __name__ == "__main__":
    main()
