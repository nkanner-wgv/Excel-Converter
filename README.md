Excel Screenshot + Layout Reorder Tool
This is a reusable Streamlit app that takes:
a screenshot of your screen layout
an Excel file
and returns a new Excel file with the columns reordered to match the screenshot.
How it works
OCR reads text from the screenshot
text boxes are sorted left-to-right
detected labels are fuzzy-matched to your canonical layout names
the app lets you review / tweak the detected order
the Excel file is parsed and reordered
output includes:
reordered Excel file
JSON report
detected screenshot order
Best use case
This works best when the screenshot shows column labels clearly across one row.
Install
```bash
pip install -r requirements.txt
```
Run locally
```bash
streamlit run app/ui.py
```
Deploy to Render
Build command:
```bash
pip install -r requirements.txt
```
Start command:
```bash
streamlit run app/ui.py --server.port $PORT --server.address 0.0.0.0
```
Files to tune
`templates/aliases.json`
`templates/layout_order.json`
Notes
OCR is not perfect, so the UI includes a review box before generating output.
For your OE-style files, use `header mode = auto` or `two-row`.
