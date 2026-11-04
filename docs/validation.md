# Validation record — 2026-11-04

Performed in the managed Linux environment. These are definition/parser and
input-validation results, not a Power BI Desktop certification.

| Check | Result |
| --- | --- |
| Microsoft PBIP/PBIR/PBISM and report JSON schemas | 132 documents passed |
| Cross-reference checks | 108 entity/column/measure references passed |
| Report layout structure | 11 pages and 110 visuals; all visual bounds inside their canvases |
| Home page | 70 native visuals, including four chart panels and four KPI blocks |
| Navigation/reset targets | 25 actions and four bookmarks reference existing destinations |
| Slicer isolation | Each of eight home-panel slicers filters only its assigned chart |
| Microsoft TOM 19.84.1 TMDL deserialization | Passed: 9 tables, 6 relationships, 32 measures, 1 M parameter |
| Microsoft Power Query parser 0.18.2 | All five M expressions parsed successfully |
| Observation-input and catalogue-normalization unit tests | 14 tests passed; none skipped |
| Observation input | Valid empty template, **0 observation rows**; not a populated data feed |
| Original uploads | All three files preserved byte-for-byte in data/source |
| Rebuild repeatability | Second build left all generated report/model/data file contents identical |
| HTML layout guide | Chromium rendered 70 positioned elements; no observation paths drawn |

The report schema checks include page definitions, native-visual definitions,
filters, resource/theme references, and bookmarks. Catalogue checks cover
combined-code splitting, duplicate KPI removal, the kpi6/kpi06 normalization,
sector-code expansion, and preservation of both g04 wage transformations.

Not executed: Windows Power BI Desktop, Power Query refresh, DAX engine queries,
native visual rendering, native UI interaction, the Windows launch helper, and
Power BI Service publication. No numerical chart/KPI correctness or exact visual
match is claimed without those checks and real observation data. The existing
Linux environment cannot run Power BI Desktop natively.

The six non-home navigation pages are metadata catalogues, not completed
dashboards. The four hidden export pages contain native data tables.

## Windows acceptance check

1. Extract the full ZIP and run `Open-Project.ps1` to set DataFolder and open PBIP.
2. Refresh. Confirm metadata/calendar load and the no-observation state displays.
3. Add real rows for the eleven home-series codes; validate input; refresh.
4. Check one known period against its source for each KPI and each chart. Check
   the common-period KPI header, percentage-point versus percentage changes,
   three-month windows, four-quarter wage smoothing, and missing-value behavior.
5. Confirm both native Y axes on g01 and g03; compare fonts, spacing, and legend
   placement to the reference at FitToPage. Adjust native visual formatting in
   Desktop if a Desktop release interprets a formatting property differently.
6. Change each panel's date/period controls; confirm other panels and KPIs stay
   unchanged; reset; open the export table and export its data.
