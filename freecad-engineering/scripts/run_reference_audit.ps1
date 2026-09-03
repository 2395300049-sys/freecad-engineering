param(
    [Parameter(Mandatory = $true)]
    [string]$InputFile,
    [Parameter(Mandatory = $true)]
    [string]$FreeCADCmd,
    [int]$ExpectedOccurrences = 0,
    [string]$OutputFile = ""
)

$ErrorActionPreference = "Stop"
$script = Join-Path $PSScriptRoot "audit_reference_assembly.py"
if (-not (Test-Path -LiteralPath $FreeCADCmd)) { throw "FreeCADCmd not found: $FreeCADCmd" }
if (-not (Test-Path -LiteralPath $InputFile)) { throw "Input model not found: $InputFile" }

$env:FREECAD_AUDIT_INPUT = (Resolve-Path -LiteralPath $InputFile).Path
$env:FREECAD_AUDIT_EXPECTED = if ($ExpectedOccurrences -gt 0) { [string]$ExpectedOccurrences } else { "" }
$env:FREECAD_AUDIT_OUTPUT = $OutputFile

$escaped = $script.Replace("'", "''")
& $FreeCADCmd -c "p=r'$escaped'; exec(compile(open(p,encoding='utf-8').read(),p,'exec'),{'__file__':p,'__name__':'__main__'})"
exit $LASTEXITCODE
