# Built over time — IS 445 HW6

Two interactive Altair visualizations of the same Illinois building inventory dataset, presented in a Streamlit report by Zijian Chen.

## Run locally

Use Python 3.12, then run from this directory:

```sh
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

## Deploy on Streamlit Community Cloud

Use the public repository `zijianc2/is445-hw6-streamlit`, branch `main`, entry point `streamlit_app.py`, and Python 3.12 in Advanced settings. Make the app public. No secrets or external runtime data requests are required; the source CSV is bundled using lossless gzip compression.

## Visualizations and interactions

1. **Agency × construction-decade heatmap.** Filter construction years, choose the top 5/8/12/15 agencies, and switch between record counts and shares within each agency. Agencies are ranked within the chosen years; the percentage denominator is the agency's records in that same interval. Missing agency–decade combinations are filled with zero. Partial boundary decades are labeled in the caption.
2. **Construction year × floor area scatterplot.** Select an agency, filter years and floor area, and toggle logarithmic versus linear area scales. Status is encoded categorically. Exact year/area/status overlaps are grouped, with record multiplicity in the tooltip. The median remains calculated from all matching source records.

Both charts have independent filters and explicit empty-result messages. The report includes one detailed interpretation/design/future-work paragraph per chart and a separate HW5 overlap statement.

## Source and preparation

- Source: <https://raw.githubusercontent.com/UIUC-iSchool-DataViz/is445_data/main/building_inventory.csv>
- Snapshot downloaded: November 13, 2026.
- File: `building_inventory.csv.gz` (losslessly compressed original CSV, preserving all original columns and rows).
- SHA-256 of the decompressed original: `c9d95a9fbb98e3b1423939a3beea182c263f496ddef372117bb882afe9784272`.
- 8,862 original rows; 289 unusable construction years; 8,573 records with valid construction years (1753–2019).
- Positive finite floor area is required only for the scatterplot. There are 57 zero-area records in the original source; year and area exclusions may overlap.
- Text categories are stripped of whitespace and numeric fields explicitly parsed.
- The 1,925 exact duplicate rows are retained because the file lacks a reliable unique building ID. Counts describe inventory records, not confirmed distinct buildings. The data are a snapshot and should not be interpreted as current conditions or a complete history of construction.

## Relationship to HW5

HW5: <https://zijianc2.github.io/hw5/>, using BFRO reports, a top-state horizontal bar chart, and a state-filtered monthly bar chart.

HW6 uses a different data source (building inventory), different variables, and different chart types (heatmap and scatterplot). No HW5 text, chart specifications, or analysis code is copied. Shared programming tools are Python and Altair. This supports the rubric's two extra-credit criteria; grading remains the instructional team's decision.

## Verification

```sh
python -m unittest -v test_app.py
```

Tests check retained-row counts, heatmap totals and percentage denominators, range filtering, both rendered charts, control changes, empty states, and recovery after an empty result.

## Submission

PrairieLearn asks for two URLs: the publicly accessible deployed Streamlit app and this public GitHub repository. The full report and both write-ups are inside the app. Check the deployed app after pushing changes.
