# Infraestrutura — Ambientes, Plataforma e Continuidade Operacional

Infraestrutura  
↓  
Como o GereIgreja é executado, conectado, protegido e sustentado nos diferentes ambientes.

Esta pasta reúne a documentação canônica da infraestrutura técnica do GereIgreja.

Ela cobre arquitetura de infraestrutura, ambientes, persistência, entrega técnica, backup, disponibilidade, automação, capacidade, custos e prontidão operacional.

Não é uma pasta genérica de operação ou deploy. Seu foco é a **plataforma técnica que sustenta a aplicação**.

## Finalidade da pasta

- documentar a arquitetura de infraestrutura;
- definir ambientes e sua segregação;
- registrar configuração de serviços essenciais;
- documentar persistência e migrations sob a ótica de infraestrutura;
- definir backup, restore e disaster recovery;
- registrar CI/CD quando ligado à infraestrutura de entrega;
- documentar escalabilidade, disponibilidade e capacidade;
- registrar automação e infraestrutura como código;
- documentar FinOps e governança de recursos;
- manter a matriz oficial de ambientes e comandos seguros;
- preservar correções históricas de infraestrutura quando tiverem valor operacional.

## Fronteira com outras famílias

### `docs/deploy/`

Responde principalmente:

```text
Como publicar uma versão?
```

### `docs/infraestrutura/`

Responde principalmente:

```text
Em qual infraestrutura a aplicação roda?
Como os ambientes são organizados?
Como banco, serviços, automação, backup e disponibilidade são sustentados?
```

### `docs/operacoes/`

Contém runbooks operacionais recorrentes.

A infraestrutura pode conter um documento de operação **quando ele for especificamente sobre a infraestrutura** e fizer parte do baseline técnico dessa família.

Runbooks de um módulo ou integração de negócio pertencem preferencialmente a `operacoes/`.

### `docs/qualidade/`

Define gates e critérios de validação.

Checklists de prontidão de produção podem permanecer aqui quando verificam especificamente capacidade e estado da infraestrutura, mas não devem substituir gates gerais do GQF.

### `docs/seguranca/`

Define política e controles de segurança.

Infraestrutura documenta como esses controles se materializam em ambientes, serviços, rede, banco, backups e configurações.

## Estrutura documental

A família possui documentação numerada e madura, incluindo documentos como:

```text
01-Arquitetura-da-Infraestrutura.md
02-Ambientes-e-Configuracao.md
05-Banco-de-Dados-e-Persistencia.md
09-CI-CD-Deploy-e-Rollback.md
11-Backup-Restore-e-Disaster-Recovery.md
12-Infraestrutura-como-Codigo-e-Automacao.md
13-Escalabilidade-Alta-Disponibilidade-e-Capacidade.md
14-Custos-FinOps-e-Governanca-de-Recursos.md
15-Operacao-Manutencao-e-Runbooks-de-Infraestrutura.md
16-Governanca-Padroes-e-Evolucao-da-Infraestrutura.md
17-Checklist-de-Producao-e-Prontidao-Operacional.md
18-Indice-e-Mapa-da-Infraestrutura.md
19-Matriz-de-Ambientes-e-Comandos-Seguros.md
20-Correcao-Historica-Migration-Secretaria-0008.md
21-Correcao-Historica-Migration-Secretaria-0014.md
```

O inventário detalhado deve ser consultado em:

```text
18-Indice-e-Mapa-da-Infraestrutura.md
```

O README não precisa duplicar integralmente esse índice.

## Fonte de verdade da família

A leitura recomendada é:

```text
01-Arquitetura-da-Infraestrutura.md
↓
visão estrutural

18-Indice-e-Mapa-da-Infraestrutura.md
↓
mapa da família

19-Matriz-de-Ambientes-e-Comandos-Seguros.md
↓
referência operacional de ambientes e comandos
```

Os demais documentos aprofundam áreas especializadas.

## Ambientes

A infraestrutura deve manter separação explícita entre:

```text
desenvolvimento
teste
staging / homologação
produção
```

quando esses ambientes existirem na plataforma.

Um documento ou comando só pode ser considerado seguro quando deixa claro:

- em qual ambiente executa;
- qual settings utiliza;
- qual banco pode atingir;
- quais credenciais/configurações são esperadas;
- qual impacto pode produzir.

## Banco de dados e migrations

A documentação de infraestrutura pode registrar:

- estratégia de persistência;
- configuração do PostgreSQL;
- migrations;
- bootstrap de ambiente;
- continuidade;
- backup e restore;
- incidentes históricos de schema relevantes.

Entretanto, regra de negócio de Models continua pertencendo ao Backend e aos Apps.

## CI/CD, deploy e rollback

`09-CI-CD-Deploy-e-Rollback.md` permanece legítimo nesta pasta quando trata da **infraestrutura da esteira de entrega**.

A divisão é:

```text
infraestrutura/
→ como a esteira e os ambientes suportam entrega

deploy/
→ como uma versão específica é publicada

qualidade/
→ quais gates devem ser satisfeitos
```

Não duplicar procedimentos inteiros entre essas famílias.

## Backup, restore e disaster recovery

`11-Backup-Restore-e-Disaster-Recovery.md` é parte central da infraestrutura.

Todo procedimento desta área deve deixar claro:

- o que é protegido;
- periodicidade;
- retenção;
- onde a cópia fica;
- como restaurar;
- como validar a restauração;
- RPO/RTO quando formalizados;
- responsabilidade operacional.

Backup não validado por restore testado não deve ser tratado como garantia de recuperação.

## Infraestrutura como código e automação

`12-Infraestrutura-como-Codigo-e-Automacao.md` documenta a automação da própria plataforma.

Isso é diferente de:

```text
docs/automacao/
```

que documenta automações funcionais do produto.

A fronteira é:

```text
infraestrutura/
→ automação da plataforma

automacao/
→ automação de funcionalidades do GereIgreja
```

## Escalabilidade e capacidade

`13-Escalabilidade-Alta-Disponibilidade-e-Capacidade.md` deve ser usado para decisões e limites de infraestrutura relacionados a:

- crescimento;
- disponibilidade;
- recursos;
- gargalos;
- capacidade;
- evolução de serviços.

Previsões de escala não devem ser apresentadas como capacidade comprovada sem métricas ou testes correspondentes.

## FinOps

`14-Custos-FinOps-e-Governanca-de-Recursos.md` pertence corretamente à família quando trata do consumo e governança de recursos técnicos.

FinOps deve relacionar custo a:

- ambiente;
- serviço;
- capacidade;
- necessidade operacional;
- risco.

Não deve virar documentação financeira do domínio de negócio.

## Runbooks de infraestrutura

`15-Operacao-Manutencao-e-Runbooks-de-Infraestrutura.md` pode permanecer aqui porque seu escopo é a operação da própria infraestrutura.

A pasta `operacoes/` permanece adequada para runbooks de integrações, módulos ou serviços funcionais.

Evitar copiar o mesmo runbook para ambas.

## Governança de infraestrutura

`16-Governanca-Padroes-e-Evolucao-da-Infraestrutura.md` define governança específica desta família.

Ele não deve criar uma autoridade concorrente com:

```text
docs/governanca/
docs/frameworks/
docs/00-Guia-de-Documentacao.md
```

Seu escopo deve permanecer restrito a infraestrutura.

## Prontidão de produção

`17-Checklist-de-Producao-e-Prontidao-Operacional.md` pode permanecer nesta pasta quando seus critérios são especificamente de infraestrutura.

Se contiver gates gerais de produto, testes funcionais ou homologação, esses critérios devem ser referenciados a partir de `docs/qualidade/`, não duplicados.

## Correções históricas 20 e 21

Os arquivos:

```text
20-Correcao-Historica-Migration-Secretaria-0008.md
21-Correcao-Historica-Migration-Secretaria-0014.md
```

são registros históricos.

Eles podem permanecer nesta família porque documentam incidentes/correções de schema relevantes para bootstrap e integridade de ambientes.

Entretanto:

```text
histórico
≠
padrão atual
```

Esses documentos não devem ser usados como instrução normativa para novas migrations.

A autoridade atual sobre migrations deve vir dos documentos técnicos vigentes de Backend e Infraestrutura.

## Regra para criar novo documento

Antes de criar `22+` ou qualquer novo arquivo nesta família:

1. demonstrar uma lacuna real;
2. verificar `18-Indice-e-Mapa-da-Infraestrutura.md`;
3. confirmar que o assunto não cabe em documento existente;
4. verificar sobreposição com `deploy/`, `operacoes/`, `seguranca/` e `qualidade/`;
5. identificar se o conteúdo é estrutural, operacional ou histórico;
6. preferir evoluir documento existente;
7. atualizar o índice da família;
8. atualizar `docs/INDEX.md` apenas quando necessário.

> O fato de o último documento ser `21` não justifica criar `22`.

## Estado da família

A família é **madura e abrangente**.

Classificação:

```text
Status: CANÔNICA
Cobertura: ALTA
Nova expansão automática: NÃO
Prioridade: manutenção e atualização
```

O principal risco atual não é falta de documentos, mas divergência entre documentação, configuração real e estado dos ambientes.

## Princípio de manutenção

Infraestrutura deve ser verificável e executável.

Todo documento operacional da família deve permitir responder:

```text
Qual ambiente?
Qual serviço?
Qual configuração?
Qual dependência?
Qual impacto?
Como validar?
Como recuperar se falhar?
```

**Evoluir a infraestrutura existente é preferível a aumentar a família documental sem necessidade comprovada.**
