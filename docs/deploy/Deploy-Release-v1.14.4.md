# Deploy & Release Guide — Gereigreja v1.14.4

## Objetivo
Publicar melhorias premium no módulo WhatsApp em Massa: listas salvas, autoapliação, favorita com carregamento automático, contadores por lista e redesign de jornadas automáticas.

## Checklist de Pré-Deploy

- [x] Código testado localmente
- [x] Migrações criadas e aplicadas
- [x] `python manage.py check` executado sem erros
- [x] CHANGELOG atualizado com v1.14.4
- [x] Release summary criado
- [x] Documentação refatorada para UI/UX premium

## Escopo da Release

### Código Funcional
- `comunicacao/models.py` — novo modelo `WhatsAppFiltroPerfil`
- `comunicacao/views/whatsapp.py` — lógica de perfis, contadores, autoapliação
- `comunicacao/urls.py` — rotas de salvar/excluir perfil
- `comunicacao/migrations/0009_*.py` e `0010_*.py` — schema updates

### UI/UX e Templates
- `comunicacao/templates/comunicacao/whatsapp/form_whatsapp_massa.html` — bloco "Listas salvas" reorganizado, filtros recolhíveis
- `comunicacao/templates/comunicacao/partials/_automacao_aniversariantes_card.html` — cards em padrão premium, 4 em linha, tabela harmonizada

### Documentação
- `RELEASE_v1.14.4_SUMMARY.md` — documento executivo da release
- `docs/deploy/Deploy-Release-v1.14.4.md` — este arquivo

## Passos de Publicação

### 1. Commit de Código + Docs
```bash
git add \
  comunicacao/models.py \
  comunicacao/views/whatsapp.py \
  comunicacao/urls.py \
  comunicacao/migrations/0009_*.py \
  comunicacao/migrations/0010_*.py \
  comunicacao/templates/comunicacao/whatsapp/form_whatsapp_massa.html \
  comunicacao/templates/comunicacao/partials/_automacao_aniversariantes_card.html \
  CHANGELOG.md \
  RELEASE_v1.14.4_SUMMARY.md \
  docs/deploy/Deploy-Release-v1.14.4.md

git commit -m "v1.14.4: WhatsApp Premium - Listas Salvas, Autoapliação, Favorita e UI Refinada"
git push origin master
```

### 2. Deploy Automático Render
O Render detectará o push em `master` e executará:
1. Build com dependências (sem mudanças de requirements.txt nesta versão)
2. Migrações: `python manage.py migrate comunicacao`
3. Coleta de estáticos: `python manage.py collectstatic --noinput`
4. Restart do serviço

### 3. Validação Pós-Deploy (Checklist)

- [ ] Página `/comunicacao/whatsapp/massa/` carrega sem erro
- [ ] Bloco "Listas salvas" renderiza corretamente
- [ ] Seletor de lista aplica automaticamente ao trocar
- [ ] Contador de aptos exibe para cada lista
- [ ] Favorita é carregada automaticamente ao abrir a página
- [ ] Botão "Filtrar destinatários" exibe corretamente no bloco recolhível
- [ ] Jornadas automáticas mostram 4 cards em linha (desktop)
- [ ] Badge com lista ativa exibe no topo do bloco
- [ ] `python manage.py check` retorna 0 issues

## Comandos de Teste Local (Antes do Push)

```bash
# Teste de migrações
python manage.py migrate --plan comunicacao

# Aplicar migrações em dev
python manage.py migrate comunicacao

# Verificar integridade
python manage.py check comunicacao

# Rodar servidor e testar
python manage.py runserver

# Acessar a página
# → http://localhost:8000/comunicacao/whatsapp/massa/
```

## Observações

- **Sem breaking changes**: retrocompatível com versões anteriores.
- **Dados preservados**: usuários mantêm suas listas salvas se existirem (primeira vez será vazio).
- **Deploy suave**: migrações são simples e não bloqueiam operação.
- **Monitoramento**: verificar `logs/django_errors.log` por 30 minutos após deploy.

## Rollback (se necessário)

```bash
git revert HEAD
git push origin master
# Render reverterá automaticamente para versão anterior

# Ou, se preferir rollback manual:
python manage.py migrate comunicacao 0008  # reverte para versão anterior à v1.14.4
```

## Contato / Suporte
Dúvidas sobre deploy? Verifique `docs/deploy/` e `skills/deploy/SKILL.md`.

---

**Versão**: 1.14.4 | **Data**: 17/07/2026 | **Status**: Pronto para Produção
