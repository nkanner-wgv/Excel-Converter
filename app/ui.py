from __future__ import annotations
import json
import tempfile
from pathlib import Path

import streamlit as st

from parser import parse_excel
from reorder import reorder_dataframe
from screenshot_layout import detect_layout_from_screenshot

st.set_page_config(page_title="Screenshot to Excel Reorder", layout="wide")
st.title("Screenshot + Excel → Reordered Excel")
st.write("Upload your layout screenshot and your Excel file. The app will detect the left-to-right order from the screenshot and build a new Excel file in that order.")

layout_file = Path("templates/layout_order.json")
aliases_file = Path("templates/aliases.json")
fallback_layout = json.loads(layout_file.read_text(encoding="utf-8"))
aliases = json.loads(aliases_file.read_text(encoding="utf-8"))

header_mode = st.selectbox("Header mode", ["auto", "single", "two-row"], index=0)
screenshot_file = st.file_uploader("Upload screenshot", type=["png", "jpg", "jpeg"])
excel_file = st.file_uploader("Upload Excel file", type=["xlsx", "xlsm", "xls"])

if screenshot_file and excel_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        screenshot_path = tmpdir / screenshot_file.name
        excel_path = tmpdir / excel_file.name
        screenshot_bytes = screenshot_file.read()
        screenshot_path.write_bytes(screenshot_bytes)
        excel_path.write_bytes(excel_file.read())

        try:
            detection = detect_layout_from_screenshot(screenshot_bytes, aliases)
            detected_order = detection["detected_canonical_order"] or fallback_layout

            st.subheader("1) Screenshot detection")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(screenshot_bytes, caption="Uploaded screenshot", use_container_width=True)
            with col2:
                st.write("Detected raw text left to right:")
                st.write(detection["raw_detected_text_left_to_right"])
                st.write("Detected canonical order:")
                st.write(detected_order)

            editable_order = st.text_area(
                "2) Review / edit the order before output",
                value="\n".join(detected_order),
                height=260,
                help="One column name per line. You can edit this if OCR missed something."
            )

            final_order = [line.strip() for line in editable_order.splitlines() if line.strip()]

            if st.button("Build reordered Excel"):
                df = parse_excel(str(excel_path), header_mode=header_mode)
                reordered_df, reorder_report = reorder_dataframe(df, final_order, aliases)

                output_path = tmpdir / f"{excel_path.stem}_reordered.xlsx"
                report_path = tmpdir / f"{excel_path.stem}_report.json"
                screenshot_order_path = tmpdir / f"{excel_path.stem}_detected_order.json"

                reordered_df.to_excel(output_path, index=False)
                report = {
                    "screenshot_report": detection,
                    "reorder_report": reorder_report,
                }
                report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                screenshot_order_path.write_text(json.dumps({"final_order_used": final_order}, indent=2), encoding="utf-8")

                st.success("Done.")
                st.subheader("3) Preview")
                st.dataframe(reordered_df.head(20), use_container_width=True)

                a, b, c = st.columns(3)
                with a:
                    st.download_button(
                        "Download reordered Excel",
                        data=output_path.read_bytes(),
                        file_name=output_path.name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                with b:
                    st.download_button(
                        "Download full JSON report",
                        data=report_path.read_bytes(),
                        file_name=report_path.name,
                        mime="application/json",
                    )
                with c:
                    st.download_button(
                        "Download final order used",
                        data=screenshot_order_path.read_bytes(),
                        file_name=screenshot_order_path.name,
                        mime="application/json",
                    )

                with st.expander("View OCR / match details"):
                    st.json(detection)
                with st.expander("View reorder report"):
                    st.json(reorder_report)

        except Exception as e:
            st.error(f"Error: {e}")
