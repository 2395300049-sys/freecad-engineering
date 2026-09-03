import argparse
import json
from pathlib import Path


def nonnegative(value, name):
    number = float(value)
    if number < 0:
        raise ValueError(f"{name} must be non-negative")
    return number


def main():
    parser = argparse.ArgumentParser(description="Estimate transparent process-based manufacturing cost.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    part_reports = []
    issues = []

    for part in data.get("parts", []):
        try:
            batch = int(part["batch_quantity"])
            if batch <= 0:
                raise ValueError("batch_quantity must be greater than zero")
            finished_mass = nonnegative(part["finished_mass_kg"], "finished_mass_kg")
            blank_mass = nonnegative(part["blank_mass_kg"], "blank_mass_kg")
            if blank_mass < finished_mass:
                raise ValueError("blank mass cannot be lower than finished mass")
            material_gross = blank_mass * nonnegative(part["material_cost_per_kg"], "material_cost_per_kg")
            scrap_recovery = (blank_mass - finished_mass) * nonnegative(part.get("material_scrap_recovery_per_kg", 0), "scrap recovery")
            material_net = material_gross - scrap_recovery
            if material_net < 0:
                raise ValueError("scrap recovery cannot exceed gross material cost")

            operation_reports = []
            operations_total = 0.0
            for operation in part.get("operations", []):
                setup_h = nonnegative(operation.get("setup_time_h", 0), "setup_time_h")
                cycle_h = nonnegative(operation.get("cycle_time_h_per_part", 0), "cycle_time_h_per_part")
                machine_rate = nonnegative(operation.get("machine_rate_per_h", 0), "machine_rate_per_h")
                labor_rate = nonnegative(operation.get("labor_rate_per_h", 0), "labor_rate_per_h")
                labor_fraction = nonnegative(operation.get("labor_fraction", 0), "labor_fraction")
                if labor_fraction > 1:
                    raise ValueError("labor_fraction cannot exceed 1")
                tooling = nonnegative(operation.get("tooling_batch_cost", 0), "tooling_batch_cost")
                setup_unit = setup_h * (machine_rate + labor_rate) / batch
                cycle_machine = cycle_h * machine_rate
                cycle_labor = cycle_h * labor_rate * labor_fraction
                tooling_unit = tooling / batch
                unit_cost = setup_unit + cycle_machine + cycle_labor + tooling_unit
                operations_total += unit_cost
                operation_reports.append(
                    {"name": operation.get("name"), "setup_unit": setup_unit, "cycle_machine": cycle_machine, "cycle_labor": cycle_labor, "tooling_unit": tooling_unit, "unit_cost": unit_cost}
                )

            inspection = nonnegative(part.get("inspection_time_h_per_part", 0), "inspection_time_h_per_part") * nonnegative(part.get("inspection_rate_per_h", 0), "inspection_rate_per_h")
            direct = (
                material_net
                + operations_total
                + nonnegative(part.get("subcontract_cost_per_part", 0), "subcontract cost")
                + inspection
                + nonnegative(part.get("assembly_cost_per_part", 0), "assembly cost")
                + nonnegative(part.get("packaging_cost_per_part", 0), "packaging cost")
            )
            overhead = direct * nonnegative(part.get("overhead_fraction", 0), "overhead fraction")
            contingency = (direct + overhead) * nonnegative(part.get("contingency_fraction", 0), "contingency fraction")
            unit_total = direct + overhead + contingency
            part_reports.append(
                {
                    "part_number": part.get("part_number"),
                    "description": part.get("description"),
                    "batch_quantity": batch,
                    "material": {"gross": material_gross, "scrap_recovery": scrap_recovery, "net": material_net},
                    "operations": operation_reports,
                    "inspection": inspection,
                    "direct_unit_cost": direct,
                    "overhead": overhead,
                    "contingency": contingency,
                    "estimated_unit_cost": unit_total,
                    "estimated_batch_cost": unit_total * batch,
                }
            )
        except (KeyError, TypeError, ValueError) as exc:
            issues.append({"part_number": part.get("part_number"), "error": str(exc)})

    report = {
        "input": str(input_path),
        "currency": data.get("currency"),
        "estimate_date": data.get("estimate_date"),
        "parts": part_reports,
        "issues": issues,
        "estimated_total_batch_cost": sum(item["estimated_batch_cost"] for item in part_reports),
        "pass": bool(part_reports) and not issues,
        "limitations": ["This is an engineering estimate, not a supplier quotation.", "Rates, yields, quantities, and process routes must be dated and verified."],
    }
    report_path = (args.report or input_path.with_name(input_path.stem + "_estimate.json")).resolve()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "parts": len(part_reports), "total_batch_cost": report["estimated_total_batch_cost"]}, ensure_ascii=False))
    print(report_path)
    raise SystemExit(0 if report["pass"] else 2)


if __name__ == "__main__":
    main()
