from __future__ import annotations
import argparse
import json
from pathlib import Path

from parser import parse_excel
from reorder import reorder_dataframe
from screenshot_layout import detect_layout_from_screenshot

def main() -> None:
    parser = argparse.ArgumentParser(description="Reorder Excel columns based on a screenshot layout.")
    parser.add_argument("--input-excel", required=True)
    parser.add_argument("--input-screenshot", required=True)
    parser.add_argument("--output-excel", required=True)
    parser.add_argument("--sheet", default=0)
    parser.add_argument("--header-mode", default="auto", choices=["auto", "single", "two-row"])
    parser.add_argument("--layout-file", default="templates/layout_order.json")
    parser.add_argument("--aliases-file", default="templates/aliases.json")
    parser.add_argument("--report-file", default=None)
    args = parser.parse_args()

    aliases = json.loads(Path(args.aliases_file).read_text(encoding="utf-8"))
    fallback_layout = json.loads(Path(args.layout_file).read_text(encoding="utf-8"))

    screenshot_bytes = Path(args.input_screenshot).read_bytes()
    screenshot_report = detect_layout_from_screenshot(screenshot_bytes, aliases)
    desired_order = screenshot_report["detected_canonical_order"] or fallback_layout

    sheet = int(args.sheet) if str(args.sheet).isdigit() else args.sheet
    df = parse_excel(args.input_excel, header_mode=args.header_mode, sheet_name=sheet)
    reordered_df, reorder_report = reorder_dataframe(df, desired_order, aliases)

    output_path = Path(args.output_excel)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    reordered_df.to_excel(output_path, index=False)

    report = {
        "screenshot_report": screenshot_report,
        "reorder_report": reorder_report,
    }
    report_path = Path(args.report_file) if args.report_file else output_path.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Done. Wrote reordered file to: {output_path}")
    print(f"Done. Wrote report to: {report_path}")

if __name__ == "__main__":
    main()
