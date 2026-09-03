param(
    [Parameter(Mandatory = $true)]
    [string]$Owner,

    [Parameter(Mandatory = $true)]
    [string[]]$Repositories
)

$ErrorActionPreference = "Stop"
$results = foreach ($repository in $Repositories) {
    $nameWithOwner = "$Owner/$repository"
    try {
        $repo = gh repo view $nameWithOwner --json nameWithOwner,visibility,isPrivate,url |
            ConvertFrom-Json
        [pscustomobject]@{
            name = $repo.nameWithOwner
            visibility = $repo.visibility
            is_private = [bool]$repo.isPrivate
            url = $repo.url
            exists = $true
            pass = [bool]$repo.isPrivate -and $repo.visibility -eq "PRIVATE"
            error = $null
        }
    }
    catch {
        [pscustomobject]@{
            name = $nameWithOwner
            visibility = $null
            is_private = $false
            url = $null
            exists = $false
            pass = $false
            error = $_.Exception.Message
        }
    }
}

$report = [pscustomobject]@{
    owner = $Owner
    repositories = $results
    pass = -not ($results | Where-Object { -not $_.pass })
}

$report | ConvertTo-Json -Depth 5
if (-not $report.pass) {
    exit 2
}
