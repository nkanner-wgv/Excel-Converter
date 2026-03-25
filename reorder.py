
import argparse
import pandas as pd
import json
from reorder import reorder_dataframe

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

df = pd.read_excel(args.input)

with open("templates/layout_order.json") as f:
    layout = json.load(f)

df2 = reorder_dataframe(df, layout)

df2.to_excel(args.output, index=False)

print("Finished. Output written:", args.output)
