[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)] [string] $ProjectId,
  [Parameter(Mandatory = $true)] [string] $GitHubRepository,
  [string] $Region = "asia-southeast1",
  [string] $GeminiModel = "gemini-2.5-flash",
  [string] $Branch = "main",
  [switch] $Push,
  [switch] $RunDeployment
)

$ErrorActionPreference = "Stop"

function Require-Command([string] $Name) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Required command '$Name' was not found in PATH. Install it before running this script."
  }
}

function Invoke-External {
  param(
    [Parameter(Mandatory = $true)] [string] $Command,
    [Parameter(Mandatory = $true)] [string[]] $Arguments
  )
  Write-Host "> $Command $($Arguments -join ' ')" -ForegroundColor DarkGray
  & $Command @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "$Command failed with exit code $LASTEXITCODE."
  }
}

Require-Command "gcloud"
Require-Command "gh"
Require-Command "git"

if (-not (Test-Path ".github/workflows/deploy-cloud-run.yml")) {
  throw "Run this script from the TrustLens repository root. Missing .github/workflows/deploy-cloud-run.yml."
}

$GitHubParts = $GitHubRepository.Split("/", 2)
if ($GitHubParts.Count -ne 2) {
  throw "GitHubRepository must use OWNER/REPOSITORY format."
}
$GitHubOwner = $GitHubParts[0]
$GitHubRepo = $GitHubParts[1]

Write-Host "Checking authentication..." -ForegroundColor Cyan
Invoke-External "gcloud" @("auth", "list", "--filter=status:ACTIVE", "--format=value(account)")
Invoke-External "gh" @("auth", "status")

$GitHubRepositoryId = (& gh repo view $GitHubRepository --json id --jq ".id").Trim()
if (-not $GitHubRepositoryId) {
  throw "Could not retrieve the numeric GitHub repository ID."
}

Write-Host "Step 1/5: Bootstrapping Google Cloud WIF and IAM..." -ForegroundColor Cyan
& powershell -NoProfile -ExecutionPolicy Bypass -File "$PSScriptRoot\bootstrap-github-wif.ps1" `
  -ProjectId $ProjectId `
  -GitHubOwner $GitHubOwner `
  -GitHubRepo $GitHubRepo `
  -GitHubRepositoryId $GitHubRepositoryId `
  -Region $Region
if ($LASTEXITCODE -ne 0) {
  throw "Google Cloud WIF bootstrap failed."
}

$ProjectNumber = (gcloud projects describe $ProjectId --format="value(projectNumber)").Trim()
$PoolResource = "projects/$ProjectNumber/locations/global/workloadIdentityPools/github-pool"
$ProviderResource = "$PoolResource/providers/github-provider"
$DeployerEmail = "github-deployer@$ProjectId.iam.gserviceaccount.com"
$RuntimeEmail = "trustlens-runtime@$ProjectId.iam.gserviceaccount.com"

Write-Host "Step 2/5: Configuring GitHub Actions variables..." -ForegroundColor Cyan
Invoke-External "gh" @("variable", "set", "GCP_PROJECT_ID", "--repo", $GitHubRepository, "--body", $ProjectId)
Invoke-External "gh" @("variable", "set", "GCP_REGION", "--repo", $GitHubRepository, "--body", $Region)
Invoke-External "gh" @("variable", "set", "GEMINI_MODEL", "--repo", $GitHubRepository, "--body", $GeminiModel)

Write-Host "Step 3/5: Configuring GitHub Actions secrets..." -ForegroundColor Cyan
# Secret values are passed to gh over stdin and are not printed by this script.
$ProviderResource | gh secret set GCP_WORKLOAD_IDENTITY_PROVIDER --repo $GitHubRepository
if ($LASTEXITCODE -ne 0) { throw "Failed to set GCP_WORKLOAD_IDENTITY_PROVIDER." }
$DeployerEmail | gh secret set GCP_DEPLOYER_SERVICE_ACCOUNT --repo $GitHubRepository
if ($LASTEXITCODE -ne 0) { throw "Failed to set GCP_DEPLOYER_SERVICE_ACCOUNT." }
$RuntimeEmail | gh secret set GCP_RUNTIME_SERVICE_ACCOUNT --repo $GitHubRepository
if ($LASTEXITCODE -ne 0) { throw "Failed to set GCP_RUNTIME_SERVICE_ACCOUNT." }

Write-Host "Step 4/5: Checking repository state..." -ForegroundColor Cyan
$Status = git status --porcelain
if ($Status) {
  Write-Host "Uncommitted changes detected:" -ForegroundColor Yellow
  $Status
  Invoke-External "git" @("add", ".github/workflows/deploy-cloud-run.yml", "trustlens-docs/GITHUB_ACTIONS_CICD.md")
  Invoke-External "git" @("commit", "-m", "Add automated TrustLens Cloud Run CI/CD")
}

if ($Push) {
  Write-Host "Pushing workflow to GitHub..." -ForegroundColor Cyan
  Invoke-External "git" @("push", "origin", $Branch)
} else {
  Write-Host "Push skipped. Re-run with -Push to publish the workflow." -ForegroundColor Yellow
}

Write-Host "Step 5/5: Deployment trigger" -ForegroundColor Cyan
if ($RunDeployment) {
  if (-not $Push) {
    throw "Use -Push together with -RunDeployment so GitHub Actions receives the workflow and commit."
  }
  Invoke-External "gh" @("workflow", "run", "deploy-cloud-run.yml", "--repo", $GitHubRepository, "--ref", $Branch, "-f", "deploy=true")
  Write-Host "Deployment workflow dispatched. Monitor it with:" -ForegroundColor Green
  Write-Host "gh run watch --repo $GitHubRepository" -ForegroundColor Green
} else {
  Write-Host "Automatic workflow dispatch skipped. A push to $Branch will deploy, or re-run with -RunDeployment." -ForegroundColor Yellow
}

Write-Host "Complete." -ForegroundColor Green
Write-Host "Provider: $ProviderResource"
Write-Host "Cloud Run service: trustlens-api"
Write-Host "Region: $Region"
