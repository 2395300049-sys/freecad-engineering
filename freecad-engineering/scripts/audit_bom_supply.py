import argparse
import csv
import json
from datetime import date, datetime, timedelta
from pathlib import Path


def parse_date(value, field, issues, row_id):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        issues.append({"severity": "blocking", "item": row_id, "field": field, "message": "Date must use YYYY-MM-DD"})
        return None


def parse_number(value, field, issues, row_id, required=False):
    if value in (None, ""):
        if required:
            issues.append({"severity": "blocking", "item": row_id, "field": field, "message": "Required numeric value is missing"})
        return None
    try:
        return float(value)
    except ValueError:
        issues.append({"severity": "blocking", "item": row_id, "field": field, "message": "Invalid numeric value"})
        return None


def main():
    parser = argparse.ArgumentParser(description="Audit BOM sourcing, quote age, lead time, lifecycle, and alternates.")
    parser.add_argument("bom", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--max-quote-age-days", type=int, default=90)
    parser.add_argument("--max-lead-time-days", type=int)
    parser.add_argument("--require-alternate-for-critical", action="store_true")
    args = parser.parse_args()

    bom_path = args.bom.expanduser().resolve()
    as_of = datetime.strptime(args.as_of, "%Y-%m-%d").date()
    with bom_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    issues = []
    item_reports = []
    seen_items = set()
    for index, row in enumerate(rows, start=2):
        item = row.get("item_no") or f"row-{index}"
        if item in seen_items:
            issues.append({"severity": "blocking", "item": item, "field": "item_no", "message": "Duplicate BOM item number"})
        seen_items.add(item)
        make_buy = (row.get("make_buy") or "").strip().lower()
        if make_buy not in {"make", "buy"}:
            issues.append({"severity": "blocking", "item": item, "field": "make_buy", "message": "Expected make or buy"})
        quantity = parse_number(row.get("quantity"), "quantity", issues, item, required=True)
        if quantity is not None and quantity <= 0:
            issues.append({"severity": "blocking", "item": item, "field": "quantity", "message": "Quantity must be positive"})

        quote_date = parse_date(row.get("quote_date"), "quote_date", issues, item)
        required_date = parse_date(row.get("required_date"), "required_date", issues, item)
        lead_time = parse_number(row.get("lead_time_days"), "lead_time_days", issues, item, required=make_buy == "buy")
        quote_age = (as_of - quote_date).days if quote_date else None
        projected_delivery = as_of + timedelta(days=lead_time) if lead_time is not None else None

        if make_buy == "buy":
            for field in ("manufacturer", "manufacturer_part_number", "supplier", "currency", "stock_status", "lifecycle_status", "source_url"):
                if not (row.get(field) or "").strip():
                    issues.append({"severity": "blocking", "item": item, "field": field, "message": "Purchased item field is required"})
            parse_number(row.get("unit_price"), "unit_price", issues, item, required=True)
            parse_number(row.get("minimum_order_qty"), "minimum_order_qty", issues, item, required=True)
            if quote_date is None:
                issues.append({"severity": "blocking", "item": item, "field": "quote_date", "message": "Purchased item requires a dated quotation or source check"})
            elif quote_age < 0:
                issues.append({"severity": "blocking", "item": item, "field": "quote_date", "message": "Quote/source date is later than the audit date"})
            elif quote_age > args.max_quote_age_days:
                issues.append({"severity": "major", "item": item, "field": "quote_date", "message": f"Quote/source data are {quote_age} days old"})
            if args.max_lead_time_days is not None and lead_time is not None and lead_time > args.max_lead_time_days:
                issues.append({"severity": "blocking", "item": item, "field": "lead_time_days", "message": "Lead time exceeds project threshold"})
            if required_date and projected_delivery and projected_delivery > required_date:
                issues.append({"severity": "blocking", "item": item, "field": "required_date", "message": f"Projected delivery {projected_delivery} misses required date"})
            if required_date and required_date < as_of:
                issues.append({"severity": "blocking", "item": item, "field": "required_date", "message": "Required date is already past"})
            lifecycle = (row.get("lifecycle_status") or "").lower()
            if lifecycle in {"obsolete", "discontinued", "last-time-buy", "eol"}:
                issues.append({"severity": "blocking", "item": item, "field": "lifecycle_status", "message": f"Lifecycle status is {lifecycle}"})
            critical = (row.get("criticality") or "").lower() in {"critical", "safety-critical", "schedule-critical"}
            if critical and not (row.get("alternate_part_number") or "").strip():
                severity = "blocking" if args.require_alternate_for_critical else "major"
                issues.append({"severity": severity, "item": item, "field": "alternate_part_number", "message": "Critical purchased item has no approved alternate"})

        item_reports.append(
            {
                "item_no": item,
                "part_number": row.get("part_number"),
                "make_buy": make_buy,
                "quote_age_days": quote_age,
                "lead_time_days": lead_time,
                "projected_delivery": projected_delivery.isoformat() if projected_delivery else None,
                "required_date": required_date.isoformat() if required_date else None,
            }
        )

    blocking = sum(item["severity"] == "blocking" for item in issues)
    major = sum(item["severity"] == "major" for item in issues)
    report = {
        "bom": str(bom_path),
        "as_of": as_of.isoformat(),
        "item_count": len(rows),
        "items": item_reports,
        "issues": issues,
        "summary": {"blocking": blocking, "major": major, "pass": blocking == 0, "conditional": blocking == 0 and major > 0},
    }
    report_path = (args.report or bom_path.with_name(bom_path.stem + "_supply_audit.json")).resolve()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    print(report_path)
    raise SystemExit(0 if report["summary"]["pass"] else 2)


if __name__ == "__main__":
    main()
