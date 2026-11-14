"""IS 445 HW6: two interactive views of Illinois building inventory records."""
import altair as alt
import streamlit as st

from data_utils import load_inventory, decade_summary, scatter_records, SOURCE_URL

st.set_page_config(page_title="Built over time | IS 445 HW6", page_icon="🏛️", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 2.5rem; padding-bottom: 3rem;}
h1 {letter-spacing: -0.04em;}
div[data-testid="stMetric"] {border-top: 3px solid #157f78; padding-top: .7rem;}
div[data-testid="stCaptionContainer"] {color: #536675;}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def cached_inventory():
    return load_inventory()


def finish_chart(chart):
    return (chart.configure_view(stroke=None)
            .configure_axis(labelFontSize=12, titleFontSize=13, gridColor="#e7edf0")
            .configure_legend(labelFontSize=12, titleFontSize=13))


try:
    data, audit = cached_inventory()
except (OSError, ValueError) as error:
    st.error(f"The inventory could not be loaded: {error}")
    st.stop()

st.caption("IS 445 · HOMEWORK 6 · ZIJIAN CHEN")
st.title("Built over time")
st.markdown("### Exploring Illinois' public building inventory")
st.write("When were the buildings in this inventory constructed, and how does building size vary across construction years? Explore two views of the same course dataset.")
st.caption("An inventory snapshot, not a current census or a historical record of every building ever constructed. Counts refer to source records, not verified unique buildings.")
c1, c2, c3 = st.columns(3)
c1.metric("Inventory records", f"{audit['source_rows']:,}")
c2.metric("Records with a usable year", f"{len(data):,}")
c3.metric("Construction years", f"{data.year.min()}–{data.year.max()}")
st.markdown(f"[Course dataset]({SOURCE_URL}) · [Source code](https://github.com/zijianc2/is445-hw6-streamlit) · [Previous HW5](https://zijianc2.github.io/hw5/)")

st.divider()
st.subheader("01 / When did each agency's inventory take shape?")
st.write("Compare construction decades across agencies. Switch to within-agency shares to compare timing without letting the largest inventories dominate.")
col1, col2, col3 = st.columns([2, 1, 1.5])
with col1:
    heat_years = st.slider("Construction-year range · heatmap", int(data.year.min()), int(data.year.max()), (1900, int(data.year.max())), key="heat_years")
with col2:
    top_n = st.selectbox("Number of agencies", [5, 8, 12, 15], index=1, key="top_n")
with col3:
    heat_metric = st.radio("Color represents", ["Share within agency", "Record count"], key="heat_metric")
summary, agency_order, heat_selected = decade_summary(data, heat_years, top_n)
if summary.empty:
    st.info("No records have a construction year in this range. Widen the range to display the heatmap.")
else:
    fraction = heat_metric == "Share within agency"
    color = alt.Color(
        "share:Q" if fraction else "records:Q",
        title="Share within agency" if fraction else "Records",
        scale=alt.Scale(scheme="tealblues", domain=[0, 1] if fraction else [0, int(summary.records.max())]),
        legend=alt.Legend(format=".0%" if fraction else ",d", orient="bottom"),
    )
    heatmap = (alt.Chart(summary).mark_rect(stroke="white", strokeWidth=1).encode(
        x=alt.X("decade_label:O", title="Construction decade", sort=summary.decade_label.drop_duplicates().tolist(), axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("agency:N", title=None, sort=agency_order, axis=alt.Axis(labelLimit=320, labelOverlap=False)),
        color=color,
        tooltip=[alt.Tooltip("agency:N", title="Agency"), alt.Tooltip("decade_label:O", title="Decade"),
                 alt.Tooltip("records:Q", title="Records", format=",d"), alt.Tooltip("share:Q", title="Within-agency share", format=".1%")],
    ).properties(height=38 * len(agency_order)))
    st.altair_chart(finish_chart(heatmap), width="stretch", height=38 * len(agency_order) + 140, key="heatmap")
    st.caption(f"{int(summary.records.sum()):,} records across the top {len(agency_order)} agencies in {heat_years[0]}–{heat_years[1]}. Agencies are ranked by record count within this range. Shares sum to 100% within each displayed agency. Boundary decades may be partial; blank-looking pale cells represent zero records.")
    peak = summary.loc[summary.records.idxmax()]
    st.write(f"**In this selection:** the largest agency–decade count is **{int(peak.records):,} records** for **{peak.agency}** in the **{peak.decade_label}**.")

st.markdown("**Plot 1 · Interpretation and design**")
st.write("This heatmap highlights how the construction dates of inventory records are distributed across agencies and decades. Each rectangular mark represents one agency–decade combination: agency is nominal, decade is ordered, and the color value is quantitative. The default view uses the share of each agency's selected records, with a fixed 0–100% sequential teal scale, so a small agency can be compared with a large one without treating raw volume as timing. The count option answers a different question about absolute inventory size and uses a zero-based scale that updates with the selection. I group usable construction years into decades, explicitly fill missing combinations with zero, and rank agencies by their counts in the selected year range. The year slider, agency-count selector, and metric switch recompute the visualization rather than merely changing tooltips or zoom. These are dates of records still present in this snapshot, so a prominent decade does not establish an agency's complete historical construction activity. With more time, I would add searchable agency selection and compare several inventory snapshots to distinguish surviving buildings from later additions or removals.")

st.divider()
st.subheader("02 / Are newer inventory records associated with larger buildings?")
st.write("Inspect individual records within one agency. Narrow the construction years or area range, and compare a logarithmic scale with a linear scale.")
col1, col2 = st.columns([1.3, 2])
agencies = sorted(data.agency.unique().tolist())
with col1:
    agency = st.selectbox("Agency", agencies, index=agencies.index("University of Illinois"), key="agency")
with col2:
    scatter_years = st.slider("Construction-year range · scatterplot", int(data.year.min()), int(data.year.max()), (1900, int(data.year.max())), key="scatter_years")
positive = data.loc[data.agency.eq(agency) & data.area.gt(0) & data.area.lt(float("inf")), "area"]
col1, col2 = st.columns([3, 1])
max_area = max(1, int(positive.max())) if not positive.empty else 1
with col1:
    area_range = st.slider("Floor-area range (square feet)", 0, max_area, (0, max_area), key=f"area_{agency}")
with col2:
    log_scale = st.toggle("Logarithmic area axis", value=True, key="log_scale")
points = scatter_records(data, agency, scatter_years, area_range)
if points.empty:
    st.info("No records match these filters. Widen the year or area range, or choose another agency.")
else:
    # Aggregation preserves every source row in the count while avoiding hidden exact overlaps.
    plotted = (points.groupby(["year", "area", "status"], dropna=False).size()
               .rename("records").reset_index())
    scatter = (alt.Chart(plotted).mark_circle(size=65, opacity=.55, stroke="white", strokeWidth=.4).encode(
        x=alt.X("year:Q", title="Year constructed", scale=alt.Scale(zero=False, domain=list(scatter_years) if scatter_years[0] != scatter_years[1] else [scatter_years[0] - 1, scatter_years[1] + 1]), axis=alt.Axis(format="d")),
        y=alt.Y("area:Q", title="Floor area (sq ft)" + (" · log scale" if log_scale else ""), scale=alt.Scale(type="log" if log_scale else "linear", zero=not log_scale), axis=alt.Axis(format=",.0f")),
        color=alt.Color("status:N", title="Recorded status", scale=alt.Scale(domain=["In Use", "Abandon", "In Progress"], range=["#147d92", "#c16b31", "#7865b3"]), legend=alt.Legend(orient="bottom")),
        tooltip=[alt.Tooltip("year:Q", title="Year", format="d"), alt.Tooltip("area:Q", title="Area (sq ft)", format=",.0f"),
                 alt.Tooltip("status:N", title="Recorded status"), alt.Tooltip("records:Q", title="Records at this point", format=",d")],
    ).properties(height=380))
    st.altair_chart(finish_chart(scatter), width="stretch", height=480, key="scatterplot")
    st.caption(f"{len(points):,} records shown as {len(plotted):,} distinct year–area–status points. Exact coordinate overlaps are combined; hover to see their record count. Zero or invalid areas are excluded. Recorded status belongs to this dataset snapshot.")
    st.write(f"**In this selection:** the median floor area is **{points.area.median():,.0f} sq ft** across **{len(points):,} records**. This descriptive comparison does not establish that construction year causes building size.")

st.markdown("**Plot 2 · Interpretation and design**")
st.write("This scatterplot highlights the spread of recorded floor areas across construction years within a selected agency, including unusually large records and differences between construction periods. Year and area are quantitative encodings on the horizontal and vertical axes. Equal-sized circular marks prevent large floor areas from receiving an additional size encoding, and the default logarithmic vertical scale makes multiplicative differences visible across several orders of magnitude; the toggle offers a zero-based linear view when absolute differences matter more. Status is nominal and uses three distinct colors rather than an ordered gradient, while partial transparency reduces overplotting. I exclude records without a usable year or a positive area and combine exact year–area–status overlaps, exposing their record counts in tooltips without claiming that they are unique buildings. The agency dropdown and year and area sliders change the subset being plotted; these interactions help compare an agency's small facilities with its largest buildings. A visible association can also reflect facility use, agency composition, or which buildings remain in the inventory. With more time, I would add use-category facets and linked record details to investigate outliers and better separate these explanations.")

st.divider()
st.subheader("Data notes and relationship to HW5")
st.markdown("**HW5 overlap statement.** HW5 used BFRO Bigfoot reports: a horizontal bar chart of the ten states with the most reports and a state-filtered monthly bar chart. HW6 uses the Illinois building inventory from a different source. Plot 1 is an agency-by-construction-decade heatmap; Plot 2 is a construction-year versus floor-area scatterplot. Both plot types and their variables differ from HW5. No HW5 plot specifications, analysis code, or write-up text are reused; the shared tools are Python and Altair. The two paragraphs above were written for these new visualizations.")
with st.expander("Data preparation, provenance, and limitations"):
    st.write(f"The bundled compressed CSV is an unchanged snapshot of the course file downloaded on November 13, 2026. It contains {audit['source_rows']:,} rows. Numeric year and area fields are parsed explicitly; text categories are trimmed. Both plots exclude {audit['excluded_years']:,} records whose construction year is missing, non-integer, zero, negative, or beyond 2026. Across the full source, {audit['excluded_area']:,} records have a nonpositive or invalid area; these are excluded from the scatterplot only, and exclusions can overlap.")
    st.write(f"The source contains {audit['duplicate_rows']:,} exact duplicate rows, but no reliable unique building identifier. I retain all rows: identical descriptions can represent separate structures, so deduplicating would assert something the data cannot establish. Consequently, all counts and the median are record-based. The heatmap is limited to the selected top agencies, and its percentages use each agency's records within the selected years as the denominator. Neither plot implies completeness, current status, or population-normalized comparisons.")
    st.markdown(f"Source: [UIUC iSchool DataViz course repository]({SOURCE_URL}). The original columns are preserved in `building_inventory.csv.gz`; the file hash and reproducibility instructions are in the repository README.")
st.caption("IS 445 · Fall 2026 · Built with Streamlit and Altair")
