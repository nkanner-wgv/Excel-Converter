from __future__ import annotations
from io import BytesIO
from typing import Dict, List, Tuple

import easyocr
import numpy as np
from PIL import Image
from rapidfuzz import fuzz

from utils import normalize, build_alias_lookup, unique_keep_order

_READER = None

def get_reader():
    global _READER
    if _READER is None:
        _READER = easyocr.Reader(["en"], gpu=False)
    return _READER

def extract_text_boxes(image_bytes: bytes) -> List[dict]:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    img_np = np.array(image)
    reader = get_reader()
    results = reader.readtext(img_np)
    boxes = []
    for box, text, confidence in results:
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        boxes.append({
            "text": str(text).strip(),
            "confidence": float(confidence),
            "x_min": min(xs),
            "x_max": max(xs),
            "y_min": min(ys),
            "y_max": max(ys),
            "x_center": sum(xs) / len(xs),
            "y_center": sum(ys) / len(ys),
        })
    return boxes

def _pick_top_header_row(boxes: List[dict]) -> List[dict]:
    good = [b for b in boxes if b["text"] and b["confidence"] >= 0.20]
    if not good:
        return []
    good = sorted(good, key=lambda b: (b["y_center"], b["x_center"]))
    y_values = [b["y_center"] for b in good]
    top_band = np.percentile(y_values, 45)
    row = [b for b in good if b["y_center"] <= top_band]
    row = sorted(row, key=lambda b: b["x_center"])
    return row

def _best_match(text: str, aliases: Dict[str, List[str]]) -> Tuple[str | None, int]:
    alias_lookup = build_alias_lookup(aliases)
    norm_text = normalize(text)
    if norm_text in alias_lookup:
        return alias_lookup[norm_text], 100

    best_name = None
    best_score = 0
    for canonical, values in aliases.items():
        candidates = [canonical] + values
        for candidate in candidates:
            score = fuzz.ratio(normalize(candidate), norm_text)
            if score > best_score:
                best_score = score
                best_name = canonical
    if best_score >= 70:
        return best_name, best_score
    return None, best_score

def detect_layout_from_screenshot(image_bytes: bytes, aliases: Dict[str, List[str]]) -> dict:
    boxes = extract_text_boxes(image_bytes)
    row = _pick_top_header_row(boxes)

    raw_texts = [b["text"] for b in row]
    mapped = []
    details = []
    for item in row:
        canonical, score = _best_match(item["text"], aliases)
        details.append({
            "raw_text": item["text"],
            "canonical_match": canonical,
            "score": score,
            "x_center": item["x_center"],
            "y_center": item["y_center"],
        })
        if canonical:
            mapped.append(canonical)

    mapped = unique_keep_order(mapped)
    return {
        "raw_detected_text_left_to_right": raw_texts,
        "detected_canonical_order": mapped,
        "details": details,
    }
