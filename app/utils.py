from __future__ import annotations
import re
from typing import Dict, List

def normalize(text: object) -> str:
    text = str(text).strip().lower()
    text = text.replace("&", "and")
    text = re.sub(r"[^a-z0-9]+", "", text)
    return text

def build_alias_lookup(aliases: Dict[str, List[str]]) -> Dict[str, str]:
    lookup: Dict[str, str] = {}
    for canonical, values in aliases.items():
        lookup[normalize(canonical)] = canonical
        for value in values:
            lookup[normalize(value)] = canonical
    return lookup

def unique_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
