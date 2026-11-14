"""Reproducible transformations for the course building inventory."""
from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).parent / "building_inventory.csv.gz"
SOURCE_URL = "https://raw.githubusercontent.com/UIUC-iSchool-DataViz/is445_data/main/building_inventory.csv"


def load_inventory(path=DATA_PATH):
    raw = pd.read_csv(path)
    data = raw.rename(columns={
        "Agency Name": "agency", "Location Name": "location", "County": "county",
        "Bldg Status": "status", "Year Constructed": "year",
        "Square Footage": "area", "Usage Description": "usage",
    }).copy()
    for col in ["agency", "location", "county", "status", "usage"]:
        data[col] = data[col].astype("string").str.strip().fillna("Unknown")
        data[col] = data[col].replace("", "Unknown")
    for col in ["year", "area"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    valid_year = data.year.between(1, 2026) & data.year.eq(data.year.round())
    audit = {
        "source_rows": len(data), "excluded_years": int((~valid_year).sum()),
        "duplicate_rows": int(raw.duplicated().sum()),
        "excluded_area": int((~(data.area.gt(0) & data.area.lt(float("inf")))).sum()),
    }
    data = data.loc[valid_year].copy()
    data["year"] = data.year.astype(int)
    data["decade"] = data.year // 10 * 10
    return data, audit


def decade_summary(data, years, top_n):
    """Count records; zero-fill agency/decade combinations before percentages."""
    selected = data[data.year.between(*years)]
    order = (selected.groupby("agency").size().rename("total").reset_index()
             .sort_values(["total", "agency"], ascending=[False, True]).head(top_n))
    agencies = order.agency.tolist()
    decades = list(range(years[0] // 10 * 10, years[1] // 10 * 10 + 1, 10))
    grid = pd.MultiIndex.from_product([agencies, decades], names=["agency", "decade"])
    counts = (selected[selected.agency.isin(agencies)].groupby(["agency", "decade"])
              .size().reindex(grid, fill_value=0).rename("records").reset_index())
    counts["share"] = counts.records / counts.groupby("agency").records.transform("sum")
    counts["decade_label"] = counts.decade.astype(str) + "s"
    return counts, agencies, selected


def scatter_records(data, agency, years, area_range):
    return data.loc[
        data.agency.eq(agency) & data.year.between(*years)
        & data.area.gt(0) & data.area.between(*area_range)
    ].copy()
