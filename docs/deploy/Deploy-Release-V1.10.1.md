# Deploy & Release Guide — Gereigreja v1.10.1

## 📋 Pre-Deploy Checklist

- [x] Documentação completa em `/docs/`
- [x] CHANGELOG.md atualizado com versão nova
- [x] Versão validada no topo do CHANGELOG.md
- [x] Testes locais passando
- [x] Migrations prontas (se houver)
- [ ] GitHub release criada
- [ ] Render deployment acionado

---

## 🚀 Deployment Steps

### 1. Local Validation

```bash
# Ativar venv
.venv\Scripts\Activate.ps1

# Executar testes
python manage.py test comunicacao

# Verificar migrações
python manage.py showmigrations

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

### 2. Version Check

```bash
# Verificar versão no topo do CHANGELOG
# A primeira linha de versão deve ser:
# ## v1.10.1 — 09/05/2026
```

### 3. Git Commit & Push

```bash
git add CHANGELOG.md docs/automacao/WhatsApp-Bulk-Celular-Edit.md README.md
git commit -m "v1.10.1: WhatsApp Bulk Celular Edit com filtros avançados"
git push origin main
```

### 4. Create GitHub Release

```bash
# No repositório GitHub:
# - Tag: v1.10.1
# - Title: "v1.10.1 - WhatsApp Bulk Celular Edit"
# - Copy changelog entry from CHANGELOG.md para description
```

### 5. Render Deployment

**Opção A: Automático (via webhook)**
- Push para `main` → Render detecta automaticamente
- Logs disponíveis em: https://dashboard.render.com/

**Opção B: Manual via Render Dashboard**
- Ir para: https://dashboard.render.com/services
- Selecionar serviço Gereigreja
- Clicar "Manual Deploy" → escolher branch "main"

### 6. Post-Deployment Validation

```bash
# SSH into Render (se necessário)
# Verificar logs de migração
# Testar rota: /comunicacao/whatsapp/massa/editar-celulares/
# Confirmar WhatsApp message delivery (health check)
```

---

## 🔄 Rollback Procedure

Se algo falhar:

```bash
# 1. No Render, redeploy a versão anterior
# 2. Revert commit local
git revert <commit_hash_v1.10.1>
git push origin main
# 3. Render redeploya automaticamente
```

---

## 📊 Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.10.1 | 09/05/2026 | WhatsApp Bulk Celular, locale fix |
| 1.10.0 | 05/05/2026 | Assinaturas, planos, funil |
| 1.8.78 | 21/04/2026 | Bulk edit, permissões |

---

## 🔐 Environment Variables (Render)

Garantir que estão definidas:

```env
DEBUG=False
ALLOWED_HOSTS=gereigreja.onrender.com
SECRET_KEY=<long_random_key>
DATABASE_URL=postgresql://...
CLOUDINARY_CLOUD_NAME=...
WAHA_API_KEY=...
WAHA_API_URL=https://devlikeaprowaha-production-83c4.up.railway.app
```

---

## 📝 Deployment Log Template

```
[DATE] v1.10.1 Deploy Started
- Commit: <hash>
- Branch: main
- Services affected:
  - comunicacao (WhatsApp bulk edit)
  - secretaria (Membro.celular)
- Migrations: None
- Static files: Recompiled
- Tests: ✅ Passed
- Status: ✅ LIVE
```

---

## 🆘 Troubleshooting

### Erro: "Locale-formatted POST keys"
- **Solução**: Versão 1.10.1 já corrige. Se persistir, limpar browser cache.

### Erro: "Página em branco em /comunicacao/whatsapp/massa/editar-celulares/"
- **Solução**: Verificar permissões (`@page_access_required('comunicacao')`)

### Erro: "CSRF token missing"
- **Solução**: Garantir que {% csrf_token %} está no form (já está no template)

---

**Maintenance Window**: Desativado (zero-downtime deploy via Render)  
**Estimated Deploy Time**: 2-5 min  
**Rollback Time**: < 1 min  

---

**Criado**: 09/05/2026  
**Versão**: v1.10.1
