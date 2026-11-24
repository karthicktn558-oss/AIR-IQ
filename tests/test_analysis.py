"""Focused tests for AIR IQ data preparation and analysis."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.analysis import (
    aqi_category_counts,
    city_aqi_summary,
    monthly_aqi_trend,
    seasonal_aqi_summary,
    yearly_aqi_trend,
)
from src.data_cleaning import load_and_clean_data


class CleaningTests(unittest.TestCase):
    def test_removes_only_exact_duplicate_and_retains_missing_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "city_day.csv"
            pd.DataFrame(
                [
                    {"City": " Delhi ", "Date": "2020-01-01", "AQI": 100},
                    {"City": " Delhi ", "Date": "2020-01-01", "AQI": 100},
                    {"City": "Delhi", "Date": "2020-01-02", "AQI": None},
                ]
            ).to_csv(path, index=False)

            cleaned, report = load_and_clean_data(path)

        self.assertEqual(len(cleaned), 2)
        self.assertEqual(report.exact_duplicates_removed, 1)
        self.assertEqual(cleaned.loc[0, "City"], "Delhi")
        self.assertTrue(pd.isna(cleaned.loc[1, "AQI"]))

    def test_reports_missing_dataset_with_guidance(self) -> None:
        with self.assertRaisesRegex(FileNotFoundError, "data/raw/city_day.csv"):
            load_and_clean_data("missing-city-day.csv")


class AnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = pd.DataFrame(
            {
                "City": ["A", "A", "B", "B"],
                "Date": pd.to_datetime(
                    ["2020-01-01", "2020-06-01", "2021-01-01", "2021-10-01"]
                ),
                "AQI": [10, 30, 50, 70],
                "AQI_Bucket": ["Good", "Satisfactory", "Moderate", "Poor"],
            }
        )

    def test_city_summary_uses_observed_values(self) -> None:
        result = city_aqi_summary(self.frame)
        self.assertEqual(result.iloc[0]["City"], "B")
        self.assertEqual(result.iloc[0]["mean"], 60)
        self.assertEqual(result.iloc[0]["count"], 2)

    def test_monthly_and_yearly_trends_have_counts(self) -> None:
        monthly = monthly_aqi_trend(self.frame)
        yearly = yearly_aqi_trend(self.frame)
        self.assertEqual(len(monthly), 4)
        self.assertEqual(monthly["Observations"].sum(), 4)
        self.assertEqual(yearly["Year"].tolist(), [2020, 2021])
        self.assertEqual(yearly["AQI"].tolist(), [20, 60])

    def test_season_and_dataset_category_counts(self) -> None:
        seasonal = seasonal_aqi_summary(self.frame)
        categories = aqi_category_counts(self.frame)
        self.assertEqual(seasonal["Observations"].sum(), 4)
        self.assertEqual(categories["Observations"].sum(), 4)
        self.assertEqual(set(categories["AQI_Bucket"]), {"Good", "Satisfactory", "Moderate", "Poor"})


if __name__ == "__main__":
    unittest.main()
