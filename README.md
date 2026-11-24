# AIR IQ — Indian Air Pollution & Air Quality Intelligence System

AIR IQ is an undergraduate B.Tech AI & Data Science project for exploring
historical air-quality observations across multiple Indian cities. It combines
reproducible data preparation, descriptive analysis, interactive Plotly
visualizations, a Jupyter notebook, and a Streamlit dashboard.

> **Data integrity:** AIR IQ does not fabricate, impute, or hardcode pollution
> observations or analytical findings. The Kaggle dataset is not included in
> this repository. Historical observations must not be presented as current AQI.

## Problem statement

Air-quality datasets contain measurements for multiple cities, pollutants, and
dates, but missingness and uneven reporting can make comparisons difficult.
AIR IQ provides a transparent workflow to inspect data quality, compare
available measurements, explore temporal patterns, and communicate the limits
of descriptive analysis.

## Objectives

- Explore the distribution of AQI and dataset-provided AQI categories.
- Compare city-level AQI and pollutant measurements with observation counts.
- Examine PM2.5/PM10, other pollutants, and pairwise correlations.
- Summarize monthly, broad seasonal, and yearly AQI patterns.
- Identify missing data and preserve outliers for inspection rather than
  deleting them automatically.
- Deliver a beginner-friendly dashboard and notebook that recompute findings
  from the original dataset.

## Dataset

Use the [India Air Quality dataset on Kaggle](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india).
The primary file is `city_day.csv`. Download it using your Kaggle account and
place it here:

```text
AIR-IQ/
└── data/
    └── raw/
        └── city_day.csv
```

The project does not redistribute the dataset. The application reports a clear
setup message if the file is absent. The expected columns include `City`,
`Date`, pollutant measurements, `AQI`, and optionally `AQI_Bucket`; the loader
requires only `City` and `Date` and charts the available measurement columns.

## Technologies

- Python 3.12
- Pandas, NumPy
- Matplotlib, Seaborn, Plotly
- Streamlit
- Jupyter Notebook

Exact dependency versions are listed in `requirements.txt`.

## Project architecture

```text
AIR-IQ/
├── data/
│   ├── raw/                    # Original Kaggle CSV (not committed)
│   └── cleaned/                # Generated cleaned CSV (not committed)
├── notebooks/
│   └── air_iq_analysis.ipynb   # Reproducible analysis notebook
├── src/
│   ├── data_cleaning.py        # Loading, validation, cleaning, CLI
│   ├── analysis.py             # Reusable descriptive statistics
│   └── visualizations.py       # Interactive Plotly charts
├── dashboard/
│   └── app.py                  # Streamlit dashboard
├── visualizations/             # Reserved for exported figures
├── documentation/
│   └── methodology.md          # Data and analysis decisions
├── tests/
│   └── test_analysis.py
├── requirements.txt
└── README.md
```

## Installation

Use Python 3.12. This project does not create or replace a virtual environment
automatically; the current workspace had no `.venv` at setup time. From the
project directory, create one if needed:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents environment activation, run commands directly with
`.venv\Scripts\python.exe -m pip ...`. Install Jupyter and the dashboard
dependencies in the same environment.

## How to run

1. Download `city_day.csv` from Kaggle and place it in `data/raw/`.
2. Install requirements using the Python 3.12 environment above.
3. Optionally create a cleaned copy:

   ```powershell
   python -m src.data_cleaning
   ```

   The output is `data/cleaned/city_day_cleaned.csv`; the original raw CSV is
   never modified. Custom paths can be supplied with `--input` and `--output`.
4. Launch the interactive dashboard from the project directory:

   ```powershell
   streamlit run dashboard/app.py
   ```

   The dashboard also accepts a CSV path in its sidebar.
5. Open the analysis notebook:

   ```powershell
   jupyter notebook notebooks/air_iq_analysis.ipynb
   ```

6. Run the focused tests:

   ```powershell
   python -m unittest discover -s tests -v
   ```

## Analysis methodology

The cleaning and analysis decisions are documented in
[documentation/methodology.md](documentation/methodology.md). In summary:

- The raw file is read without modification; only exact duplicate rows are
  removed. Rows sharing a city and date but having different measurements are
  retained.
- City and AQI bucket text is trimmed. Dates and numeric measurements are
  parsed. Unparseable values become missing instead of being guessed.
- Missing values, invalid dates, and statistical outliers are retained and
  reported. Each statistic uses the available values for that measure.
- City rankings are based on mean available AQI and include observation counts.
  Uneven reporting coverage can affect comparisons.
- Monthly/yearly trends pool city-day records and are not population-weighted.
- Broad season groups are Winter (Dec–Feb), Summer (Mar–May), Monsoon (Jun–Sep),
  and Post-monsoon (Oct–Nov), not city-specific climate classifications.
- AQI category analysis uses only source-provided `AQI_Bucket` labels.
- Correlation is pairwise Pearson correlation and does not imply causation.

## Results and findings

No analytical results are included in advance. The source dataset was not
present in the workspace when this project was created, so the charts, summary
statistics, city rankings, and findings will be computed when the real Kaggle
CSV is supplied and the notebook/dashboard is run. This avoids inventing
real-world pollution values or presenting unverified conclusions.

## Limitations

- Results depend on the dataset's historical date range, coverage, and quality.
- City means and pooled trends may be affected by missing or uneven reporting.
- Pooled comparisons are not adjusted for population, weather, monitor count,
  or changes to measurement practices.
- Broad month-to-season assignments do not model local climatic variation.
- Correlation and descriptive comparisons do not support causal claims.
- AIR IQ is an educational analysis tool, not a real-time air-quality service
  or health advisory.

## Future improvements

- Add map-based views with verified geographic coordinates.
- Provide robustness comparisons using medians and explicit minimum coverage
  thresholds selected by project stakeholders.
- Evaluate seasonal patterns per city and account for reporting coverage.
- Add data validation summaries and downloadable filtered tables.
- Integrate a separately sourced real-time data feed with explicit provenance,
  keeping it distinct from the historical Kaggle dataset.

## Team contributions (8 members)

Adapt the following role allocation to the group's actual contributions; do not
claim work that was not performed.

1. **Member 1 — Project coordination:** scope, milestones, integration.
2. **Member 2 — Data acquisition:** Kaggle download, source documentation.
3. **Member 3 — Data cleaning:** schema checks, missingness, duplicate review.
4. **Member 4 — Exploratory analysis:** AQI and city comparisons.
5. **Member 5 — Temporal analysis:** monthly, seasonal, and yearly patterns.
6. **Member 6 — Visualization:** Plotly chart design and interpretation.
7. **Member 7 — Dashboard:** Streamlit layout, filters, and usability.
8. **Member 8 — Testing and documentation:** validation, limitations, report.

## Academic presentation guidance

Show the dataset source and date coverage, explain how missingness affects
comparisons, display observation counts beside averages, and distinguish
historical descriptive patterns from current conditions. Discuss association
without claiming causation.
