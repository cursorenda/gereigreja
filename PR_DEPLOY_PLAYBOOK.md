Título: Playbook e script de deploy para Squashed Migrations (SECRETARIA)

Resumo
- Este PR adiciona o playbook de deploy (`PLAYBOOK.md`) e o script interativo (`scripts/deploy_squash_playbook.ps1`) que descrevem e automatizam, com confirmações, o processo seguro para aplicar squashed migrations do app `secretaria` em ambientes que já possuem histórico de migrations aplicadas.

O que não está incluído: o(s) squashed migration(s) foram arquivados em backups e não estão inclusos neste PR. A inclusão será feita em PRs separados após validação em staging.

Motivação
- Fornecer documentação e um processo repetível para aplicar squashed migrations com mínima chance de erro em produção.
- Fornecer ao DBA/ops um script interativo com confirmações manuais antes de executar ações destrutivas (`--fake`, `migrate`).

Checklist para reviewers / DBA
- [ ] Revisar `PLAYBOOK.md` e confirmar os passos de backup e rollback
- [ ] Revisar `scripts/deploy_squash_playbook.ps1` e confirmar permissões e caminhos
- [ ] Validar o fluxo completo em staging (restaurar dump de produção e seguir o playbook)
- [ ] Definir a estratégia final para o squashed migration (incluir no PR ou abrir PR separado)
- [ ] Aprovação explícita do DBA para uso de `migrate --fake` em produção (se aplicável)

Comandos de validação rápida (staging)
```powershell
# listar migrações da app secretaria
.\.venv\Scripts\python.exe manage.py showmigrations secretaria

# ver o plano de migrate
.\.venv\Scripts\python.exe manage.py migrate --plan

# aplicar migrate (testar em staging)
.\.venv\Scripts\python.exe manage.py migrate
```

Notas
- Se preferirem, eu posso também restaurar o arquivo de migration squashed dos backups e incluir em um PR separado para que possamos testar exatamente o mesmo artefato em staging antes de promover para produção.
- Para abrir o PR no GitHub eu posso ajudar com o comando `gh pr create --fill --body-file PR_DEPLOY_PLAYBOOK.md` se a CLI `gh` estiver disponível; caso contrário, basta colar o conteúdo deste arquivo na descrição do PR web.

---

(Arquivo gerado automaticamente por assistência para preparar o PR — depois do push, abra o PR no GitHub apontando `fix/secretaria-migrations` como branch de origem.)
