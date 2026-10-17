[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)] [string] $ProjectId,
  [Parameter(Mandatory = $true)] [string] $GitHubOwner,
  [Parameter(Mandatory = $true)] [string] $GitHubRepo,
  [Parameter(Mandatory = $true)] [string] $GitHubRepositoryId,
  [string] $Region = "asia-southeast1",
  [string] $PoolId = "github-pool",
  [string] $ProviderId = "github-provider",
  [string] $DeployerServiceAccountId = "github-deployer",
  [string] $RuntimeServiceAccountId = "trustlens-runtime"
)

$ErrorActionPreference = "Stop"

function Invoke-Gcloud {
  param([Parameter(Mandatory = $true)] [string[]] $Arguments)
  & gcloud @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "gcloud failed with exit code ${LASTEXITCODE}: gcloud $($Arguments -join ' ')"
  }
}

Write-Host "Checking gcloud authentication and project access..." -ForegroundColor Cyan
Invoke-Gcloud @("config", "set", "project", $ProjectId)

$ProjectNumber = (& gcloud projects describe $ProjectId --format="value(projectNumber)").Trim()
$DeployerEmail = "$DeployerServiceAccountId@$ProjectId.iam.gserviceaccount.com"
$RuntimeEmail = "$RuntimeServiceAccountId@$ProjectId.iam.gserviceaccount.com"
$ProviderResource = "projects/$ProjectNumber/locations/global/workloadIdentityPools/$PoolId/providers/$ProviderId"
$PoolResource = "projects/$ProjectNumber/locations/global/workloadIdentityPools/$PoolId"
$RepositoryPrincipal = "principalSet://iam.googleapis.com/$PoolResource/attribute.repository_id/$GitHubRepositoryId"
$CloudBuildServiceAccount = "$ProjectNumber@cloudbuild.gserviceaccount.com"

Write-Host "Enabling required APIs..." -ForegroundColor Cyan
Invoke-Gcloud @("services", "enable", "iam.googleapis.com", "iamcredentials.googleapis.com", "sts.googleapis.com", "cloudresourcemanager.googleapis.com", "run.googleapis.com", "artifactregistry.googleapis.com", "cloudbuild.googleapis.com", "aiplatform.googleapis.com")

function Ensure-ServiceAccount {
  param([string] $AccountId, [string] $DisplayName)
  $prevEap = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  & gcloud iam service-accounts describe "$AccountId@$ProjectId.iam.gserviceaccount.com" --project=$ProjectId 2>&1 | Out-Null
  $ErrorActionPreference = $prevEap
  if ($LASTEXITCODE -ne 0) {
    Invoke-Gcloud @("iam", "service-accounts", "create", $AccountId, "--project=$ProjectId", "--display-name=$DisplayName")
  } else {
    Write-Host "Service account exists: $AccountId" -ForegroundColor DarkGray
  }
}

Ensure-ServiceAccount $DeployerServiceAccountId "TrustLens GitHub Actions deployer"
Ensure-ServiceAccount $RuntimeServiceAccountId "TrustLens Cloud Run runtime"

Write-Host "Granting runtime Vertex AI permission..." -ForegroundColor Cyan
Invoke-Gcloud @("projects", "add-iam-policy-binding", $ProjectId, "--member=serviceAccount:$RuntimeEmail", "--role=roles/aiplatform.user", "--condition=None")

Write-Host "Granting deployer permissions..." -ForegroundColor Cyan
Invoke-Gcloud @("projects", "add-iam-policy-binding", $ProjectId, "--member=serviceAccount:$DeployerEmail", "--role=roles/run.admin", "--condition=None")
Invoke-Gcloud @("projects", "add-iam-policy-binding", $ProjectId, "--member=serviceAccount:$DeployerEmail", "--role=roles/artifactregistry.writer", "--condition=None")
Invoke-Gcloud @("projects", "add-iam-policy-binding", $ProjectId, "--member=serviceAccount:$DeployerEmail", "--role=roles/cloudbuild.builds.editor", "--condition=None")
Invoke-Gcloud @("projects", "add-iam-policy-binding", $ProjectId, "--member=serviceAccount:$DeployerEmail", "--role=roles/serviceusage.serviceUsageAdmin", "--condition=None")
Invoke-Gcloud @("iam", "service-accounts", "add-iam-policy-binding", $RuntimeEmail, "--project=$ProjectId", "--member=serviceAccount:$DeployerEmail", "--role=roles/iam.serviceAccountUser")

# Cloud Build pushes the image, so its build identity needs Artifact Registry write access.
Invoke-Gcloud @("projects", "add-iam-policy-binding", $ProjectId, "--member=serviceAccount:$CloudBuildServiceAccount", "--role=roles/artifactregistry.writer", "--condition=None")

Write-Host "Creating Workload Identity Pool if needed..." -ForegroundColor Cyan
& gcloud iam workload-identity-pools describe $PoolId --project=$ProjectId --location=global *> $null
if ($LASTEXITCODE -ne 0) {
  Invoke-Gcloud @("iam", "workload-identity-pools", "create", $PoolId, "--project=$ProjectId", "--location=global", "--display-name=GitHub Actions pool", "--description=Federation for TrustLens GitHub Actions")
} else {
  Write-Host "Workload Identity Pool exists: $PoolId" -ForegroundColor DarkGray
}

$Mapping = "google.subject=assertion.sub,attribute.repository_id=assertion.repository_id,attribute.repository_owner_id=assertion.repository_owner_id,attribute.ref=assertion.ref,attribute.event_name=assertion.event_name"
$Condition = "assertion.repository_id == '$GitHubRepositoryId' && (assertion.event_name == 'push' || assertion.event_name == 'workflow_dispatch') && assertion.ref == 'refs/heads/main'"

Write-Host "Creating or updating GitHub OIDC provider..." -ForegroundColor Cyan
& gcloud iam workload-identity-pools providers describe $ProviderId --project=$ProjectId --location=global --workload-identity-pool=$PoolId *> $null
if ($LASTEXITCODE -ne 0) {
  Invoke-Gcloud @("iam", "workload-identity-pools", "providers", "create-oidc", $ProviderId, "--project=$ProjectId", "--location=global", "--workload-identity-pool=$PoolId", "--display-name=GitHub OIDC provider", "--issuer-uri=https://token.actions.githubusercontent.com/", "--attribute-mapping=$Mapping", "--attribute-condition=$Condition")
} else {
  Write-Host "OIDC provider exists: $ProviderId. Inspect it before changing it." -ForegroundColor Yellow
}

Write-Host "Allowing only this GitHub repository to impersonate the deployer..." -ForegroundColor Cyan
Invoke-Gcloud @("iam", "service-accounts", "add-iam-policy-binding", $DeployerEmail, "--project=$ProjectId", "--role=roles/iam.workloadIdentityUser", "--member=$RepositoryPrincipal")

Write-Host "Bootstrap complete." -ForegroundColor Green
Write-Host "GitHub variable GCP_PROJECT_ID: $ProjectId"
Write-Host "GitHub variable GCP_REGION: $Region"
Write-Host "GitHub secret GCP_WORKLOAD_IDENTITY_PROVIDER: $ProviderResource"
Write-Host "GitHub secret GCP_DEPLOYER_SERVICE_ACCOUNT: $DeployerEmail"
Write-Host "GitHub secret GCP_RUNTIME_SERVICE_ACCOUNT: $RuntimeEmail"
Write-Host "GitHub repository restriction: $GitHubOwner/$GitHubRepo (numeric ID $GitHubRepositoryId)"
