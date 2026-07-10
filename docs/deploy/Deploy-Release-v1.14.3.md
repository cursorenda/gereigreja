# Deploy & Release Guide — Gereigreja v1.14.3

## Objetivo
Publicar o pacote de padronização documental da engenharia e produto.

## Checklist
- [x] Documentos novos incluídos
- [x] CHANGELOG atualizado
- [x] Release summary criado
- [x] Commit da release realizado
- [x] Push para `origin/master`
- [ ] GitHub Release (opcional, conforme fluxo)

## Escopo da Release
- `docs/backend/`
- `docs/frameworks/`
- `docs/arquitetura/`
- `docs/produto/`
- `CHANGELOG.md`
- `RELEASE_v1.14.3_SUMMARY.md`

## Comandos de Publicação
```bash
git add CHANGELOG.md RELEASE_v1.14.3_SUMMARY.md docs/backend docs/frameworks docs/arquitetura docs/produto docs/deploy/Deploy-Release-v1.14.3.md
git commit -m "v1.14.3: padronizacao documental de engenharia e produto"
git push origin master
```

## Observações
- Release documental, sem migrações.
- Deploy no Render é acionado pelo push, conforme configuração padrão do projeto.
