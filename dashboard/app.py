"""AIR IQ interactive Streamlit dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis import (  # noqa: E402
    aqi_category_counts,
    city_aqi_summary,
    missing_data_summary,
    monthly_aqi_trend,
    pollutant_summary,
)
from src.data_cleaning import DEFAULT_INPUT, load_and_clean_data  # noqa: E402
from src.visualizations import (  # noqa: E402
    aqi_distribution_chart,
    category_chart,
    city_comparison_chart,
    correlation_heatmap,
    monthly_trend_chart,
    pollutant_means_chart,
    pm_scatter_chart,
    seasonal_chart,
    yearly_trend_chart,
)

st.set_page_config(
    page_title="AIR IQ | India Air Quality Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("""
<style>
.stApp {
    background-color: #F1F5F9;
    color: #1E293B;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background-color: #172554;
}

[data-testid="stSidebar"] * {
    color: white;
}

.main .block-container {
    padding-top: 2rem;
}

h1, h2, h3, h4, p, label {
    color: #1E293B;
}

.hero {
    padding: 1.8rem;
    border-radius: 18px;
    color: white;
    background: linear-gradient(120deg, #064E3B, #059669, #0EA5E9);
    margin-bottom: 1.5rem;
}

.hero h1, .hero p {
    color: white !important;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #CBD5E1;
    padding: 1.2rem;
    border-radius: 14px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.05);
}

[data-testid="stMetricLabel"] {
    color: #475569 !important;
}

[data-testid="stMetricValue"] {
    color: #047857 !important;
}

.stTabs [data-baseweb="tab"] {
    color: #334155;
}

</style>
""", unsafe_allow_html=True)
st.caption(
    "Explore historical observations from the selected dataset. "
    "These records do not represent current air quality."
)

with st.sidebar:
    st.header("Explore the data")
    dataset_path = st.text_input("Dataset CSV path", value=str(DEFAULT_INPUT))
    st.caption("Expected: data/raw/city_day.csv")

try:
    data, cleaning_report = load_and_clean_data(dataset_path)
except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.warning(str(error))
    st.info(
        "Download the original city_day.csv from Kaggle and place it at "
        "`data/raw/city_day.csv`, then refresh this page."
    )
    st.markdown("### About AIR IQ")
    st.write(
        "AIR IQ is an academic data-science project for exploring historical "
        "air-quality measurements across Indian cities."
    )
    st.markdown(
        "[Open the project README](../README.md) · "
        "[Kaggle dataset](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india)"
    )
    st.stop()

st.sidebar.success(f"Loaded {len(data):,} cleaned rows")
st.sidebar.caption(
    f"Exact duplicate rows removed: {cleaning_report.exact_duplicates_removed:,}"
)

cities = sorted(data["City"].dropna().unique().tolist())
selected_cities = st.sidebar.multiselect("Cities", cities, default=cities)
filtered = data.loc[data["City"].isin(selected_cities)].copy()

if "Date" in filtered.columns and filtered["Date"].notna().any():
    min_date = filtered["Date"].min().date()
    max_date = filtered["Date"].max().date()
    date_range = st.sidebar.date_input(
        "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        filtered = filtered.loc[filtered["Date"].between(start, end)]

available_years = (
    sorted(filtered["Date"].dropna().dt.year.unique().tolist())
    if "Date" in filtered.columns
    else []
)
if available_years:
    selected_years = st.sidebar.multiselect(
        "Years", available_years, default=available_years
    )
    filtered = filtered.loc[filtered["Date"].dt.year.isin(selected_years)]

st.subheader("Project overview")
st.write(
    "AIR IQ examines air-quality measurements, compares city-level patterns, "
    "and visualizes changes over time using the Kaggle India Air Quality dataset."
)
aqi_values = filtered["AQI"].dropna() if "AQI" in filtered.columns else pd.Series(dtype=float)
metrics = st.columns(4)
metrics[0].metric("Cities in selection", f"{filtered['City'].nunique():,}")
metrics[1].metric("Available observations", f"{len(filtered):,}")
metrics[2].metric("Mean AQI", f"{aqi_values.mean():,.1f}" if not aqi_values.empty else "N/A")
metrics[3].metric("Highest recorded AQI", f"{aqi_values.max():,.0f}" if not aqi_values.empty else "N/A")

tab_overview, tab_cities, tab_trends, tab_pollutants, tab_data = st.tabs(
    ["Overview", "City comparison", "Trends", "Pollutants", "Data & methodology"]
)

with tab_overview:
    left, right = st.columns(2)
    with left:
        st.plotly_chart(aqi_distribution_chart(filtered), use_container_width=True)
    with right:
        st.plotly_chart(category_chart(filtered), use_container_width=True)
    st.plotly_chart(monthly_trend_chart(filtered), use_container_width=True)

    if not aqi_values.empty:
        city_means = city_aqi_summary(filtered)
        if not city_means.empty:
            highest = city_means.iloc[0]
            lowest = city_means.iloc[-1]
            st.markdown("#### Key findings for the current selection")
            st.write(
                f"- Highest city mean AQI in this selection: **{highest['City']}** "
                f"({highest['mean']:.1f}; {int(highest['count'])} available AQI observations)."
            )
            st.write(
                f"- Lowest city mean AQI in this selection: **{lowest['City']}** "
                f"({lowest['mean']:.1f}; {int(lowest['count'])} available AQI observations)."
            )
            monthly = monthly_aqi_trend(filtered)
            st.write(
                f"- The filtered data contains **{len(monthly)} months** with AQI values. "
                "Monthly averages may reflect changes in which cities reported data."
            )
    else:
        st.info("No non-missing AQI measurements are available for this selection.")

with tab_cities:
    city_top_n = st.slider("Cities to display", min_value=5, max_value=50, value=20, step=5)
    st.plotly_chart(
        city_comparison_chart(filtered, top_n=city_top_n),
        use_container_width=True,
    )
    st.dataframe(city_aqi_summary(filtered), use_container_width=True, hide_index=True)

with tab_trends:
    st.plotly_chart(yearly_trend_chart(filtered), use_container_width=True)
    st.plotly_chart(seasonal_chart(filtered), use_container_width=True)
    st.caption(
        "Broad calendar grouping used: Winter (Dec–Feb), Summer (Mar–May), "
        "Monsoon (Jun–Sep), and Post-monsoon (Oct–Nov). These are descriptive "
        "groups, not city-specific climate classifications."
    )

with tab_pollutants:
    st.plotly_chart(pollutant_means_chart(filtered), use_container_width=True)
    st.plotly_chart(pm_scatter_chart(filtered), use_container_width=True)
    st.plotly_chart(correlation_heatmap(filtered), use_container_width=True)
    st.dataframe(pollutant_summary(filtered), use_container_width=True, hide_index=True)
    st.caption(
        "Correlations describe pairwise linear association in the available "
        "observations; they do not establish causation."
    )

with tab_data:
    st.markdown("#### Dataset health")
    st.write(
        f"Rows read: **{cleaning_report.rows_before:,}** · "
        f"Exact duplicates removed: **{cleaning_report.exact_duplicates_removed:,}** · "
        f"Invalid or missing dates retained: **{cleaning_report.invalid_dates:,}**"
    )
    st.dataframe(missing_data_summary(filtered), use_container_width=True, hide_index=True)
    st.markdown("#### Methodology")
    st.markdown(
        "- The source CSV is read without editing it; the cleaned copy is created only on request.\n"
        "- Exact duplicate rows are removed. Distinct measurements for the same city and date are retained.\n"
        "- Dates and measurement columns are parsed; invalid dates and missing measurements remain missing.\n"
        "- Outliers are not deleted. Means and maxima can be sensitive to extreme values.\n"
        "- Rankings and trends use available AQI records and can be affected by unequal city coverage.\n"
        "- Category counts use the dataset's AQI_Bucket labels; categories are not reconstructed."
    )
    st.markdown(
        "[Dataset source: Kaggle – Air Quality Data in India](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india)"
    )
