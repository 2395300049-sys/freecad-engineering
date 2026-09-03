import argparse
import json
import math
from pathlib import Path


EXTERNAL_TYPES = {"spur", "helical", "bevel", "hypoid"}


def bevel_cone_angles(teeth_driver, teeth_follower, shaft_angle_deg):
    shaft_angle = math.radians(shaft_angle_deg)
    ratio = teeth_follower / teeth_driver
    driver = math.atan2(math.sin(shaft_angle), ratio + math.cos(shaft_angle))
    follower = shaft_angle - driver
    return math.degrees(driver), math.degrees(follower)


def issue(issues, severity, code, message):
    issues.append({"severity": severity, "code": code, "message": message})


def main():
    parser = argparse.ArgumentParser(description="Validate gear-pair engineering parameters and motion results.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--angle-tolerance-deg", type=float, default=0.01)
    parser.add_argument("--ratio-tolerance", type=float, default=1e-6)
    parser.add_argument("--volume-tolerance-mm3", type=float, default=1e-5)
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    pair_reports = []
    for index, pair in enumerate(data.get("gear_pairs", [])):
        issues = []
        pair_id = pair.get("id", f"pair-{index + 1}")
        gear_type = str(pair.get("type", "")).lower()
        z1 = pair.get("teeth_driver")
        z2 = pair.get("teeth_follower")
        module = pair.get("module_mm")
        if not isinstance(z1, int) or z1 <= 0 or not isinstance(z2, int) or z2 <= 0:
            issue(issues, "blocking", "teeth", "Driver and follower tooth counts must be positive integers")
            theoretical_ratio = None
        else:
            sign = -1.0 if gear_type in EXTERNAL_TYPES else 1.0
            theoretical_ratio = sign * z2 / z1
            expected = pair.get("ratio_expected")
            if expected is None or abs(float(expected) - theoretical_ratio) > args.ratio_tolerance:
                issue(issues, "blocking", "ratio", f"Expected ratio {expected} does not match theoretical {theoretical_ratio}")
        if module is None or float(module) <= 0:
            issue(issues, "blocking", "module", "Module must be positive")
        pressure_angle = pair.get("pressure_angle_deg")
        if pressure_angle is None or not 0 < float(pressure_angle) < 45:
            issue(issues, "major", "pressure-angle", "Pressure angle must be explicitly defined and plausible")

        calculated_cones = None
        if gear_type == "bevel" and isinstance(z1, int) and z1 > 0 and isinstance(z2, int) and z2 > 0:
            shaft_angle = pair.get("shaft_angle_deg")
            if shaft_angle is None or not 0 < float(shaft_angle) < 180:
                issue(issues, "blocking", "shaft-angle", "Bevel gear shaft angle must be between 0 and 180 degrees")
            else:
                calculated_cones = bevel_cone_angles(z1, z2, float(shaft_angle))
                supplied_1 = pair.get("pitch_cone_driver_deg")
                supplied_2 = pair.get("pitch_cone_follower_deg")
                if supplied_1 is None or abs(float(supplied_1) - calculated_cones[0]) > args.angle_tolerance_deg:
                    issue(issues, "blocking", "driver-cone", f"Driver pitch-cone angle should be {calculated_cones[0]:.6f} deg")
                if supplied_2 is None or abs(float(supplied_2) - calculated_cones[1]) > args.angle_tolerance_deg:
                    issue(issues, "blocking", "follower-cone", f"Follower pitch-cone angle should be {calculated_cones[1]:.6f} deg")

        backlash_values = [pair.get("backlash_min_mm"), pair.get("backlash_nominal_mm"), pair.get("backlash_max_mm")]
        if any(value is None for value in backlash_values):
            issue(issues, "blocking", "backlash-missing", "Minimum, nominal, and maximum backlash are required")
        else:
            minimum, nominal, maximum = map(float, backlash_values)
            if minimum < 0 or not minimum <= nominal <= maximum:
                issue(issues, "blocking", "backlash-range", "Backlash must satisfy 0 <= min <= nominal <= max")

        motion = pair.get("motion_result")
        if not motion:
            issue(issues, "major", "motion-missing", "No sampled motion result supplied")
        else:
            if int(motion.get("sample_count", 0)) <= 0:
                issue(issues, "blocking", "sample-count", "Motion sample count must be positive")
            if not motion.get("full_required_cycle", False):
                issue(issues, "blocking", "cycle", "Full required motion cycle was not verified")
            common = float(motion.get("max_forbidden_common_volume_mm3", math.inf))
            if common > args.volume_tolerance_mm3:
                issue(issues, "blocking", "penetration", f"Forbidden common volume is {common} mm3")
            required_clearance = float(pair.get("minimum_forbidden_clearance_mm", 0.0))
            measured_clearance = float(motion.get("minimum_forbidden_clearance_mm", -math.inf))
            if measured_clearance < required_clearance:
                issue(issues, "blocking", "clearance", f"Measured clearance {measured_clearance} mm is below required {required_clearance} mm")

        blocking = sum(item["severity"] == "blocking" for item in issues)
        pair_reports.append(
            {
                "id": pair_id,
                "type": gear_type,
                "theoretical_ratio": theoretical_ratio,
                "calculated_pitch_cone_angles_deg": calculated_cones,
                "issues": issues,
                "pass": blocking == 0,
            }
        )

    report = {
        "input": str(input_path),
        "pair_count": len(pair_reports),
        "pairs": pair_reports,
        "pass": bool(pair_reports) and all(item["pass"] for item in pair_reports),
    }
    report_path = (args.report or input_path.with_name(input_path.stem + "_validation.json")).resolve()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "pairs": len(pair_reports)}, ensure_ascii=False))
    print(report_path)
    raise SystemExit(0 if report["pass"] else 2)


if __name__ == "__main__":
    main()
