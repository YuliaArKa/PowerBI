param([switch]$NoOpen)
$ErrorActionPreference = 'Stop'

# Run this file after extracting the complete ZIP on a Windows machine.
# It updates only the Power Query data-folder parameter, then opens the PBIP.
$projectRoot = $PSScriptRoot
$models = @(Get-ChildItem -LiteralPath $projectRoot -Directory -Filter '*.SemanticModel')
$projects = @(Get-ChildItem -LiteralPath $projectRoot -File -Filter '*.pbip')
if ($models.Count -ne 1 -or $projects.Count -ne 1) {
    throw 'Expected one PBIP and one SemanticModel folder beside this script.'
}
$dataFolder = Join-Path $projectRoot 'data'
if (-not (Test-Path -LiteralPath (Join-Path $dataFolder 'observations.csv'))) {
    throw 'Missing data/observations.csv. Extract the complete project ZIP first.'
}
$parameterFile = Join-Path $models[0].FullName 'definition/expressions.tmdl'
$original = [IO.File]::ReadAllText($parameterFile, [Text.Encoding]::UTF8)
$mPath = $dataFolder.Replace('\', '/').Replace('"', '""')
$newLine = 'expression DataFolder = "' + $mPath + '" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
if (-not [regex]::IsMatch($original, '(?m)^expression DataFolder =.*$')) {
    throw 'Could not find the DataFolder parameter. No files have been changed.'
}
$updated = [regex]::Replace($original, '(?m)^expression DataFolder =.*$', [Text.RegularExpressions.MatchEvaluator]{ param($match) $newLine })
if ($updated -ne $original) {
    [IO.File]::WriteAllText($parameterFile, $updated, [Text.UTF8Encoding]::new($false))
}
Write-Host ('DataFolder configured: ' + $dataFolder)
if (-not $NoOpen) { Start-Process -FilePath $projects[0].FullName }
