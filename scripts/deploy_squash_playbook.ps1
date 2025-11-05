<#
  deploy_squash_playbook.ps1

  Script interativo de apoio ao deploy de squashed migrations.
  Funciona em PowerShell no Windows. Executar a partir da raiz do repositório.

  Atenção: o script NÃO executa backups automaticamente. Faça backup antes de qualquer ação em produção.
  Use-o como um assistente — ele solicitará confirmações antes de `--fake` ou `migrate`.
#>

param()

function Run-Command {
    param($cmd)
    Write-Host "-> Executando: $cmd" -ForegroundColor Cyan
    & cmd /c $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Comando falhou com exit code $LASTEXITCODE" -ForegroundColor Red
        return $false
    }
    return $true
}

Write-Host "Deploy Squash Playbook - Assistente" -ForegroundColor Green

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "Atenção: não encontrei $python. Ajuste a variável python no script se necessário." -ForegroundColor Yellow
}

$app = Read-Host "Nome do app (ex: secretaria)"
$migration = Read-Host "Nome da migration squash (ex: 0001_squashed_0022_alter_acompanhamentovisita_membro_and_more)"
$env = Read-Host "Ambiente (staging/production). Atenção: em production, faça backup antes de prosseguir"

Write-Host "Fase 1: Mostrar migrações e plano (apenas leitura)" -ForegroundColor Cyan
Run-Command "$python manage.py showmigrations $app"
Run-Command "$python manage.py migrate --plan"

if ($env -eq 'production') {
    Write-Host "Você está no ambiente PRODUCTION. Confirme que backup foi feito e verificado." -ForegroundColor Yellow
    $ok = Read-Host "Backup feito e verificado? (s/n)"
    if ($ok -ne 's') { Write-Host "Abortando."; exit 1 }
}

$doFake = Read-Host "Deseja marcar a migration squashed como aplicada com --fake? (s/n)"
if ($doFake -eq 's') {
    Write-Host "Fazendo: migrate $app $migration --fake" -ForegroundColor Cyan
    $cmd = "$python manage.py migrate $app $migration --fake"
    if (-not (Run-Command $cmd)) { Write-Host 'Falha no fake apply. Abortando.' -ForegroundColor Red; exit 1 }
    Write-Host "Fake apply OK. Agora aplicando migrations pendentes globais..." -ForegroundColor Green
    if (-not (Run-Command "$python manage.py migrate")) { Write-Host 'Falha ao rodar migrate global.' -ForegroundColor Red; exit 1 }
} else {
    $doMigrate = Read-Host "Deseja rodar migrate normalmente agora? (s/n)"
    if ($doMigrate -eq 's') {
        if (-not (Run-Command "$python manage.py migrate")) { Write-Host 'Falha ao rodar migrate.' -ForegroundColor Red; exit 1 }
    } else {
        Write-Host "Nenhuma ação de migrate executada. Verifique manualmente e rode os comandos necessários." -ForegroundColor Yellow
    }
}

Write-Host "Executando smoke checks básicos..." -ForegroundColor Cyan
Run-Command "$python manage.py shell -c \"from secretaria.models import Membro; print('Membros:', Membro.objects.count())\""
Run-Command "$python manage.py shell -c \"from eventos.models import Evento; print('Eventos:', Evento.objects.count())\""

Write-Host "Se tudo OK, monitore logs por 30-60 minutos." -ForegroundColor Green
Write-Host "Fim do assistente." -ForegroundColor Green
