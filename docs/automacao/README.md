# Automação — Rotinas Automatizadas do GereIgreja

Automação  
↓  
O que o sistema executa automaticamente, em qual contexto e sob quais condições.

Esta pasta reúne documentação funcional e operacional de rotinas automatizadas do GereIgreja.

Ela não substitui:

- `docs/apps/` — regras funcionais dos módulos;
- `docs/operacoes/` — runbooks e procedimentos operacionais;
- `docs/deploy/` — publicação e configuração de ambiente;
- `docs/qualidade/` — critérios de validação;
- `docs/frameworks/06-GOC-GereIgreja-Operations-Center.md` — governança operacional.

## Finalidade da pasta

- documentar automações recorrentes;
- registrar gatilhos, frequência e condições de execução;
- indicar comandos responsáveis pela execução;
- documentar dependências de configuração;
- registrar observabilidade e logs;
- explicar fallback local quando existir;
- separar automação de rotina manual e de funcionalidade comum de interface.

## O que caracteriza uma automação

Um documento pertence a esta pasta quando descreve algo que ocorre sem intervenção manual contínua.

Exemplos:

```text
Cron Job
↓
executa comando
↓
processa rotina
↓
gera resultado automaticamente
```

ou:

```text
Evento / Scheduler
↓
dispara rotina
↓
executa ação programada
```

Não basta o recurso usar scripts ou processamento em massa para ser considerado automação.

## Índice atual

| Documento | Natureza | Classificação |
|---|---|---|
| [WHATSAPP_AUTOMACOES_DIARIAS.md](WHATSAPP_AUTOMACOES_DIARIAS.md) | Automação diária de WhatsApp | Correto em `automacao/` |
| [WhatsApp-Bulk-Celular-Edit.md](WhatsApp-Bulk-Celular-Edit.md) | Funcionalidade de edição em massa | Reclassificar |

## WHATSAPP_AUTOMACOES_DIARIAS.md

Este documento está corretamente classificado.

Ele registra:

- automação diária do app Comunicação;
- aniversariantes do dia;
- lembretes de eventos;
- comando principal:

```bash
python manage.py rodar_automacoes_whatsapp_diarias
```

- execução em produção via Render Cron Job;
- scripts auxiliares Windows/Linux;
- observabilidade;
- dependência de configuração por congregação.

Essa é uma automação real e recorrente.

## WhatsApp-Bulk-Celular-Edit.md

Este arquivo não documenta uma automação.

Ele descreve uma funcionalidade interativa de edição em massa:

- acesso por tela;
- filtros;
- tabela;
- alteração manual de celulares;
- salvamento via formulário;
- validações;
- UX;
- implementação técnica.

O usuário inicia a operação manualmente.

Portanto:

```text
edição em massa
≠
automação
```

Destino conceitual mais adequado:

- `docs/apps/04-Comunicacao.md`, como parte da visão funcional; ou
- documentação técnica especializada de Comunicação, caso seja necessário manter um arquivo próprio.

Não mover automaticamente antes de revisar referências.

## Relação com RENDER_CRON_WHATSAPP.md

A auditoria de `docs/deploy/` identificou:

```text
docs/deploy/RENDER_CRON_WHATSAPP.md
```

Esse documento explica como configurar em produção a execução da automação diária.

Ele complementa `WHATSAPP_AUTOMACOES_DIARIAS.md`.

A divisão conceitual correta é:

```text
WHATSAPP_AUTOMACOES_DIARIAS.md
↓
o que a automação faz

RENDER_CRON_WHATSAPP.md
↓
como a execução é agendada no ambiente de produção
```

Por isso, `RENDER_CRON_WHATSAPP.md` pode ser classificado futuramente como:

- configuração de automação; ou
- operação de infraestrutura.

Não deve existir uma segunda cópia do mesmo conteúdo nesta pasta.

A decisão de mover deve ser tomada apenas após revisão de referências.

## Relação com PLANO_AUTOMACOES_COMUNICACAO.md

A auditoria de `docs/operacoes/` identificou:

```text
PLANO_AUTOMACOES_COMUNICACAO.md
```

Esse arquivo possui natureza de planejamento/evolução.

Planejamento de futuras automações não deve ser confundido com documentação de automação implementada.

Se permanecer relevante, deve ser classificado como:

- roadmap/evolução de Comunicação; ou
- plano histórico.

Somente capacidades efetivamente implementadas devem ser promovidas para documentação operacional desta pasta.

## Fronteira com Comunicação

A autoridade funcional do módulo permanece:

```text
docs/apps/04-Comunicacao.md
```

Esta pasta deve registrar somente a parte automatizada.

Exemplo:

```text
Comunicação
↓
define jornada e regra funcional

Automação
↓
define execução automática dessa jornada
```

## Fronteira com Operações

`docs/operacoes/` responde:

```text
Como operar, diagnosticar ou recuperar?
```

`docs/automacao/` responde:

```text
O que roda automaticamente?
Quando?
Por qual mecanismo?
Com quais condições?
```

Um runbook para recuperar uma automação quebrada pertence a `operacoes/`.

A descrição da própria rotina automática pertence aqui.

## Fronteira com Deploy

`docs/deploy/` responde:

```text
Como publicar ou configurar a versão/ambiente?
```

A automação não deve duplicar instruções completas de deploy.

Pode apenas referenciá-las.

## Regra para criar um novo documento

Antes de criar um arquivo em `docs/automacao/`:

1. confirme que existe execução automática real;
2. identifique o gatilho;
3. identifique a frequência ou condição;
4. informe o comando, job ou mecanismo responsável;
5. documente escopo por igreja/tenant quando aplicável;
6. registre flags/configurações necessárias;
7. indique logs e observabilidade;
8. documente idempotência quando relevante;
9. descreva comportamento em caso de falha;
10. diferencie claramente implementação atual de planejamento.

## Multi-Tenancy

Automações do GereIgreja devem respeitar o mesmo isolamento dos fluxos manuais.

Uma automação não pode utilizar a ausência de interação humana como justificativa para ignorar tenant.

Quando a rotina operar sobre múltiplas igrejas ou congregações, deve:

- iterar explicitamente pelos contextos permitidos;
- aplicar configurações próprias de cada tenant;
- impedir cruzamento de dados;
- registrar contexto suficiente em logs e auditoria.

## Observabilidade

Toda automação relevante deve possuir uma forma verificável de execução.

Possíveis evidências:

- logs do scheduler;
- logs do Django;
- registros em banco;
- contador de sucesso/falha;
- timestamp de última execução;
- alertas, quando aplicável.

No caso atual do WhatsApp, a documentação registra como fontes principais em produção:

- logs do Render Cron Job;
- registros em `WhatsAppMensagemLog`.

## Falhas e reexecução

Automação recorrente deve ser projetada para evitar duplicações quando executada novamente.

Quando possível, a documentação deve registrar:

- se a rotina é idempotente;
- como detectar execução parcial;
- como reexecutar;
- quais registros podem ser duplicados;
- como recuperar falhas.

A ausência dessas informações deve ser tratada como lacuna operacional, não preenchida por suposição.

## Estado atual da pasta

A pasta possui:

```text
1 automação real e documentada
1 arquivo mal classificado
```

O objetivo agora não é aumentar artificialmente a quantidade de documentos.

A prioridade é:

```text
manter WHATSAPP_AUTOMACOES_DIARIAS.md
reclassificar WhatsApp-Bulk-Celular-Edit.md
avaliar RENDER_CRON_WHATSAPP.md
avaliar PLANO_AUTOMACOES_COMUNICACAO.md
```

## Princípio de manutenção

Automação deve ser explícita, observável e segura.

Todo documento desta pasta deve permitir responder:

```text
O que roda automaticamente?
O que dispara a execução?
Quando roda?
Para qual tenant?
Que configuração é necessária?
Como verificar o resultado?
O que acontece se falhar?
```

Se o documento não responde principalmente a essas perguntas, provavelmente pertence a outra família.
