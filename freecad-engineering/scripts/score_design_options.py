import argparse
import json
import operator
from copy import deepcopy
from pathlib import Path


OPERATORS = {
    "<=": operator.le,
    "<": operator.lt,
    ">=": operator.ge,
    ">": operator.gt,
    "==": operator.eq,
    "!=": operator.ne,
}


def evaluate_constraints(option, constraints):
    results = []
    values = option.get("values", {})
    for constraint in constraints:
        field = constraint["field"]
        op = constraint["operator"]
        target = constraint["value"]
        actual = values.get(field)
        passed = actual is not None and op in OPERATORS and OPERATORS[op](actual, target)
        results.append(
            {"field": field, "operator": op, "target": target, "actual": actual, "pass": passed}
        )
    return results


def weighted_scores(options, criteria, weight_override=None):
    weights = weight_override or {item["id"]: float(item["weight"]) for item in criteria}
    total_weight = sum(weights.values())
    weights = {key: value / total_weight for key, value in weights.items()}
    ranges = {}
    for criterion in criteria:
        criterion_id = criterion["id"]
        values = [float(option["values"][criterion_id]) for option in options]
        ranges[criterion_id] = (min(values), max(values))

    scored = []
    for option in options:
        normalized = {}
        score = 0.0
        for criterion in criteria:
            criterion_id = criterion["id"]
            value = float(option["values"][criterion_id])
            minimum, maximum = ranges[criterion_id]
            if maximum == minimum:
                norm = 1.0
            elif criterion["direction"] == "min":
                norm = (maximum - value) / (maximum - minimum)
            else:
                norm = (value - minimum) / (maximum - minimum)
            normalized[criterion_id] = norm
            score += norm * weights[criterion_id]
        scored.append(
            {"id": option["id"], "score": score, "normalized": normalized, "values": option["values"]}
        )
    return sorted(scored, key=lambda item: (-item["score"], item["id"]))


def main():
    parser = argparse.ArgumentParser(description="Score engineering design options after hard constraints.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--sensitivity-fraction", type=float, default=0.2)
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    criteria = data.get("criteria", [])
    constraints = data.get("hard_constraints", [])
    options = data.get("options", [])
    issues = []

    criterion_ids = [item.get("id") for item in criteria]
    if not criteria or len(set(criterion_ids)) != len(criterion_ids):
        issues.append("Criteria must be non-empty with unique IDs")
    for criterion in criteria:
        if criterion.get("direction") not in {"min", "max"}:
            issues.append(f"Invalid direction for {criterion.get('id')}")
        if float(criterion.get("weight", 0)) < 0:
            issues.append(f"Negative weight for {criterion.get('id')}")
    if sum(float(item.get("weight", 0)) for item in criteria) <= 0:
        issues.append("Total criterion weight must be greater than zero")

    evaluated = []
    feasible = []
    for option_item in options:
        missing = [criterion_id for criterion_id in criterion_ids if criterion_id not in option_item.get("values", {})]
        if missing:
            issues.append(f"Option {option_item.get('id')} missing criteria: {missing}")
        results = evaluate_constraints(option_item, constraints)
        passed = all(item["pass"] for item in results)
        evaluated.append({"id": option_item.get("id"), "hard_constraints": results, "feasible": passed})
        if passed and not missing:
            feasible.append(option_item)

    ranking = weighted_scores(feasible, criteria) if feasible and not issues else []
    sensitivity = []
    if ranking:
        base_weights = {item["id"]: float(item["weight"]) for item in criteria}
        for criterion in criteria:
            for direction, multiplier in (("down", 1 - args.sensitivity_fraction), ("up", 1 + args.sensitivity_fraction)):
                varied = deepcopy(base_weights)
                varied[criterion["id"]] *= multiplier
                varied_ranking = weighted_scores(feasible, criteria, varied)
                sensitivity.append(
                    {
                        "criterion": criterion["id"],
                        "variation": direction,
                        "winner": varied_ranking[0]["id"],
                        "winner_score": varied_ranking[0]["score"],
                    }
                )

    report = {
        "input": str(input_path),
        "issues": issues,
        "option_constraint_results": evaluated,
        "feasible_option_count": len(feasible),
        "ranking": ranking,
        "sensitivity": sensitivity,
        "pass": not issues and bool(feasible),
    }
    report_path = (args.report or input_path.with_name(input_path.stem + "_scored.json")).resolve()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "feasible": len(feasible), "winner": ranking[0]["id"] if ranking else None}, ensure_ascii=False))
    print(report_path)
    raise SystemExit(0 if report["pass"] else 2)


if __name__ == "__main__":
    main()
