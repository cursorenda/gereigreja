Pasta:
docs/apps/

Arquivo:
04-Comunicacao.md

Documento:
GAP-04

Seção:
Apps

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 04 - Comunicação

> "Comunicação é um domínio de negócio orientado a campanhas, avisos e canais externos; a interface coordena, a regra de negócio vive nos Services e a leitura vive nos Selectors."

---

# Sumário

1. Objetivo
2. Escopo do App
3. Estrutura Oficial
4. Canais e Jornadas
5. Services e Selectors
6. Views e Templates
7. Segurança e Permissões
8. Testes e Validação
9. Checklist de Conclusão
10. Documentos Relacionados
11. Princípios Finais

---

# 1. Objetivo

Este documento consolida a arquitetura oficial do app Comunicação do GereIgreja.

Seu objetivo é registrar o estado atual do módulo, suas responsabilidades e os padrões obrigatórios para evolução futura.

O app Comunicação deve permanecer focado em campanhas, mensagens, avisos e integrações com canais externos.

---

# 2. Escopo do App

O app Comunicação atende quatro frentes principais:

- Home operacional da Comunicação;
- envio de e-mail em massa;
- envio e administração de WhatsApp;
- mural de avisos.

O domínio também inclui:

- previews de templates de e-mail;
- automacao de aniversariantes para WhatsApp e e-mail;
- configuração de WhatsApp por congregação;
- configuração global do WAHA;
- logs operacionais de WhatsApp;
- webhook de recebimento.

---

# 3. Estrutura Oficial

Estrutura consolidada do app:

```text
comunicacao/

forms.py
models.py
selectors.py
services.py
services_whatsapp.py
urls.py
utils.py
views/
    __init__.py
    home.py
    email.py
    logs.py
    mural.py
    whatsapp.py

templates/comunicacao/
tests/
```

Arquivos legados foram removidos após a migração para o pacote `views/`.

---

# 4. Canais e Jornadas

## Home

A Home da Comunicação apresenta indicadores operacionais, atalhos e visão geral do módulo.

## E-mail

Fluxos cobertos:

- visualização de templates;
- envio de e-mail em massa;
- configuracao da automacao de aniversariantes;
- prévia do template de e-mail em massa;
- prévia do template de e-mail de aniversario;
- prévia do template de redefinição de senha.

## WhatsApp

Fluxos cobertos:

- configuração por congregação;
- configuração global;
- envio em massa;
- envio automatico para aniversariantes;
- prévia de destinatários;
- edição em massa de celulares;
- teste de saúde do WAHA;
- webhook de recebimento;
- logs operacionais.

## Mural

Fluxos cobertos:

- lista de avisos;
- detalhe de aviso;
- criação;
- edição;
- exclusão.

---

# 5. Services e Selectors

## Selectors

Toda consulta reutilizável do módulo deve permanecer em [comunicacao/selectors.py](../../comunicacao/selectors.py).

Responsabilidades atuais:

- filtragem de audiência para e-mail;
- filtragem de audiência para WhatsApp;
- montagem de preview de destinatários;
- contexto da Home;
- consulta de logs de WhatsApp.

## Services

Toda regra de negócio do módulo deve permanecer em [comunicacao/services.py](../../comunicacao/services.py).

Responsabilidades atuais:

- envio de e-mail em massa;
- envio de WhatsApp em massa.

As integrações com WAHA permanecem apoiadas por [comunicacao/services_whatsapp.py](../../comunicacao/services_whatsapp.py).

---

# 6. Views e Templates

As Views do módulo passaram a seguir a organização por pacote:

- [comunicacao/views/home.py](../../comunicacao/views/home.py)
- [comunicacao/views/email.py](../../comunicacao/views/email.py)
- [comunicacao/views/logs.py](../../comunicacao/views/logs.py)
- [comunicacao/views/mural.py](../../comunicacao/views/mural.py)
- [comunicacao/views/whatsapp.py](../../comunicacao/views/whatsapp.py)

Os templates específicos do módulo permanecem dentro de `comunicacao/templates/comunicacao/`.

A interface segue o GereIgreja Design System, com sidebar lateral, breadcrumbs e CTA consistente.

---

# 7. Segurança e Permissões

Padrões obrigatórios:

- uso de autenticação nas rotas protegidas;
- validação de assinatura ativa;
- verificação de escopo por ministério e igreja;
- webhook com token dedicado;
- revisão de permissões antes de expor ações sensíveis.

Rotas sensíveis devem permanecer restritas por decorators e contexto adequado.

---

# 8. Testes e Validação

Cobertura mínima consolidada:

- smoke tests de rotas;
- smoke tests de imports dos módulos de views;
- smoke tests de acesso anônimo;
- validação de webhook com método incorreto;
- `manage.py check comunicacao`.

O módulo já possui testes básicos em:

- [comunicacao/tests/test_urls.py](../../comunicacao/tests/test_urls.py)
- [comunicacao/tests/test_views_imports.py](../../comunicacao/tests/test_views_imports.py)
- [comunicacao/tests/test_access_flow.py](../../comunicacao/tests/test_access_flow.py)
- [comunicacao/tests/test_functional_flows.py](../../comunicacao/tests/test_functional_flows.py)
- [comunicacao/tests/test_services.py](../../comunicacao/tests/test_services.py)

---

# 9. Checklist de Conclusão

Antes de considerar o app Comunicação concluído, validar:

- [x] e-mail em massa funcionando;
- [x] WhatsApp funcionando;
- [x] mural funcionando;
- [x] views modularizadas;
- [x] services e selectors separados;
- [x] sidebar e breadcrumbs padronizados;
- [x] smoke tests criados;
- [x] `manage.py check comunicacao` verde;
- [x] ambiente de teste do projeto liberado para comunicação.

---

# 10. Documentos Relacionados

- [03 - Arquitetura dos Apps](../backend/03-Arquitetura-dos-Apps.md)
- [05 - Services](../backend/05-Services.md)
- [06 - Selectors](../backend/06-Selectors.md)
- [08 - Views](../backend/08-Views.md)
- [01 - GereIgreja Design System](../frameworks/01-GDS-GereIgreja-Design-System.md)
- [04 - GereIgreja Quality Framework](../frameworks/04-GQF-GereIgreja-Quality-Framework.md)
- [05 - GereIgreja Documentation Framework](../frameworks/05-GDF-GereIgreja-Documentation-Framework.md)
- [Runbook WAHA - Comunicação](../operacoes/COMUNICACAO_WAHA_RUNBOOK.md)
- [Checklist de Release WAHA - Comunicação](../qualidade/COMUNICACAO_CHECKLIST_RELEASE_WAHA.md)

---

# 11. Princípios Finais

O app Comunicação só deve crescer se mantiver:

- baixo acoplamento;
- alto reaproveitamento;
- regras de negócio fora das Views;
- documentação atualizada;
- cobertura de testes mínima.
