[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Project,
    [string] $RunRegion = 'europe-north2',
    [string] $RuntimeRegion = 'europe-west4',
    [string] $ModelLocation = 'global',
    [string] $ModelArmorTemplate = 'bastion-guardrail',
    [string] $ModelArmorLocation = 'europe-west4',
    [Parameter(Mandatory)] [string] $MemoryAgentEngineId,
    [Parameter(Mandatory)] [string] $RuntimeAgentEngineId,
    [string] $FindingHmacSecret = 'bastion-finding-hmac',
    [string] $A2ASecret = 'bastion-a2a-shared-secret',
    [switch] $SkipSmoke
)

$ErrorActionPreference = 'Stop'
$GitBash = 'C:\Program Files\Git\bin\bash.exe'
if (-not (Test-Path -LiteralPath $GitBash)) {
    throw 'Git for Windows Bash is required at C:\Program Files\Git\bin\bash.exe'
}

function Ensure-GeneratedSecret([string] $Name) {
    gcloud secrets describe $Name --project=$Project *> $null
    if ($LASTEXITCODE -eq 0) { return }
    gcloud secrets create $Name --project=$Project --replication-policy=automatic --quiet | Out-Null
    $Bytes = [byte[]]::new(32)
    [Security.Cryptography.RandomNumberGenerator]::Fill($Bytes)
    $Value = [Convert]::ToHexString($Bytes).ToLowerInvariant()
    $Temp = New-TemporaryFile
    try {
        Set-Content -LiteralPath $Temp.FullName -Value $Value -NoNewline -Encoding ascii
        gcloud secrets versions add $Name --project=$Project --data-file=$Temp.FullName --quiet | Out-Null
    }
    finally {
        Remove-Item -LiteralPath $Temp.FullName -Force
    }
}

$env:GCP_PROJECT_ID = $Project
$env:GCP_PROJECT_NUMBER = gcloud projects describe $Project --format='value(projectNumber)'
$env:GCP_REGION = $RunRegion
$env:AGENT_RUNTIME_REGION = $RuntimeRegion
$env:AGENT_REGISTRY_REGION = $RuntimeRegion
$env:GOOGLE_CLOUD_LOCATION = $ModelLocation
$env:MODEL_ARMOR_TEMPLATE_ID = $ModelArmorTemplate
$env:MODEL_ARMOR_LOCATION = $ModelArmorLocation
$env:BASTION_MEMORY_AGENT_ENGINE_ID = $MemoryAgentEngineId
$env:BASTION_FINDING_HMAC_SECRET = $FindingHmacSecret
$env:BASTION_A2A_SHARED_SECRET_ID = $A2ASecret
$env:BASTION_SESSION_SERVICE_URI = "agentengine://projects/$($env:GCP_PROJECT_NUMBER)/locations/$RuntimeRegion/reasoningEngines/$MemoryAgentEngineId"
$env:BASTION_MEMORY_SERVICE_URI = $env:BASTION_SESSION_SERVICE_URI
$env:PUBSUB_TOPIC = 'bastion-investigations'
$env:BASTION_AGENT_GATEWAY = 'bastion-egress'
$env:BASTION_RUNTIME_AGENT_ENGINE_ID = $RuntimeAgentEngineId

gcloud services enable secretmanager.googleapis.com --project=$Project --quiet
Ensure-GeneratedSecret $FindingHmacSecret
Ensure-GeneratedSecret $A2ASecret

python -m infrastructure.provision --apply
gcloud secrets add-iam-policy-binding $FindingHmacSecret --project=$Project `
    --member="serviceAccount:access-auditor-sa@$Project.iam.gserviceaccount.com" `
    --role=roles/secretmanager.secretAccessor --quiet | Out-Null
foreach ($Account in @('access-auditor-sa', 'escalation-agent-sa')) {
    gcloud secrets add-iam-policy-binding $A2ASecret --project=$Project `
        --member="serviceAccount:$Account@$Project.iam.gserviceaccount.com" `
        --role=roles/secretmanager.secretAccessor --quiet | Out-Null
}
& $GitBash infrastructure/deploy.sh
python -m infrastructure.provision_gateway --apply

$Runtime = python -m infrastructure.deploy_agent_runtime | ConvertFrom-Json
$env:BASTION_RUNTIME_AGENT_ENGINE_ID = ($Runtime.name -split '/')[-1]
python -m infrastructure.configure_agent_runtime
python -m infrastructure.provision_observability
python -m infrastructure.verify_fleet
if (-not $SkipSmoke) {
    python -m infrastructure.smoke_test
}

Write-Host "Bastion bootstrap complete. Runtime Agent Engine: $($env:BASTION_RUNTIME_AGENT_ENGINE_ID)"
