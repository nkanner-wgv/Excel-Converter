# Excel Layout Reorder Tool

Tool to reorder Excel columns to match a saved UI layout.

## Problem this solves
Manufacturing / postal layout screens have a fixed column order.
Excel extracts often come out in random order.
This tool normalizes headers and reorders columns automatically.

## Run locally

pip install -r requirements.txt

python app/main.py --input samples/sample_input.xlsx --output output.xlsx

## How ordering works
Column order is stored in:
templates/layout_order.json

Update that file any time the UI layout changes.

## Roadmap
- multi‑sheet support
- screenshot layout reader
- simple upload UI
