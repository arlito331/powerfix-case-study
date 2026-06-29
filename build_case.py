#!/usr/bin/env python3
"""
build_case.py  —  turn a case-data file into the finished PDF.

Usage:
    python3 build_case.py case_guatemala.py
    python3 build_case.py case_peru.py

Output lands in ./output/PowerFix_CaseStudy<N>_<Country>.pdf
"""
import sys, os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from powerfix_engine import compute
from powerfix_render import render


def load_case(path):
    spec = importlib.util.spec_from_file_location("case_data", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CASE


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 build_case.py <case_data_file.py>")
        sys.exit(1)
    case_path = sys.argv[1]
    inp = load_case(case_path)
    res = compute(inp)

    # console summary so you can sanity-check the math before sending
    print("=" * 56)
    print("  PowerFix Case Study #%d  \u2014  %s" % (inp.case_number, inp.country))
    print("=" * 56)
    print("  Pothole (1 box):     %.2f m2" % res.pothole_m2)
    print("  Cut zone (%d\u00d7):       %.2f m2" % (int(res.cut_multiplier), res.cut_zone_m2))
    print("  Gov rate:            US$%.2f/m2" % res.gov_rate_per_m2_usd)
    print("  Conventional total:  US$%.2f" % res.conventional_total_usd)
    print("  PowerPatch box:      US$%.2f  %s" % (
        res.powerpatch_box_usd,
        "(BACK-CALCULATED \u2014 value-positioned)" if res.box_is_backcalculated else "(confirmed price)"))
    print("  Savings:             US$%.2f  (%.1f%%)" % (res.savings_usd, res.savings_pct))
    print("  Speed:               %d\u00d7 faster" % res.speed_multiple)
    print("=" * 56)

    out_dir = os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)
    safe_country = inp.country.replace(" ", "_")
    out_path = os.path.join(out_dir, "PowerFix_CaseStudy%d_%s.pdf" % (inp.case_number, safe_country))
    render(inp, res, out_path)
    print("  \u2713 PDF written to: %s" % out_path)
    return out_path


if __name__ == "__main__":
    main()
