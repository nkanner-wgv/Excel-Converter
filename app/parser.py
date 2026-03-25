from __future__ import annotations
import pandas as pd

def _clean_piece(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()

def parse_single_row_excel(input_path: str, sheet_name=0) -> pd.DataFrame:
    return pd.read_excel(input_path, sheet_name=sheet_name)

def parse_two_row_excel(input_path: str, sheet_name=0) -> pd.DataFrame:
    raw = pd.read_excel(input_path, header=None, sheet_name=sheet_name)
    if len(raw) < 3:
        raise ValueError("File does not appear to have enough rows for two-row header parsing.")
    header_row_1 = raw.iloc[1].tolist()
    header_row_2 = raw.iloc[2].tolist()
    combined_headers = []
    for a, b in zip(header_row_1, header_row_2):
        a = _clean_piece(a)
        b = _clean_piece(b)
        combined = f"{a} {b}".strip()
        combined_headers.append(combined if combined else "Unnamed")
    data = raw.iloc[3:].copy()
    data.columns = combined_headers
    data = data.reset_index(drop=True)
    return data

def looks_like_bad_single_row_header(df: pd.DataFrame) -> bool:
    headers = list(df.columns)
    unnamed_count = sum(1 for c in headers if str(c).startswith("Unnamed"))
    numeric_count = sum(1 for c in headers if isinstance(c, (int, float)))
    return unnamed_count >= max(3, len(headers) // 4) or numeric_count >= 2

def parse_excel(input_path: str, header_mode: str = "auto", sheet_name=0) -> pd.DataFrame:
    header_mode = header_mode.lower()
    if header_mode == "single":
        return parse_single_row_excel(input_path, sheet_name=sheet_name)
    if header_mode == "two-row":
        return parse_two_row_excel(input_path, sheet_name=sheet_name)
    if header_mode == "auto":
        single = parse_single_row_excel(input_path, sheet_name=sheet_name)
        if looks_like_bad_single_row_header(single):
            return parse_two_row_excel(input_path, sheet_name=sheet_name)
        return single
    raise ValueError("header_mode must be one of: single, two-row, auto")
