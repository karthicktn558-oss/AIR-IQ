"""Load and clean the original India air-quality city-day dataset."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "city_day.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "cleaned" / "city_day_cleaned.csv"
REQUIRED_COLUMNS = {"City", "Date"}


@dataclass(frozen=True)
class CleaningReport:
    """Counts of the non-destructive cleaning operations performed."""

    input_path: str
    rows_before: int
    rows_after: int
    exact_duplicates_removed: int
    invalid_dates: int


def load_and_clean_data(
    path: str | Path = DEFAULT_INPUT,
) -> tuple[pd.DataFrame, CleaningReport]:
    """Read a source CSV and return a cleaned copy plus an operation report.

    The source file is never edited. Invalid dates and missing measurements are
    retained for transparent downstream handling; only exact duplicate rows
    are removed.
    """
    input_path = Path(path)
    if not input_path.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {input_path}\n"
            "Download city_day.csv from "
            "https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india "
            "and place it in data/raw/city_day.csv."
        )

    frame = pd.read_csv(input_path, low_memory=False, encoding="utf-8-sig")
    missing_columns = REQUIRED_COLUMNS.difference(frame.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Dataset is missing required column(s): {missing}")

    rows_before = len(frame)
    frame = frame.drop_duplicates().copy().reset_index(drop=True)
    duplicates_removed = rows_before - len(frame)

    frame["City"] = frame["City"].astype("string").str.strip()
    frame["City"] = frame["City"].replace("", pd.NA)
    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    invalid_dates = int(frame["Date"].isna().sum())

    for column in frame.columns:
        if column not in {"City", "Date", "AQI_Bucket"}:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if "AQI_Bucket" in frame.columns:
        frame["AQI_Bucket"] = frame["AQI_Bucket"].astype("string").str.strip()
        frame["AQI_Bucket"] = frame["AQI_Bucket"].replace("", pd.NA)

    report = CleaningReport(
        input_path=str(input_path.resolve()),
        rows_before=rows_before,
        rows_after=len(frame),
        exact_duplicates_removed=duplicates_removed,
        invalid_dates=invalid_dates,
    )
    return frame, report


def save_cleaned_data(
    frame: pd.DataFrame, path: str | Path = DEFAULT_OUTPUT
) -> Path:
    """Save a cleaned dataset, creating its parent directory if necessary."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False, date_format="%Y-%m-%d")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        cleaned, report = load_and_clean_data(args.input)
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        parser.exit(2, f"error: {error}\n")
    output_path = save_cleaned_data(cleaned, args.output)
    print(f"Saved {len(cleaned):,} rows to {output_path}")
    for key, value in asdict(report).items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
