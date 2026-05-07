$ErrorActionPreference = 'Stop'
$env:PYTHONWARNINGS = 'ignore'

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$pythonExe = Join-Path $projectRoot '.venv\Scripts\python.exe'
$logDir = Join-Path $projectRoot 'logs'
$logFile = Join-Path $logDir 'whatsapp_automations.log'

if (!(Test-Path $pythonExe)) {
    throw "Python do ambiente virtual nao encontrado em $pythonExe"
}

if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
Add-Content -Path $logFile -Value "[$timestamp] Inicio da automacao diaria de WhatsApp"

Push-Location $projectRoot
try {
    & $pythonExe -W ignore manage.py enviar_whatsapp_automatico --tipo aniversariantes 2>&1 | Tee-Object -FilePath $logFile -Append
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao executar automacao de aniversariantes. Exit code: $LASTEXITCODE"
    }

    & $pythonExe -W ignore manage.py enviar_whatsapp_automatico --tipo lembrete_eventos 2>&1 | Tee-Object -FilePath $logFile -Append
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao executar automacao de lembrete de eventos. Exit code: $LASTEXITCODE"
    }

    $done = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Add-Content -Path $logFile -Value "[$done] Automacao diaria finalizada com sucesso"
}
catch {
    $failed = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Add-Content -Path $logFile -Value "[$failed] ERRO: $($_.Exception.Message)"
    throw
}
finally {
    Pop-Location
}
