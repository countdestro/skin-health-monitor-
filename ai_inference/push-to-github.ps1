# Run AFTER creating an empty repo at https://github.com/YOUR_USER/YOUR_REPO
# Usage: .\push-to-github.ps1 -GitHubUser "your_github_username" -RepoName "skin-health-monitor-member3"

param(
    [Parameter(Mandatory = $true)]
    [string] $GitHubUser,
    [Parameter(Mandatory = $false)]
    [string] $RepoName = "skin-health-monitor-member3"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$url = "https://github.com/$GitHubUser/$RepoName.git"
if (git remote get-url origin 2>$null) {
    Write-Host "Remote 'origin' already set. Pushing..."
    git push -u origin main
} else {
    git remote add origin $url
    Write-Host "Added origin: $url"
    Write-Host "Pushing (sign in if prompted)..."
    git push -u origin main
}
