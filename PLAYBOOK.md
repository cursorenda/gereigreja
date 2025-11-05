# Playbook de Deploy — Squashed Migrations (SECRETARIA)

Este documento descreve, em passos reproduzíveis, como aplicar uma(s) migração(ões) "squashed" para o app `secretaria` (ou apps dependentes) em ambientes que já têm histórico de migrações aplicadas.

IMPORTANTE: siga este playbook passo-a-passo. Faça backup completo do banco de produção antes de qualquer ação em produção.

SUMÁRIO
- Objetivo
- Pré-requisitos
- Passos em Staging
- Passos em Produção (cenário com histórico de migrações já aplicadas)
- Comandos úteis (PowerShell)
- Verificações pós-deploy (smoke checks)
- Rollback
- Checklist

---

OBJETIVO
- Permitir aplicar um squashed migration sem corromper bancos que já possuem migrações históricas aplicadas.

PRÉ-REQUISITOS
- Acesso SSH / CI com credenciais para executar commands no servidor de staging/produção.
- Ferramentas: Python (virtualenv do projeto), `psql`/`pg_dump` (se usar Postgres), permissões para criar dumps.
- Backup automático testado: testar restauração do backup em ambiente separado.

PASSOS EM STAGING (recomendado)
1. Preparar branch PR com o(s) squashed migration(s) e documentação (este playbook + notes no PR).
2. Fazer deploy do branch em staging (code + migrations) e garantir que o ambiente staging foi provisionado a partir de snapshot da produção.
3. No staging, verificar migrações aplicadas:
   ```powershell
   .\.venv\Scripts\python.exe manage.py showmigrations secretaria
   .\.venv\Scripts\python.exe manage.py migrate --plan
   ```
4. Tentar aplicar `migrate` normalmente. Se `migrate` aplicar sem erros, rodar testes e smoke checks.
5. Se `migrate` falhar por operações duplicadas, testar a abordagem `--fake` no squashed (ver Produção abaixo) e documentar exatamente quais comandos funcionaram.

PASSOS EM PRODUÇÃO (cenário com histórico já aplicado)
1. Janela de manutenção: comunicar time e marcar downtime se necessário.
2. Backup completo do banco (pg_dump ou snapshot). Verificar integridade do backup.
3. Deploy do código (branch do PR) no servidor.
4. Verificar migrações aplicadas em produção:
   ```powershell
   .\.venv\Scripts\python.exe manage.py showmigrations secretaria
   ```
5. Decidir ação para o squashed migration:
   - Se as migrações antigas (0001..00NN) já foram aplicadas: marcar o squashed como aplicado com `--fake`.
     ```powershell
     .\.venv\Scripts\python.exe manage.py migrate secretaria <nome_da_migration_squash> --fake
     .\.venv\Scripts\python.exe manage.py migrate
     ```
   - Se o squashed puder ser aplicado normalmente (testado em staging): rodar `migrate` normalmente.
6. Executar smoke tests e verificações (counts, endpoints, health checks).
7. Monitorar logs por 30-60 minutos.

COMANDOS ÚTEIS (PowerShell)
- Listar migrações:
  ```powershell
  .\.venv\Scripts\python.exe manage.py showmigrations
  ```
- Ver plano de migrate:
  ```powershell
  .\.venv\Scripts\python.exe manage.py migrate --plan
  ```
- Fake apply do squashed (trocar pelo nome real):
  ```powershell
  .\.venv\Scripts\python.exe manage.py migrate secretaria 0001_squashed_0022_alter_acompanhamentovisita_membro_and_more --fake
  .\.venv\Scripts\python.exe manage.py migrate
  ```
- Exemplo de dump (executar em ambiente que tenha pg_dump configurado; troque credenciais):
  ```powershell
  pg_dump -h <host> -p <port> -U <user> -d <db> -F c -b -v -f "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').dump"
  ```

VERIFICAÇÕES PÓS-DEPLOY (SMOKE CHECKS)
- `showmigrations` para confirmar estado.
- Queries rápidas:
  ```powershell
  .\.venv\Scripts\python.exe manage.py shell -c "from secretaria.models import Membro; print(Membro.objects.count())"
  .\.venv\Scripts\python.exe manage.py shell -c "from eventos.models import Evento; print(Evento.objects.count())"
  ```
- Acessar principais endpoints web e validar HTTP 200.

ROLLBACK
- Se apenas marcou migrações com `--fake` (nenhuma alteração física no schema): remover o fake (ou rodar migrate zero --fake) e re-deploy do código anterior.
- Se alterações físicas ocorreram e houve corrupção: restaurar backup (pg_restore ou snapshot restore). Testar a restauração antes de usá-la.

CHECKLIST PARA O DIA DO DEPLOY
- [ ] Backup completo da base de produção criado e verificado
- [ ] Branch PR mergeado e código deployado (quase-idêntico ao testado em staging)
- [ ] Janela de manutenção anunciada e times notificados
- [ ] showmigrations anotado (quem rodou e hora)
- [ ] Executado:
  - .\.venv\Scripts\python.exe manage.py migrate secretaria <nome_squash> --fake
  - .\.venv\Scripts\python.exe manage.py migrate
- [ ] Smoke tests e verificação de contagens/queries
- [ ] Monitoramento ativo por 60 minutos

CONSIDERAÇÕES FINAIS E MELHORIAS
- Automatizar o playbook via script CI/CD (ex.: job que roda em staging e bloqueia produção até aprovação manual).
- Documentar passos exatos no PR (nome da migration, SHA do commit usado no staging, etc.).
- Evitar editar migrações aplicadas publicamente sem comunicação e plano de rollback.

---

Se desejar, existe um script PowerShell interativo complementar em `scripts/deploy_squash_playbook.ps1` que ajuda a executar as etapas de verificação e (com confirmação explícita) aplicar o `--fake` e migrar.
