Pasta:
docs/operacoes/

Arquivo:
COMUNICACAO_WAHA_RUNBOOK.md

Documento:
GOC-COM-WAHA-01

Seção:
Operações

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# Runbook Operacional - Comunicação + WAHA

> Objetivo: padronizar execução, validação e resposta a incidentes da integração WhatsApp no módulo Comunicação.

---

## 1. Escopo

Este runbook cobre:

- health-check de WAHA no módulo Comunicação;
- envio manual em massa via WhatsApp;
- automação diária de aniversariantes;
- troubleshooting de conexão, timeout e erro HTTP;
- critérios de rollback operacional.

Não cobre:

- alterações de código da integração;
- migrações de banco fora do app Comunicação;
- operação de provedores externos de WhatsApp além de WAHA.

---

## 2. Ambientes e Configuração

### 2.1 Dev

- usar WAHA local ou sandbox dedicado;
- nunca usar números reais de usuários finais;
- validar `WAHA_BASE_URL` e `WAHA_API_KEY` antes de teste manual.

### 2.2 Homologação

- usar instância isolada de WAHA;
- usar lista branca de números de QA;
- executar validação de ponta a ponta antes de release.

### 2.3 Produção

- usar URL de WAHA de produção com segredo gerenciado;
- monitoramento contínuo de latência e taxa de falha;
- ativar automações somente após smoke test pós-deploy.

---

## 3. Pré-check Operacional

Executar nesta ordem:

1. `python manage.py check comunicacao`
2. `python manage.py test comunicacao.tests --settings=core.settings_test -v 1`
3. Validar rota do módulo: `/comunicacao/home/`
4. Em `/comunicacao/whatsapp/massa/`, clicar em `Testar WAHA`
5. Confirmar resposta com status HTTP e latência.

---

## 4. Teste Funcional Recomendado

### 4.1 Envio Manual

1. Acessar `/comunicacao/whatsapp/massa/`.
2. Definir filtros com público pequeno.
3. Enviar mensagem de teste para números internos de QA.
4. Validar em `/comunicacao/whatsapp/logs/`:
   - tipo `manual`;
   - status `sucesso` ou `erro`;
   - mensagem de erro legível.

### 4.2 Automação de Aniversariantes

1. Acessar `/comunicacao/automacoes/aniversariantes/`.
2. Configurar templates e horários de WhatsApp/E-mail.
3. Executar comando manual:
   - `python manage.py rodar_automacoes_comunicacao_diarias`
4. Validar no painel da Home e nos logs do módulo.

---

## 5. Troubleshooting

### 5.1 Erro: nenhum servidor encontrado em localhost:3000

Causa provável:

- `WAHA_BASE_URL` não configurada para URL real;
- WAHA local não iniciado.

Ações:

1. revisar variável `WAHA_BASE_URL`;
2. validar acesso HTTP ao endpoint `/api/sessions/default`;
3. reiniciar aplicação após ajuste de ambiente.

### 5.2 Erro: timeout de conexão WAHA

Causa provável:

- instância WAHA fria/lenta;
- falha de rede;
- endpoint degradado.

Ações:

1. repetir health-check;
2. verificar disponibilidade no host WAHA;
3. acionar retentativa controlada de envio;
4. se persistir, desativar automação temporariamente.

### 5.3 Erro HTTP 4xx/5xx do WAHA

Ações:

1. registrar status + corpo da resposta;
2. validar sessão (`default`/sessão ativa);
3. revisar API key;
4. abrir incidente com evidências de horário e payload resumido.

---

## 6. Monitoramento e Alertas

Métricas mínimas:

- latência de health-check WAHA;
- taxa de sucesso de envio;
- taxa de falha por igreja;
- volume de erros por tipo (`manual`, `aniversario`, `evento`).

Alertas recomendados:

- conexão recusada > 3 vezes em 10 minutos;
- timeout > 20% em 15 minutos;
- erro 5xx contínuo por 5 minutos.

---

## 7. Rollback Operacional

Sem rollback de código, ações imediatas:

1. desativar automações de aniversariantes na tela de configuração;
2. suspender campanhas de envio manual;
3. manter logs para investigação;
4. restabelecer somente após novo smoke test WAHA.

Com rollback de release:

1. aplicar rollback de deploy;
2. revalidar health-check;
3. rodar checklist de release novamente.

---

## 8. Comandos de Referência

- `python manage.py check comunicacao`
- `python manage.py test comunicacao.tests --settings=core.settings_test -v 1`
- `python manage.py enviar_whatsapp_automatico --tipo aniversariantes`
- `python manage.py enviar_email_automatico --tipo aniversariantes`
- `python manage.py rodar_automacoes_comunicacao_diarias`

---

## 9. Evidências mínimas para Go/No-Go

- saída do `check`;
- saída dos testes;
- print do health-check WAHA;
- print dos logs de envio;
- confirmação de templates de automação ativos/inativos conforme plano.
