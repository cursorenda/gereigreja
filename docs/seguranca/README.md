# Segurança — Controles, Isolamento e Conformidade

Segurança  
↓  
Como os princípios do GereIgreja Security Framework são aplicados tecnicamente em toda a plataforma.

Esta pasta reúne a documentação canônica de segurança do GereIgreja.

Ela detalha controles, padrões e procedimentos técnicos para identidade, autorização, multi-tenancy, aplicação, APIs, dados, infraestrutura, observabilidade, continuidade, vulnerabilidades, incidentes, conformidade e desenvolvimento seguro.

## Finalidade da pasta

- transformar princípios do GSF em controles técnicos verificáveis;
- documentar proteção de dados e informações;
- definir gestão de identidade;
- definir autorização e controle de acesso;
- proteger isolamento multi-tenant;
- orientar segurança da aplicação;
- orientar segurança das APIs;
- orientar segurança da infraestrutura e de segredos;
- registrar logging, monitoramento e auditoria;
- documentar continuidade e recuperação;
- estabelecer gestão de vulnerabilidades;
- estabelecer gestão de incidentes;
- consolidar conformidade e LGPD;
- orientar secure development lifecycle;
- governar a evolução da segurança.

## Relação com Frameworks

A relação correta é:

```text
docs/frameworks/03-GSF-GereIgreja-Security-Framework.md
→ princípios e autoridade normativa transversal

docs/seguranca/
→ aplicação técnica e controles especializados
```

Autenticação e identidade também devem permanecer alinhadas ao:

```text
docs/frameworks/02-GAF-GereIgreja-Authentication-Framework.md
```

A família de Segurança não deve criar um sistema paralelo de autenticação.

## Inventário atual

A família possui o baseline:

```text
01-Fundamentos-de-Seguranca.md
02-Classificacao-e-Protecao-da-Informacao.md
03-Gestao-de-Identidade.md
04-Autorizacao-e-Controle-de-Acesso.md
05-Seguranca-Multi-Tenant.md
06-Seguranca-da-Aplicacao.md
07-Seguranca-das-APIs.md
08-Seguranca-de-Dados-e-Privacidade.md
09-Seguranca-de-Infraestrutura-e-Segredos.md
10-Logging-Monitoramento-e-Auditoria.md
11-Backup-Continuidade-e-Recuperacao.md
12-Gestao-de-Vulnerabilidades.md
13-Gestao-de-Incidentes-de-Seguranca.md
14-Conformidade-e-LGPD.md
15-Secure-Development-Lifecycle.md
16-Governanca-de-Seguranca.md
17-Mapa-e-Indice-da-Seguranca.md
```

O mapa detalhado da família é:

```text
17-Mapa-e-Indice-da-Seguranca.md
```

## Estado real da família

```text
Status: CANÔNICA
Baseline: 01–17
Cobertura: ALTA
Expansão automática: NÃO
Prioridade: manutenção, aderência ao sistema e consolidação de legado
```

A existência de `17` não justifica criar `18`.

## Multi-tenancy

O isolamento entre igrejas é requisito estrutural.

A documentação deve considerar que um usuário autenticado não pode acessar dados de outra igreja por manipulação de:

- URL;
- formulário;
- identificador;
- parâmetro;
- payload;
- API;
- JavaScript.

A proteção deve ocorrer no backend.

```text
ocultar no frontend
≠
autorizar
```

## Identidade, autenticação e autorização

A distinção deve permanecer explícita:

```text
identidade
→ quem é o usuário

autenticação
→ comprova a identidade

autorização
→ define o que ele pode fazer

tenant
→ define sobre quais dados pode operar
```

Esses conceitos não devem ser tratados como equivalentes.

## Segurança da aplicação

A família deve orientar proteção contra classes conhecidas de falhas, incluindo:

- CSRF;
- XSS;
- SQL Injection;
- entrada inválida;
- manipulação de parâmetros;
- exposição indevida de informações;
- falhas de autorização;
- tratamento inadequado de exceções.

Sempre que possível, utilizar mecanismos nativos do Django corretamente.

## APIs

`07-Seguranca-das-APIs.md` aplica controles de segurança à superfície de API.

A política geral continua em Segurança/GSF, enquanto:

```text
docs/api/
→ contrato e comportamento das APIs

docs/seguranca/
→ requisitos de proteção
```

## Dados e privacidade

`08-Seguranca-de-Dados-e-Privacidade.md` e `14-Conformidade-e-LGPD.md` devem permanecer alinhados.

A divisão recomendada é:

```text
08
→ controles técnicos de proteção de dados

14
→ conformidade, LGPD, governança e critérios jurídicos/operacionais
```

Nenhum desses documentos deve ser tratado como parecer jurídico.

## Infraestrutura e segredos

`09-Seguranca-de-Infraestrutura-e-Segredos.md` define requisitos de proteção.

`docs/infraestrutura/` documenta a implementação da plataforma.

```text
seguranca/
→ o que precisa ser protegido

infraestrutura/
→ como o ambiente materializa essa proteção
```

Segredos não devem ser armazenados em código-fonte ou documentação.

## Logging, monitoramento e auditoria

`10-Logging-Monitoramento-e-Auditoria.md` define requisitos de rastreabilidade.

A implementação pode envolver:

```text
backend/
infraestrutura/
operacoes/
```

Logs não devem expor senhas, tokens, segredos ou dados pessoais desnecessários.

## Backup e continuidade

`11-Backup-Continuidade-e-Recuperacao.md` trata backup sob a ótica de segurança e disponibilidade.

`docs/infraestrutura/11-Backup-Restore-e-Disaster-Recovery.md` trata a implementação de infraestrutura.

Esses documentos devem ser complementares, não duplicados.

Princípio:

```text
backup sem teste de restauração
→ não é garantia de recuperação
```

## Vulnerabilidades

`12-Gestao-de-Vulnerabilidades.md` deve orientar identificação, priorização, correção e acompanhamento.

Vulnerabilidade conhecida não deve permanecer apenas em relatório sem responsável e tratamento definido.

## Incidentes

`13-Gestao-de-Incidentes-de-Seguranca.md` define o processo:

```text
detecção
↓
classificação
↓
contenção
↓
correção
↓
recuperação
↓
lições aprendidas
```

Resultados concretos de incidentes podem gerar evidências em relatórios ou auditorias, mas o procedimento permanece nesta família.

## Conformidade e LGPD

`14-Conformidade-e-LGPD.md` é a fonte canônica da família para conformidade e proteção de dados pessoais.

Ele deve prevalecer sobre documentos antigos ou específicos de deploy que tratem LGPD como implementação isolada.

Conformidade não substitui controles técnicos.

## Secure Development Lifecycle

`15-Secure-Development-Lifecycle.md` integra segurança ao ciclo de desenvolvimento.

A lógica correta é:

```text
requisito
↓
análise de segurança
↓
arquitetura
↓
implementação
↓
revisão
↓
testes
↓
release
↓
monitoramento
```

Segurança posterior à implementação não deve ser o padrão.

## Governança de segurança

`16-Governanca-de-Seguranca.md` governa a evolução desta família.

Ele não substitui:

```text
docs/governanca/
docs/frameworks/
docs/00-Guia-de-Documentacao.md
```

Seu escopo é a governança específica de segurança.

## Mapa e índice

`17-Mapa-e-Indice-da-Seguranca.md` encerra o baseline atual.

Ele deve ser utilizado como mapa detalhado para evitar que o README replique toda a estrutura.

## Relação com Governança antiga

Os arquivos:

```text
docs/governanca/10-Padroes-de-Permissoes.md
docs/governanca/11-Padroes-de-Seguranca.md
```

são hoje documentos legados concorrentes.

A família atual já possui referências mais específicas para os mesmos temas, especialmente:

```text
03-Gestao-de-Identidade.md
04-Autorizacao-e-Controle-de-Acesso.md
05-Seguranca-Multi-Tenant.md
06-Seguranca-da-Aplicacao.md
16-Governanca-de-Seguranca.md
```

além dos frameworks GAF e GSF.

A ação correta é:

```text
comparar conteúdo
↓
absorver apenas informação exclusiva ainda válida
↓
corrigir referências
↓
arquivar ou remover o legado
```

Não mover os documentos antigos para `seguranca/` integralmente.

## Relação com Backend

`backend/11-Permissions.md` documenta implementação técnica.

```text
GAF/GSF/seguranca/
→ política e controles

backend/11-Permissions.md
→ implementação
```

## Relação com Qualidade

Segurança define requisitos.

Qualidade define gates e validação.

```text
seguranca/
→ padrão esperado

qualidade/
→ comprovação e verificação
```

## Regra para novo documento 18+

Antes de criar novo documento:

1. demonstrar lacuna real;
2. verificar `01–17`;
3. consultar `17-Mapa-e-Indice-da-Seguranca.md`;
4. verificar sobreposição com GAF, GSF, Backend, API, Infraestrutura e Qualidade;
5. preferir evolução de documento existente;
6. criar somente tema autônomo e duradouro;
7. atualizar mapa e README.

## Princípio de manutenção

Segurança é transversal, mas a documentação não deve ser redundante.

**Uma política deve existir em uma fonte canônica e ser aplicada pelas famílias técnicas correspondentes.**
