# Deploy & Release Guide — Gereigreja v1.14.2

## 📋 Pre-Deploy Checklist

- [x] Documentação da release criada
- [x] CHANGELOG.md atualizado com a nova versão
- [x] Versionamento validado no topo do CHANGELOG.md
- [x] Testes/validações locais executados
- [x] Migração do Hinário aplicada localmente
- [ ] GitHub release criada
- [ ] Push para `main` executado
- [ ] Deploy automático no Render validado

---

## 🚀 Deployment Steps

### 1. Validação Local

```bash
C:/Gereigreja/.venv/Scripts/python.exe manage.py makemigrations hinario --check --dry-run
C:/Gereigreja/.venv/Scripts/python.exe manage.py check
```

### 2. Version Check

- Confirmar que a primeira entrada do `CHANGELOG.md` é `v1.14.2`.
- Confirmar que a release summary `RELEASE_v1.14.2_SUMMARY.md` está presente.

### 3. Git Commit & Push

```bash
git add CHANGELOG.md RELEASE_v1.14.2_SUMMARY.md docs/deploy/Deploy-Release-v1.14.2.md painel_desenvolvedor/views.py painel_desenvolvedor/urls.py painel_desenvolvedor/templates/painel_desenvolvedor/fila_compliance_hinos.html hinario/models.py hinario/admin.py hinario/selectors.py hinario/services.py hinario/views.py hinario/templates/hinario/catalogo.html hinario/templates/hinario/detalhe.html hinario/migrations/0002_hinotema_hino_temas.py
git commit -m "v1.14.2: Hinario premium com compliance, temas e UX otimizada"
git push origin main
```

### 4. GitHub Release

- Tag: `v1.14.2`
- Título: `v1.14.2 - Hinário Premium`
- Descrição: copiar o conteúdo do topo do `CHANGELOG.md`

### 5. Render Deployment

- Push para `main` aciona o deploy automático via webhook.
- Se necessário, executar manual deploy no dashboard do Render.

### 6. Post-Deployment Validation

- Acessar o catálogo do Hinário em `/portal/hinario/`.
- Acessar o detalhe de um hino e confirmar a letra em destaque.
- Validar a fila de compliance em `/admin/painel-desenvolvedor/hinario-compliance/`.
- Confirmar filtros por tema e ações em lote.

---

## 🔄 Rollback Procedure

Se necessário:

```bash
git revert <commit_hash_v1.14.2>
git push origin main
```

Depois, redeploy da versão anterior no Render.

---

## 📊 Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.14.2 | 10/07/2026 | Hinário premium com compliance, temas e UX otimizada |
| 1.14.1 | 08/07/2026 | Hotfix financeiro do sistema |
| 1.14.0 | 07/07/2026 | Knowledge base completa |

---

## 📝 Deployment Log Template

```text
[DATE] v1.14.2 Deploy Started
- Commit: <hash>
- Branch: main
- Services affected:
  - hinario
  - painel_desenvolvedor
  - secretaria
- Migrations: hinario.0002_hinotema_hino_temas
- Tests: ✅ Passed
- Status: ✅ LIVE
```
