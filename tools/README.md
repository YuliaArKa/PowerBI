`build_project.py` uses Python's standard library. It rebuilds the report and
model from the two originals in `data/source/`, preserves `observations.csv`, and
preserves the configured `DataFolder` expression. Rebuilding replaces generated
visual/model files, so back up any manual Power BI edits first.

`validate_project.py` uses the unmodified Microsoft schemas vendored in `schemas/`.
Install `requirements-validation.txt`, then run it from any directory. It checks
schemas, field references, report/model paths, action targets, visual bounds, and
per-chart slicer isolation. It is not a Power BI rendering or DAX engine test.

`check_observations.py` validates the local observation file and returns nonzero
for malformed input, duplicate keys, invalid frequency/date conventions, and
non-finite values. A valid empty template is explicitly reported as zero rows.

`TmdlValidator/` is an optional Microsoft TOM parser check, using .NET 8:

```
dotnet run --project tools/TmdlValidator -- "<absolute-path-to-SemanticModel/definition>"
```

Microsoft's schema source is https://github.com/microsoft/json-schemas .
The snapshot used here is from the main branch at build time, and individual
schemas retain their original `$id` and version. Schema validation does not
validate every built-in visual formatting property or guarantee Desktop layout.

The optional M syntax check uses Microsoft's Power Query parser:

```
npm ci --prefix tools/powerquery --ignore-scripts --no-audit --no-fund
node tools/powerquery/check.cjs
```

This parses the five generated Power Query expressions; it does not execute
Power Query, access a data source, or refresh an Analysis Services engine.
