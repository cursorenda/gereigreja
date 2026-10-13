Pasta:
docs/apps/

Arquivo:
07-Eventos.md

Documento:
APP-07

Família:
Apps — Documentação Funcional

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Setembro de 2026

# 07 — Eventos

> O módulo Eventos é o domínio canônico para criação, edição, acompanhamento e presença em eventos da igreja, integrado à Agenda e ao Financeiro, com participação dinâmica e escopo por igreja.

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Conceitos Centrais
5. Ciclo de Vida do Evento
6. Agenda e Eventos
7. Programações Padrão e Recorrência
8. Participantes Esperados
9. Sistema Híbrido de Participantes
10. Presença
11. Tipos de Pessoa e Status
12. Feriados e Agenda
13. Prestação de Contas
14. Integração com Financeiro
15. Integração com Configurações
16. Integração com EBD
17. Multi-Tenancy
18. Permissões e Segurança
19. Auditoria e Histórico
20. UX e Operação
21. Testes e Qualidade
22. Compatibilidade e Legado
23. Pontos a Validar
24. Documentos Relacionados
25. Princípios Finais
26. Status

---

# 1. Objetivo

Este documento consolida a visão funcional canônica do módulo Eventos do GereIgreja.

Seu objetivo é registrar:

- o que o domínio Eventos representa;
- como eventos são criados, exibidos e operados;
- como Agenda e Eventos se relacionam;
- como participantes esperados são calculados;
- como ajustes manuais e presença funcionam;
- como o módulo se integra com Financeiro, Configurações e EBD;
- como o isolamento por igreja deve ser preservado.

Este documento não substitui documentação técnica de Models, Views, Forms, Services, Frontend, Segurança ou releases.

---

# 2. Escopo

O domínio Eventos cobre, conforme a documentação auditada:

- listagem de eventos;
- criação;
- edição;
- visualização de detalhe;
- exclusão;
- marcação de presença;
- participantes esperados;
- critérios por tipo de pessoa e status;
- ajustes manuais de participantes;
- programação recorrente;
- integração com Agenda;
- importação de feriados;
- prestação de contas;
- integração financeira;
- proteção contra conflitos com EBD.

---

# 3. Papel deste Documento

Este é o documento funcional canônico de Eventos em `docs/apps/`.

A relação esperada é:

```text
docs/apps/07-Eventos.md
        ↓
Visão funcional do domínio
        ↓
eventos/
agenda/
docs/apps/01-Membros.md
docs/apps/03-Financeiro.md
docs/apps/06-EBD.md
docs/seguranca/
docs/release-notes/
        ↓
Implementação, integração e histórico
```

Registros de release servem como evidência de evolução, mas não devem substituir este documento como ponto funcional de referência.

---

# 4. Conceitos Centrais

O domínio trabalha com os seguintes conceitos:

```text
Evento
+
Igreja
+
Data/Hora
+
Local
+
Tipo
+
Participantes esperados
+
Presença
+
Integrações
```

Eventos devem existir dentro do contexto correto da igreja e podem ser exibidos na Agenda consolidada.

---

# 5. Ciclo de Vida do Evento

A documentação mais recente confirma um ciclo completo de operação com telas para:

- listar;
- criar;
- editar;
- detalhar;
- excluir;
- marcar presença.

Esse ciclo deve ser tratado como responsabilidade principal do módulo Eventos.

A Agenda não deve manter um CRUD concorrente quando a ação pertencer ao domínio Eventos.

---

# 6. Agenda e Eventos

A versão v1.13.18 consolidou explicitamente o fluxo entre Agenda e Eventos.

Regras documentadas:

- rotas legadas de CRUD da Agenda foram redirecionadas para Eventos;
- Agenda mensal passou a utilizar a mesma base de eventos;
- importação de feriados foi unificada para o modelo Evento.

A divisão funcional é:

```text
Eventos
↓
cria e gerencia eventos

Agenda
↓
organiza e apresenta eventos no calendário
```

Essa separação reduz duplicidade de fluxo e divergência entre módulos.

---

# 7. Programações Padrão e Recorrência

A documentação da v1.13.18 registra evolução de programações padrão da igreja.

Capacidades documentadas incluem:

- hora de término;
- cálculo de duração;
- recorrência;
- validações condicionais;
- resumo de configuração;
- integração com o modelo Evento.

Programações recorrentes devem gerar ou relacionar eventos sem criar fluxos paralelos incompatíveis.

---

# 8. Participantes Esperados

Eventos podem utilizar critérios para determinar participantes esperados.

Os critérios documentados utilizam principalmente:

- tipos de pessoa;
- status.

A lista deve ser dinâmica, permitindo que alterações futuras no cadastro de pessoas sejam refletidas sem manter uma cópia estática obsoleta.

---

# 9. Sistema Híbrido de Participantes

A versão 1.6.0 documenta um modelo híbrido de participantes.

A lógica funcional é:

```text
Participantes por critérios
+
Adicionados manualmente
-
Removidos manualmente
=
Lista final esperada
```

Tipos de inclusão documentados:

- `AUTOMATICA`;
- `MANUAL_ADICIONADO`;
- `MANUAL_REMOVIDO`.

Esse modelo permite:

- atualização automática conforme cadastro atual;
- inclusão de convidados;
- remoção de exceções;
- preservação de ajustes manuais.

O cálculo deve sempre respeitar a igreja do evento.

---

# 10. Presença

O módulo possui fluxo específico de marcação de presença.

A documentação mais recente registra melhorias operacionais:

- busca em tempo real;
- ordenação A-Z/Z-A;
- ações em massa para marcar/desmarcar;
- filtros e ações compactados.

Presença deve estar relacionada ao evento correto e aos participantes dentro do escopo permitido.

A interface de presença não deve permitir manipular participantes de outra igreja.

---

# 11. Tipos de Pessoa e Status

A seleção automática de participantes depende das regras de Membros.

O documento `01-Membros.md` é a referência funcional para:

- Membro;
- Obreiro;
- Novo Convertido;
- Congregado;
- Visitante;
- status válidos.

A documentação histórica registra que Visitante não é utilizado como critério padrão de “participantes esperados” em determinados fluxos, pois sua presença pode ser imprevisível.

Visitantes podem ser adicionados manualmente quando necessário.

---

# 12. Feriados e Agenda

A importação de feriados evoluiu para utilizar o modelo Evento como base comum.

A documentação registra:

- importação via interface;
- importação por comando;
- prevenção contra duplicação;
- integração com Agenda.

Feriados importados devem ser tratados como eventos de calendário, sem criar estrutura paralela desnecessária.

---

# 13. Prestação de Contas

Foi identificada interface específica de `prestacao_contas_eventos.html`, o que demonstra integração operacional entre Eventos e Financeiro.

Entretanto, a documentação auditada não oferece material suficiente para afirmar todas as regras atuais dessa prestação.

Portanto, este documento reconhece a capacidade como existente, mas não inventa estados, aprovações ou regras contábeis não suportadas pelas fontes auditadas.

---

# 14. Integração com Financeiro

O Financeiro possui fundo `EVENTOS` documentado como escopo específico.

A documentação financeira estabelece vínculo entre lançamentos de evento e fundo EVENTOS.

Em termos funcionais:

```text
Evento
↓
movimentações financeiras relacionadas
↓
escopo financeiro EVENTOS
```

A autorização financeira continua pertencendo ao módulo Financeiro.

Participar da organização de um evento não concede automaticamente permissão financeira.

---

# 15. Integração com Configurações

Programações padrão da igreja são configuradas fora do módulo Eventos e materializadas/integradas com eventos.

Configurações documentadas incluem regras de:

- recorrência;
- frequência;
- horário;
- hora de término.

Eventos devem consumir essas definições de maneira coerente, sem duplicar regras de configuração.

---

# 16. Integração com EBD

A versão v1.13.18 registra proteção contra conflitos entre Programações padrão e Escola Bíblica Dominical.

O sistema deve evitar criar programações recorrentes que conflitem silenciosamente com o calendário configurado da EBD quando as regras de negócio determinarem essa proteção.

A EBD continua sendo autoridade sobre seu próprio período, dia e horário.

---

# 17. Multi-Tenancy

Todo evento deve permanecer no escopo correto da igreja.

Devem respeitar tenant:

- criação;
- edição;
- participantes;
- presença;
- importação de feriados;
- agenda;
- movimentações financeiras;
- programações recorrentes.

A documentação do sistema híbrido de participantes registra explicitamente filtro por igreja como requisito de segurança.

---

# 18. Permissões e Segurança

A autorização deve ser validada no backend.

A existência de botão ou rota não constitui autorização.

Ações sensíveis incluem:

- criar evento;
- editar;
- excluir;
- marcar presença;
- importar feriados;
- acessar prestação de contas;
- manipular participantes.

Cada ação deve respeitar:

- usuário autenticado;
- acesso à página;
- igreja ativa;
- objeto;
- permissões funcionais aplicáveis.

---

# 19. Auditoria e Histórico

A documentação auditada não fornece especificação completa de auditoria do módulo Eventos.

Ainda assim, mudanças críticas devem ser rastreáveis conforme os padrões gerais do GSF, especialmente:

- exclusão;
- alterações relevantes;
- ajustes manuais de participantes;
- presença;
- integrações financeiras.

O histórico do sistema híbrido de participantes é relevante porque diferencia inclusão automática de ajustes manuais.

---

# 20. UX e Operação

A v1.13.18 consolidou padrão visual premium em:

- lista;
- criação;
- edição;
- detalhe;
- exclusão;
- presença.

Também registrou:

- breadcrumbs;
- headers padronizados;
- cards;
- centralização de estilos;
- melhorias de produtividade na presença.

Esses pontos são de implementação visual, mas refletem um objetivo funcional importante: manter fluxo coerente e previsível durante todo o ciclo de vida do evento.

---

# 21. Testes e Qualidade

A documentação de releases registra validação com `manage.py check`.

O domínio também deve possuir testes para:

- isolamento por igreja;
- participantes por critérios;
- inclusão manual;
- remoção manual;
- presença;
- programação recorrente;
- conflitos de calendário;
- integração financeira;
- importação de feriados;
- permissões.

Testes técnicos específicos devem permanecer na documentação de Qualidade e Backend.

---

# 22. Compatibilidade e Legado

O domínio Eventos passou por consolidação com Agenda.

Portanto, fluxos antigos de CRUD existentes em Agenda devem ser considerados legados quando redirecionados para Eventos.

A preservação de compatibilidade deve evitar:

- URLs quebradas;
- duplicação de eventos;
- divergência entre calendários;
- importação duplicada de feriados.

---

# 23. Pontos a Validar

Durante a auditoria, os seguintes pontos não possuem documentação suficiente para serem promovidos a regra normativa detalhada:

1. regras de transição entre os estados e status formais já definidos no modelo;
2. regras completas de cancelamento;
3. regras atuais de prestação de contas;
4. auditoria específica do módulo;
5. política exata de exclusão quando existem presenças ou lançamentos financeiros;
6. permissões finas por perfil;
7. comportamento atual de convidados externos;
8. detalhes atuais de recorrência após v1.13.18.

Esses itens devem ser verificados no código atual antes de ampliar este documento.

---

# 24. Documentos Relacionados

## Canônicos

- `docs/apps/README.md`
- `docs/apps/01-Membros.md`
- `docs/apps/03-Financeiro.md`
- `docs/apps/06-EBD.md`

## Histórico e evolução

- [`RELEASE_NOTES_v1.6.0.md`](../release-notes/RELEASE_NOTES_v1.6.0.md)
- [`RELEASE_v1.13.18_SUMMARY.md`](../release-notes/RELEASE_v1.13.18_SUMMARY.md)

## Segurança e arquitetura

- `docs/arquitetura/08-Arquitetura-Multi-Tenant.md`
- `docs/seguranca/08-Seguranca-de-Dados-e-Privacidade.md`
- `docs/seguranca/14-Conformidade-e-LGPD.md`

---

# 25. Princípios Finais

O domínio Eventos deve preservar:

```text
igreja correta
+
evento correto
+
participantes corretos
+
presença correta
+
integrações coerentes
```

Agenda é a visão temporal.

Eventos é a autoridade funcional sobre o ciclo de vida do evento.

Financeiro é a autoridade sobre movimentações financeiras.

Membros é a autoridade sobre classificação das pessoas.

EBD é a autoridade sobre seu calendário educacional.

---

# 26. Status

**Pasta:** `docs/apps/`

**Arquivo:** `07-Eventos.md`

**Documento:** `APP-07`

**Versão:** `1.0`

**Status:** **OFICIAL**

A lacuna documental foi confirmada em `docs/apps/`.

Este documento consolida a visão funcional de Eventos sem transformar registros históricos ou detalhes não verificados em regras atuais.
