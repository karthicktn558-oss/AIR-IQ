"""Plotly chart builders shared by the AIR IQ dashboard and notebook."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.analysis import (
    POLLUTANT_COLUMNS,
    aqi_category_counts,
    city_aqi_summary,
    monthly_aqi_trend,
    pollutant_correlations,
    seasonal_aqi_summary,
    yearly_aqi_trend,
)

PALETTE = ["#147D64", "#40A879", "#F2B84B", "#E77B43", "#C94C4C", "#5377A8"]


def aqi_distribution_chart(frame: pd.DataFrame) -> go.Figure:
    if "AQI" not in frame.columns:
        return go.Figure()
    data = frame.dropna(subset=["AQI"])
    return px.histogram(
        data, x="AQI", nbins=35, title="AQI distribution",
        labels={"AQI": "Air Quality Index"}, color_discrete_sequence=PALETTE,
    )


def city_comparison_chart(frame: pd.DataFrame, top_n: int = 20) -> go.Figure:
    summary = city_aqi_summary(frame).head(top_n).sort_values("mean")
    return px.bar(
        summary, x="mean", y="City", orientation="h", error_x=None,
        title=f"Cities with highest mean AQI (up to {top_n})",
        labels={"mean": "Mean AQI", "City": ""},
        color="mean", color_continuous_scale="YlOrRd",
        hover_data={"count": True, "median": ":.1f", "max": True},
    )


def monthly_trend_chart(frame: pd.DataFrame) -> go.Figure:
    trend = monthly_aqi_trend(frame)
    fig = px.line(
        trend, x="Month", y="AQI", markers=True, title="Monthly mean AQI",
        labels={"Month": "Month", "AQI": "Mean AQI"},
        color_discrete_sequence=PALETTE,
    )
    if "Observations" in trend.columns:
        fig.update_traces(
            customdata=trend[["Observations"]],
            hovertemplate="Month: %{x|%b %Y}<br>Mean AQI: %{y:.1f}"
            "<br>Observations: %{customdata[0]}<extra></extra>",
        )
    return fig


def seasonal_chart(frame: pd.DataFrame) -> go.Figure:
    summary = seasonal_aqi_summary(frame)
    return px.bar(
        summary, x="Season", y="AQI", title="Mean AQI by broad season",
        labels={"AQI": "Mean AQI"}, color="Season",
        color_discrete_sequence=PALETTE,
    )


def pm_scatter_chart(frame: pd.DataFrame) -> go.Figure:
    columns = {"PM2.5", "PM10", "City"}
    if not columns.issubset(frame.columns):
        return go.Figure()
    data = frame.dropna(subset=["PM2.5", "PM10"])
    return px.scatter(
        data, x="PM2.5", y="PM10", color="City", opacity=0.65,
        title="PM2.5 vs PM10", labels={"PM2.5": "PM2.5", "PM10": "PM10"},
        hover_data=["Date"] if "Date" in data.columns else None,
    )


def correlation_heatmap(frame: pd.DataFrame) -> go.Figure:
    corr = pollutant_correlations(frame)
    if corr.empty:
        return go.Figure()
    return px.imshow(
        corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu_r",
        title="Pollutant and AQI Pearson correlation",
        labels={"color": "Correlation"},
        aspect="auto",
    )


def category_chart(frame: pd.DataFrame) -> go.Figure:
    categories = aqi_category_counts(frame)
    return px.bar(
        categories, x="AQI_Bucket", y="Observations", color="AQI_Bucket",
        title="AQI category distribution (dataset-provided labels)",
        labels={"AQI_Bucket": "AQI category"},
        color_discrete_sequence=PALETTE,
    )


def yearly_trend_chart(frame: pd.DataFrame) -> go.Figure:
    trend = yearly_aqi_trend(frame)
    fig = px.line(
        trend, x="Year", y="AQI", markers=True, title="Yearly mean AQI",
        labels={"AQI": "Mean AQI"},
        color_discrete_sequence=PALETTE,
    )
    if "Observations" in trend.columns:
        fig.update_traces(
            customdata=trend[["Observations"]],
            hovertemplate="Year: %{x}<br>Mean AQI: %{y:.1f}"
            "<br>Observations: %{customdata[0]}<extra></extra>",
        )
    return fig


def pollutant_means_chart(frame: pd.DataFrame, city: str | None = None) -> go.Figure:
    columns = [column for column in POLLUTANT_COLUMNS if column in frame.columns]
    data = frame
    if city is not None and "City" in frame.columns:
        data = frame.loc[frame["City"].eq(city)]
    means = data[columns].mean().dropna().rename_axis("Pollutant").reset_index(name="Mean")
    return px.bar(
        means, x="Pollutant", y="Mean", title="Mean pollutant concentration",
        labels={"Mean": "Mean concentration (dataset units)"},
        color="Pollutant", color_discrete_sequence=PALETTE,
    )
