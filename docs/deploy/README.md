# Deploy — Publicação e Mudanças de Ambiente

Deploy  
↓  
Como uma versão do GereIgreja é preparada, publicada, validada e, quando necessário, revertida.

Esta pasta reúne documentação de publicação e transição entre ambientes.

Ela não substitui:

- `docs/frameworks/06-GOC-GereIgreja-Operations-Center.md`;
- `docs/operacoes/`;
- `docs/qualidade/`;
- `docs/release-notes/`;
- `docs/seguranca/`.

## Finalidade da pasta

- registrar procedimentos de deploy;
- documentar passos de publicação;
- manter checklists específicos de release quando ligados diretamente ao processo de deploy;
- registrar rollback;
- documentar configuração de ambiente necessária para publicar uma versão;
- preservar guias históricos de deploy quando forem relevantes;
- distinguir claramente procedimento recorrente de registro histórico.

## Fronteira com outras famílias

### `docs/operacoes/`

Contém runbooks de operação contínua.

Exemplos:

- restaurar integração;
- rotacionar credencial;
- validar saúde;
- reexecutar rotina;
- responder a falha operacional.

### `docs/qualidade/`

Contém gates, critérios de homologação e validação.

Exemplos:

- critérios de aceite;
- checklist de homologação;
- regressão;
- aprovação/reprovação de release.

### `docs/release-notes/`

Registra o que mudou em uma versão.

### `docs/deploy/`

Registra como publicar essa versão ou configurar o ambiente necessário para fazê-lo.

## Índice atual

| Documento | Natureza | Classificação recomendada |
|---|---|---|
| [Deploy-Release-v1.15.0.md](Deploy-Release-v1.15.0.md) | Guia de deploy de release | Correto em `deploy/` |
| [Deploy-Release-v1.14.4.md](Deploy-Release-v1.14.4.md) | Guia de deploy de release | Correto em `deploy/` |
| [Deploy-Release-v1.14.3.md](Deploy-Release-v1.14.3.md) | Guia de deploy de release | Correto em `deploy/` |
| [Deploy-Release-v1.14.2.md](Deploy-Release-v1.14.2.md) | Guia de deploy de release | Correto em `deploy/` |
| [Deploy-Release-V1.10.1.md](Deploy-Release-V1.10.1.md) | Guia histórico de deploy | Correto em `deploy/` |
| [RENDER_CRON_WHATSAPP.md](RENDER_CRON_WHATSAPP.md) | Configuração operacional de cron no Render | Revisar destino |
| [ANALISE_SISTEMA_DEPLOY.md](../relatorios/ANALISE_SISTEMA_DEPLOY.md) | Análise histórica do sistema de deploy | Reclassificado para `relatorios/` |
| [LGPD_IMPLEMENTACAO.md](LGPD_IMPLEMENTACAO.md) | Registro de implementação LGPD | Não pertence a `deploy/` |

## Guias de Deploy por Release

Arquivos como:

```text
Deploy-Release-v1.14.2.md
Deploy-Release-v1.14.3.md
Deploy-Release-v1.14.4.md
```

são adequados nesta pasta quando documentam:

- pré-deploy;
- escopo da publicação;
- comandos;
- migrações;
- validação pós-deploy;
- rollback;
- observações específicas daquela versão.

Esses documentos são **históricos por natureza**.

Eles não devem ser tratados como procedimento universal atual de deploy.

Quando houver um procedimento transversal e estável, ele deverá existir em documento próprio e os guias por release deverão referenciá-lo.

## RENDER_CRON_WHATSAPP.md

Este documento explica como configurar um Render Cron Job para executar:

```bash
python manage.py rodar_automacoes_whatsapp_diarias
```

Ele descreve uma configuração persistente de produção, incluindo agendamento, variáveis de ambiente, execução manual e observabilidade.

Por isso, sua natureza é mais próxima de:

- `docs/operacoes/`; ou
- `docs/automacao/`;

do que de um deploy de versão específico.

Não mover automaticamente.

Primeiro revisar referências e a futura governança de `docs/automacao/`.

## ANALISE_SISTEMA_DEPLOY.md

Localização canônica atual:

```text
docs/relatorios/ANALISE_SISTEMA_DEPLOY.md
```

Este arquivo é uma análise datada do sistema interno de deploy, originalmente referente à versão 1.5.0.

Ele registra:

- situação observada naquele momento;
- melhorias já implementadas;
- lacunas;
- propostas de evolução;
- exemplos de código;
- recomendações.

Portanto, deve ser tratado como **análise histórica**, não como procedimento atual de deploy.

A reclassificação para `docs/relatorios/` já foi executada e está registrada em `docs/relatorios/README.md`.

O documento permanece sem promoção a fonte normativa.

## LGPD_IMPLEMENTACAO.md

Este documento não é documentação de deploy.

Seu conteúdo registra evolução funcional e técnica da implementação LGPD, incluindo:

- consentimento;
- visualização de dados;
- exportação;
- histórico;
- exclusão/anonimização ainda pendente;
- decisões técnicas relacionadas.

Seu conteúdo já foi utilizado como evidência histórica na consolidação de:

```text
docs/seguranca/14-Conformidade-e-LGPD.md
```

Portanto, `LGPD_IMPLEMENTACAO.md` deve ser considerado **arquivo mal classificado em `deploy/`**.

Não duplicar seu conteúdo.

Antes de mover, revisar links e referências.

Destino provável:

```text
docs/sistema/
```

ou uma área histórica/auditoria, dependendo da política final de reclassificação.

## Checklist de Comunicação / WAHA

A auditoria de `docs/operacoes/` encontrou um checklist de deploy da Comunicação/WAHA.

Por sua natureza — pré-deploy, ambiente, staging, pós-deploy e rollback — ele pertence conceitualmente mais a esta família.

Entretanto, a mudança de pasta só deve ocorrer depois da revisão de referências.

O objetivo é terminar com **uma única fonte canônica**, não criar outra cópia.

## Regra para criar um novo documento de Deploy

Antes de criar um novo arquivo:

1. confirme que o documento trata de publicação ou transição de ambiente;
2. verifique se já existe procedimento transversal;
3. diferencie procedimento permanente de guia específico de release;
4. inclua pré-condições;
5. registre migrações e mudanças de infraestrutura quando aplicável;
6. informe validações pós-deploy;
7. documente rollback;
8. referencie gates de qualidade em vez de duplicá-los;
9. não coloque segredos ou credenciais;
10. atualize este README quando o arquivo fizer parte do índice ativo.

## Estado atual

A pasta possui conteúdo legítimo de deploy, mas também contém documentos historicamente acumulados que pertencem a outras classificações.

Situação:

```text
Guias de release        → manter
Cron WhatsApp           → revisar
Análise sistema deploy  → histórico / revisar
LGPD implementação      → reclassificar
```

A prioridade não é criar mais documentos.

A prioridade é reduzir mistura de responsabilidades.

## Princípio de manutenção

Todo documento de deploy deve responder claramente:

```text
O que será publicado?
Quais pré-condições existem?
Quais passos executar?
Quais mudanças de ambiente ocorrerão?
Como validar após publicar?
Como reverter com segurança?
```

Se o documento não trata principalmente dessas perguntas, provavelmente pertence a outra família.
