# דשבורד שוק העבודה — Power BI project

An editable **PBIP + enhanced PBIR + TMDL** project built from the supplied
screenshots, `GraphTbl.csv`, and `SeriesGraphTbl.csv`. The report opens on
**עמוד הבית**. This is a new project: the uploaded 311-byte `.pbip` contained only
a reference to report folders, not the report or semantic model itself.

## Open on Windows

1. Extract the **entire ZIP**, keeping the PBIP, Report, SemanticModel, data, and
   script beside one another.
2. Install a current **Power BI Desktop for Windows** with PBIP/enhanced PBIR
   support. Enable the Power BI project/report-format preview options if your
   Desktop release still requires them, then restart Desktop.
3. From the extracted folder, run `powershell -File .\Open-Project.ps1`.
   This sets `DataFolder` to that copy's `data` directory and opens the PBIP.
   Alternatively set the `DataFolder` parameter in Power Query yourself and
   open the root `דשבורד שוק העבודה.pbip`.
4. Select **Refresh**. The metadata and calendar tables can load immediately.
   Populate `data/observations.csv` with real observations, then refresh again
   to populate the charts and KPI values.

The CSV uploads describe **which series to show**, not their dated numeric
observations. The supplied `observations.csv` therefore has a header and **zero
rows**. No screenshot values, synthetic history, or unverified API responses are
presented as data. The report displays dashes/empty charts until data is added.

## Home page

- 1300 × 1450 canvas, matching the reference's portrait proportions and RTL
  arrangement: right-aligned Hebrew title, navigation, navy KPI headers, gold
  separators, and a pale-gray two-by-two chart layout.
- Four KPI blocks: labor-force rates (25–64); employee jobs/employed persons;
  job vacancies; nominal wages. Values, changes, arrows, and common-period
  headers are measures, not baked-in screenshot text.
- **g01:** unemployment on the primary Y axis; participation/employment on the
  secondary Y axis. **g02:** year-over-year change smoothed across three months.
  **g03:** three-month average vacancy counts as columns and vacancy rate as a
  line on the secondary axis. **g04:** quarterly nominal-wage change and its
  four-quarter moving average, preserving both definitions of the same code.
- Each panel has its own date range, **1Y / 5Y / All** selection and reset
  bookmark. Explicit visual interactions isolate the controls to that panel.
- The cyan down-arrow opens a graph-specific data table. Use the table's
  **⋯ → Export data** menu for CSV export. It is not an automatic file download.
- The other six navigation tabs open **catalogue pages** containing the supplied
  graph/series definitions. Their full dashboards have not been built. Missing
  regional series definitions remain visible in the catalogue notes.

All report elements are native, editable Power BI visuals; no custom-visual
installation or online service credentials are required. `docs/home-layout.html`
and its PNG are a layout guide, **not** a Desktop screenshot or rendering test.

## Data contract

UTF-8 CSV, comma-delimited, with this exact header:

```csv
FREQ,TIME_PERIOD,SERIES_CODE,OBS_VALUE,SeriesName,Legend
```

| Field | Required representation |
| --- | --- |
| FREQ | `M`, `Q`, `W`, `D`, or `A`; consistent for each series |
| TIME_PERIOD | ISO `YYYY-MM-DD`; month/quarter/year start for M/Q/A |
| SERIES_CODE | One exact series code, such as `UE_R_A25_64_M_SA` |
| OBS_VALUE | Finite decimal in the series' native unit; empty means missing, never zero |
| SeriesName / Legend | Optional descriptive text; keep the two CSV fields |

Exactly one row per **SERIES_CODE + TIME_PERIOD**. The Power Query import rejects
duplicate keys, missing keys, invalid frequencies, and conversion errors.
`python tools/check_observations.py` performs stricter date/frequency checks before
refreshing. The currently empty file is a template, not a validated data feed.

For the home page, supply the eleven distinct codes listed in
`docs/home-series.csv`. Counts for `EM_M_SA` and `EP_M_SA` are **thousands**; wages
are NIS; rate observations such as 81.6 are **percentage points**, not 0.816.
`AW_ANNPCT_Q_SA` is already an annual percentage change; the model does not
derive it from monthly wages. Smoothing requires three actual months or four
actual quarters; incomplete windows return blank. Year-over-year comparisons
require the corresponding period from the preceding year.

KPI changes are against the previous available observation. Rate changes use
percentage points; other changes use percentage growth. The card date is the
latest nonblank period common to all its series, preventing a header from
silently mixing observation periods. An empty cell does not become zero.

## Model and source preservation

The central six-table arrangement follows the model image: `MeasuresTable`,
`Date`, `Fact`, `Date2`, `Date Periods`, and `Date Periods2`. Both date dimensions
have active single-direction relationships to Fact. The period bridges filter
their respective date dimension in both directions. `GraphTbl`, `SeriesGraphTbl`,
and `DimSeries` supply the chart catalogue and the unique series dimension.
Catalogue-to-Fact mapping is applied by measures with `TREATAS`, avoiding a
many-to-many observation join. See `docs/model.md` for the diagram and calculations.

`Date` uses the ADDCOLUMNS/CALENDAR formula from your follow-up image, including
the Sunday-based `WEEKNUM(...,1)` convention. Its minimum/maximum come from Fact.
The only addition is a 2011–2023 **calendar-only fallback** when Fact is empty,
plus `DateForGraph_M`; no fact values are generated.

The original two CSVs and uploaded manifest are retained byte-for-byte in
`data/source/`. Normalized metadata has 48 defined graph/KPI entries and 167
expanded, deduplicated series mappings. See `docs/catalogue-notes.md` for all
unmapped entries and normalization decisions. No provider code has been guessed
for missing regional definitions.

## Validation and limitations

Run these optional developer checks with Python 3.10+:

```sh
python -m pip install -r tools/requirements-validation.txt
python tools/validate_project.py
python tools/check_observations.py
python -m unittest discover -s tests -v
```

The included offline Microsoft schemas validate report structure and all page,
visual, filter, and bookmark documents. `tools/TmdlValidator` additionally checks
the TMDL with Microsoft TOM. Checks performed here are recorded in
`docs/validation.md`.

**Power BI Desktop could not be run in the Linux build environment.** TMDL and
Power Query parsing do not execute the DAX engine, refresh the model in Desktop,
or prove visual rendering. Exact pixel matching, native secondary-axis behavior,
button/slicer behavior, and data refresh still require a Windows Desktop check
after observations are supplied. The source captions reproduce the reference;
update them if your observations have a different source.
