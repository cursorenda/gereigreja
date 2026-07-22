Pasta:
docs/qualidade/

Arquivo:
COMUNICACAO_CHECKLIST_RELEASE_WAHA.md

Documento:
GQF-COM-WAHA-01

Seção:
Qualidade

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# Checklist de Release - Comunicação (WAHA)

> Uso: checklist obrigatório para homologar e liberar mudanças do módulo Comunicação com impacto em WhatsApp/automações.

---

## 1. Arquitetura e Código

- [ ] Regras de negócio em Service (sem lógica de domínio em View)
- [ ] Consultas reutilizáveis em Selector
- [ ] Rotas protegidas com autenticação/assinatura/permissão
- [ ] Tratamento de erro com mensagem operacional legível
- [ ] Sem hardcode de credenciais/chaves em código

---

## 2. Banco e Migrações

- [ ] Migrações geradas e revisadas
- [ ] Migrações aplicadas em homologação
- [ ] Smoke do módulo após migrate
- [ ] Plano de rollback de migration documentado

---

## 3. Testes (GQF)

- [ ] `python manage.py check comunicacao`
- [ ] `python manage.py test comunicacao.tests --settings=core.settings_test -v 1`
- [ ] Testes de Services cobrindo automação de aniversariantes
- [ ] Testes de rotas/acesso atualizados quando houver rota nova
- [ ] Evidência anexada ao card de release

---

## 4. Integração WAHA

- [ ] `WAHA_BASE_URL` do ambiente validada
- [ ] `WAHA_API_KEY` validada (quando aplicável)
- [ ] Health-check via tela `Testar WAHA` executado
- [ ] Teste de envio manual para números internos de QA
- [ ] Logs com status e latência revisados

---

## 5. Automações de Aniversariantes

- [ ] Configuração de templates revisada
- [ ] Horários de execução revisados
- [ ] Comando diário validado em homologação
- [ ] Proteção contra reenvio no mesmo dia validada
- [ ] Canal WhatsApp/E-mail ativado conforme aprovação de produto

---

## 6. UI/UX e GDS

- [ ] Sidebar/breadcrumb/CTA conforme padrão
- [ ] Responsividade validada (desktop e mobile)
- [ ] Mensagens de sucesso/erro claras para operação
- [ ] Sem regressão visual nas telas: Home, WhatsApp, E-mail

---

## 7. Documentação (GDF)

- [ ] Documento de módulo atualizado em `docs/apps/04-Comunicacao.md`
- [ ] Runbook operacional WAHA atualizado
- [ ] Checklist de release atualizado (este documento)
- [ ] Referências cruzadas entre docs revisadas

---

## 8. Go/No-Go

Go somente se:

- todos os itens críticos (seções 1, 3, 4) estiverem concluídos;
- sem erros bloqueantes em health-check e envio de teste;
- validação final aprovada por Engenharia e Operações.

No-Go se:

- falha de conexão WAHA persistente sem mitigação;
- ausência de evidência de testes;
- regressão funcional nas jornadas principais de Comunicação.
