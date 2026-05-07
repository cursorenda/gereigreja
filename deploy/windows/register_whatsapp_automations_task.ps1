param(
    [string]$TaskName = 'Gereigreja_WhatsApp_Automacoes_Diarias',
    [string]$ScheduleTime = '08:00'
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$scriptPath = Join-Path $projectRoot 'scripts\automation\run_whatsapp_automations.ps1'

if (!(Test-Path $scriptPath)) {
    throw "Script de execucao nao encontrado em $scriptPath"
}

$command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""

schtasks /Create /F /SC DAILY /ST $ScheduleTime /TN $TaskName /TR $command /RU SYSTEM | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Warning 'Nao foi possivel registrar com a conta SYSTEM. Tentando com o usuario atual.'
    schtasks /Create /F /SC DAILY /ST $ScheduleTime /TN $TaskName /TR $command | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao registrar a tarefa agendada '$TaskName'."
    }
}

schtasks /Query /TN $TaskName | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "A tarefa '$TaskName' nao foi localizada apos o registro."
}

Write-Host "Tarefa '$TaskName' registrada para rodar diariamente as $ScheduleTime"
