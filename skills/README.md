# Skills do Gereigreja

Este diretório contém instruções organizadas para o agente IA usar **automaticamente** quando necessário.

## 🎯 Como Funciona

Skills são como "manuais especializados" que o agente consulta quando detecta que precisa:
1. **Progressive Disclosure**: Agente lê apenas nome + descrição (economiza tokens)
2. **Ativação Automática**: Carrega instruções completas só quando necessário
3. **Contexto Específico**: Cada skill tem exemplos práticos e regras de negócio

## 📚 Skills Disponíveis

| Nome da Skill | Quando Usar |
|---------------|-------------|
| **gerenciando-financeiro** | Receitas, despesas, contas bancárias, relatórios |
| **fazendo-deploy** | Criar versões, deploy, release notes |
| **gerenciando-backup** | Backup e restauração do banco PostgreSQL |
| **gerenciando-eventos** | Criar eventos, inscrições, presença |
| **enviando-comunicacao** | E-mails, SMS, notificações em massa |
| **gerenciando-secretaria** | Cadastro de pessoas, famílias, histórico |
| **configurando-sistema** | Organizações, usuários, permissões, integrações |
| **gerenciando-escola-biblica** | Turmas, alunos, professores, frequência, aulas |
| **gerenciando-agenda** | Compromissos, reuniões, calendário da igreja |
| **gerenciando-suporte** | Tickets de suporte, atendimento, base de conhecimento |

## 🏗️ Anatomia de uma Skill

```
minha-skill/
├── SKILL.md         ← Obrigatório (YAML + instruções)
├── scripts/         ← Opcional (código executável)
├── references/      ← Opcional (documentação extra)
└── assets/          ← Opcional (templates, imagens)
```

### Estrutura do SKILL.md

```yaml
---
name: "gerenciando-algo"       # minúsculas, hífen, verbo gerúndio
description: "Faz X, Y e Z. Use quando trabalhar com A, B ou C."  # máx 24 palavras
---

# Quando Usar Esta Skill
- Lista de cenários

## Estrutura de Dados
- Models, campos, relacionamentos

## Regras de Negócio
- Validações importantes

## Exemplos de Uso
- Código prático (one-shot, few-shot)

## Boas Práticas
- Recomendações técnicas
```

## 🚀 Vantagens do Sistema de Skills

- ✅ **Economia de Tokens**: Agente lê apenas o necessário
- ✅ **Performance**: Pode ter 100+ skills sem deixar lento
- ✅ **Consistência**: Padrão de código uniforme em todos os projetos
- ✅ **Reutilização**: Skills funcionam em projetos similares
- ✅ **Manutenibilidade**: Fácil atualizar conhecimento do agente

## 📖 Documentação Complementar

- [`copilot-instructions.md`](copilot-instructions.md) - Instruções gerais do projeto
- [`contexto_gereigreja.md`](contexto_gereigreja.md) - Contexto completo do sistema
- [`deploy/references/`](deploy/references/) - Templates de deploy e release notes

## 🔧 Como Criar Novas Skills

1. Identifique um padrão que se repete em seus projetos
2. Crie pasta `skills/nome-da-skill/`
3. Crie `SKILL.md` com YAML + instruções
4. Adicione exemplos práticos de código
5. (Opcional) Adicione scripts, references ou assets

---

**Padrão seguido**: Breno Vieira LionLab - Context Engineering
