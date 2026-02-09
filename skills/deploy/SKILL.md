---
name: "fazendo-deploy"
description: "Cria versões, publica atualizações e gerencia deploys no Render. Use para versionamento, release notes ou deploy de mudanças."
---

# Quando Usar Esta Skill

Use esta skill quando:
- Criar nova versão do sistema
- Gerar release notes automaticamente
- Fazer deploy para produção
- Verificar mudanças pendentes (git)
- Preparar documentação de versão

## Fluxo de Deploy Completo

### 1. Verificar Mudanças Pendentes
```bash
# Ver status do git
git status

# Ver arquivos modificados
git diff

# Ver commits desde última versão
git log --oneline v1.0.9..HEAD
```

### 2. Criar Nova Versão
```python
# No admin do sistema: /admin/deploy/nova-versao/
# Preencher:
# - Número da versão (ex: 1.0.10)
# - Descrição das mudanças
# - Data de publicação
```

### 3. Atualizar CHANGELOG.md
```markdown
## v1.0.10 — 05/02/2026

### Novidades
- [Feature] Nova funcionalidade X
- [Feature] Melhoria em Y

### Correções
- [Fix] Corrigido bug em Z

### Técnico
- Atualização de dependências
```

### 4. Commit e Push
```bash
git add .
git commit -m "Release v1.0.10: [Descrição curta]"
git push origin main
```

### 5. Deploy Automático Render
O Render detecta push na main e:
1. Executa build
2. Instala dependências
3. Roda migrações
4. Coleta arquivos estáticos
5. Reinicia serviço

## Estrutura de Release Notes

### Template para Usuários
```markdown
# 🎉 Versão 1.0.10 - [Data]

## O que há de novo?

### 🚀 [Nome da Funcionalidade Principal]
[Descrição amigável do que mudou e benefício para o usuário]

### 📋 Outras Melhorias
- ✅ [Melhoria 1]
- ✅ [Melhoria 2]

## 💡 Dica de Uso
[Como usar a nova funcionalidade]

## 📞 Suporte
Dúvidas? Entre em contato!

---
**Versão**: 1.0.10 | **Data**: 05/02/2026
```

## Checklist Pré-Deploy

- [ ] Backup do banco criado
- [ ] Testes locais executados
- [ ] Migrações testadas
- [ ] CHANGELOG.md atualizado
- [ ] Release notes criadas
- [ ] Variáveis de ambiente conferidas
- [ ] Nenhum dado sensível no código

## Comandos Importantes

```bash
# Backup do banco
python manage.py dumpdata > backup.json

# Testar migrações
python manage.py migrate --plan

# Verificar erros
python manage.py check --deploy

# Coletar estáticos
python manage.py collectstatic --noinput
```

## Boas Práticas

1. **Sempre fazer backup antes de deploy crítico**
2. **Descrever mudanças de forma clara e objetiva**
3. **Versionar seguindo semântico**: MAJOR.MINOR.PATCH
4. **Testar localmente antes de dar push**
5. **Monitorar logs após deploy** (`logs/django_errors.log`)
6. **Não fazer deploy em horários de pico**
