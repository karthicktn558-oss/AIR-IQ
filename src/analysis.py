"""Reusable descriptive analyses for the India air-quality dataset."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

POLLUTANT_COLUMNS = (
    "PM2.5",
    "PM10",
    "NO",
    "NO2",
    "NOx",
    "NH3",
    "CO",
    "SO2",
    "O3",
    "Benzene",
    "Toluene",
    "Xylene",
)
SEASON_BY_MONTH = {
    12: "Winter",
    1: "Winter",
    2: "Winter",
    3: "Summer",
    4: "Summer",
    5: "Summer",
    6: "Monsoon",
    7: "Monsoon",
    8: "Monsoon",
    9: "Monsoon",
    10: "Post-monsoon",
    11: "Post-monsoon",
}


def _available(frame: pd.DataFrame, columns: Sequence[str]) -> list[str]:
    return [column for column in columns if column in frame.columns]


def city_aqi_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Return each city's mean, median, maximum, and available AQI count."""
    if not {"City", "AQI"}.issubset(frame.columns):
        return pd.DataFrame(columns=["City", "mean", "median", "max", "count"])
    data = frame.dropna(subset=["City", "AQI"])
    return (
        data.groupby("City", as_index=False)["AQI"]
        .agg(mean="mean", median="median", max="max", count="count")
        .sort_values("mean", ascending=False)
        .reset_index(drop=True)
    )


def pollutant_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize available pollutant columns without imputing their values."""
    columns = _available(frame, POLLUTANT_COLUMNS)
    if not columns:
        return pd.DataFrame(columns=["Pollutant", "mean", "median", "std", "count"])
    summary = frame[columns].agg(["mean", "median", "std", "count"]).T
    summary.index.name = "Pollutant"
    return summary.reset_index()


def missing_data_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Report missing cell counts and percentages for every input column."""
    total = len(frame)
    counts = frame.isna().sum()
    return pd.DataFrame(
        {
            "Column": counts.index,
            "Missing": counts.values,
            "Missing percent": (counts.values / total * 100) if total else 0.0,
        }
    ).sort_values("Missing percent", ascending=False, ignore_index=True)


def monthly_aqi_trend(frame: pd.DataFrame) -> pd.DataFrame:
    """Return monthly AQI mean and observation count across available cities."""
    if not {"Date", "AQI"}.issubset(frame.columns):
        return pd.DataFrame(columns=["Month", "AQI", "Observations"])
    data = frame.dropna(subset=["Date", "AQI"]).copy()
    data["Month"] = data["Date"].dt.to_period("M").dt.to_timestamp()
    return (
        data.groupby("Month", as_index=False)
        .agg(AQI=("AQI", "mean"), Observations=("AQI", "count"))
        .sort_values("Month")
        .reset_index(drop=True)
    )


def seasonal_aqi_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize AQI by broad meteorological month groups (not local climate)."""
    if not {"Date", "AQI"}.issubset(frame.columns):
        return pd.DataFrame(columns=["Season", "AQI", "Observations"])
    data = frame.dropna(subset=["Date", "AQI"]).copy()
    data["Season"] = data["Date"].dt.month.map(SEASON_BY_MONTH)
    order = ["Winter", "Summer", "Monsoon", "Post-monsoon"]
    result = (
        data.groupby("Season", as_index=False)
        .agg(AQI=("AQI", "mean"), Observations=("AQI", "count"))
    )
    result["Season"] = pd.Categorical(result["Season"], categories=order, ordered=True)
    return result.sort_values("Season").reset_index(drop=True)


def yearly_aqi_trend(frame: pd.DataFrame) -> pd.DataFrame:
    """Return yearly mean AQI and observation count across available cities."""
    if not {"Date", "AQI"}.issubset(frame.columns):
        return pd.DataFrame(columns=["Year", "AQI", "Observations"])
    data = frame.dropna(subset=["Date", "AQI"]).copy()
    data["Year"] = data["Date"].dt.year
    return (
        data.groupby("Year", as_index=False)
        .agg(AQI=("AQI", "mean"), Observations=("AQI", "count"))
        .sort_values("Year")
        .reset_index(drop=True)
    )


def aqi_category_counts(frame: pd.DataFrame) -> pd.DataFrame:
    """Count dataset-provided AQI buckets; do not infer missing categories."""
    if "AQI_Bucket" not in frame.columns:
        return pd.DataFrame(columns=["AQI_Bucket", "Observations"])
    data = frame.dropna(subset=["AQI_Bucket"])
    return (
        data.groupby("AQI_Bucket", as_index=False, observed=True)
        .size()
        .rename(columns={"size": "Observations"})
        .sort_values("Observations", ascending=False)
        .reset_index(drop=True)
    )


def pollutant_correlations(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate pairwise-complete Pearson correlations for present pollutants."""
    columns = _available(frame, POLLUTANT_COLUMNS)
    if "AQI" in frame.columns:
        columns.append("AQI")
    return frame[columns].corr(min_periods=2) if columns else pd.DataFrame()


def city_pollutant_summary(frame: pd.DataFrame, city: str) -> pd.DataFrame:
    """Return available pollutant means for one city."""
    if "City" not in frame.columns:
        return pd.DataFrame(columns=["Pollutant", "Mean"])
    columns = _available(frame, POLLUTANT_COLUMNS)
    if not columns:
        return pd.DataFrame(columns=["Pollutant", "Mean"])
    means = frame.loc[frame["City"].eq(city), columns].mean()
    return means.rename_axis("Pollutant").reset_index(name="Mean").dropna()
