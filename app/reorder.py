from __future__ import annotations
from typing import Dict, List, Tuple
import pandas as pd
from utils import normalize, build_alias_lookup

def canonicalize_columns(columns: List[str], aliases: Dict[str, List[str]]) -> Tuple[Dict[str, str], Dict[str, str]]:
    alias_lookup = build_alias_lookup(aliases)
    canonical_to_actual: Dict[str, str] = {}
    actual_to_canonical: Dict[str, str] = {}

    for col in columns:
        col = str(col)
        norm_col = normalize(col)
        canonical = alias_lookup.get(norm_col)
        if canonical:
            if canonical not in canonical_to_actual:
                canonical_to_actual[canonical] = col
            actual_to_canonical[col] = canonical

    return canonical_to_actual, actual_to_canonical

def reorder_dataframe(df: pd.DataFrame, desired_order: List[str], aliases: Dict[str, List[str]]) -> tuple[pd.DataFrame, dict]:
    actual_columns = [str(c) for c in df.columns]
    canonical_to_actual, actual_to_canonical = canonicalize_columns(actual_columns, aliases)

    matched_actual = []
    missing = []

    for desired in desired_order:
        if desired in canonical_to_actual:
            matched_actual.append(canonical_to_actual[desired])
        else:
            missing.append(desired)

    extras = [col for col in actual_columns if col not in matched_actual]
    final_order = matched_actual + extras

    report = {
        "desired_order_used": desired_order,
        "matched_columns_in_output_order": matched_actual,
        "missing_from_file": missing,
        "extra_columns_appended_to_end": extras,
        "canonical_mapping_used": actual_to_canonical,
    }
    return df[final_order], report
