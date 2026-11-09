# Produto — Iniciativas, Especificações e Evolução de Produto

Produto  
↓  
Por que uma capacidade existe, qual problema resolve e como sua evolução é estruturada antes de se tornar documentação canônica.

Esta pasta reúne documentação de iniciativas de produto do GereIgreja.

Ela não substitui:

- `docs/apps/` — comportamento funcional canônico dos módulos;
- `docs/usuario/` — orientação de uso;
- `docs/arquitetura/` e `docs/backend/` — arquitetura e implementação técnica;
- `docs/seguranca/` — políticas e controles;
- `docs/release-notes/` — mudanças efetivamente entregues;
- `docs/relatorios/` — análises e diagnósticos históricos.

## Finalidade da pasta

- documentar especificações de novas capacidades antes ou durante sua implementação;
- registrar objetivos de produto;
- explicitar problema, escopo e proposta de valor;
- organizar fases de evolução;
- registrar restrições funcionais relevantes;
- preservar decisões de produto que ainda não tenham sido absorvidas pelas famílias canônicas;
- distinguir planejamento de implementação concluída.

## O que não deve ser centralizado aqui

O README antigo atribuía a esta pasta responsabilidades amplas como:

- regras de negócio;
- roadmap geral;
- personas;
- estratégia comercial;
- funcionalidades de todo o GereIgreja.

Essa definição é ampla demais.

Regras funcionais implementadas pertencem a `docs/apps/`.

Documentação de uso pertence a `docs/usuario/`.

Histórico entregue pertence a `docs/release-notes/`.

Arquitetura técnica pertence às famílias técnicas.

`docs/produto/` deve permanecer focada em **iniciativas de produto e especificações em evolução**.

## Índice atual

| Documento | Natureza | Situação |
|---|---|---|
| [00-Hinario-Base-Juridica.md](00-Hinario-Base-Juridica.md) | Restrição jurídica/compliance da iniciativa Hinário | Manter como evidência da iniciativa; revisar contra Segurança |
| [01-Hinario-Especificacao.md](01-Hinario-Especificacao.md) | Especificação funcional/técnica da iniciativa Hinário | Manter enquanto houver conteúdo não consolidado |
| [02-Hinario-Portal-Usuario.md](02-Hinario-Portal-Usuario.md) | Jornada de produto do Hinário no Portal | Manter e consolidar depois em documentação canônica |
| [10-Fase-1-Completa.md](10-Fase-1-Completa.md) | Registro de conclusão de fase | Histórico da iniciativa; revisar para relatório/release |

## Estado real da pasta

Apesar do nome `produto/`, o conteúdo atual não representa a estratégia geral de produto do GereIgreja.

A pasta está praticamente dedicada a uma única iniciativa:

```text
Hinário
```

Isso inclui:

- base jurídica;
- especificação;
- jornada no Portal;
- registro de conclusão de fase.

Portanto, esta pasta deve ser tratada hoje como uma área de **iniciativas de produto**, não como repositório central de todas as decisões funcionais da plataforma.

## Iniciativa Hinário

A documentação atual descreve um catálogo interno de hinos com:

- compliance jurídico por padrão;
- auditoria;
- isolamento multi-tenant;
- catálogo global com customização por igreja;
- integração ao Portal do Membro.

### Objetivo de produto

A proposta documentada é substituir um link externo por um catálogo interno integrado ao Portal, mantendo controle de direitos autorais e experiência consistente.

### Restrições principais

A iniciativa adota comportamento seguro por padrão:

```text
conteúdo não revisado
→ bloqueado

conteúdo autorizado
→ liberado após revisão
```

Também exige respeito ao contexto da igreja ativa.

## 00-Hinario-Base-Juridica.md

Este documento registra uma política operacional de conformidade para importação e publicação de hinos.

Ele estabelece:

- conteúdo importado bloqueado por padrão;
- revisão antes da publicação;
- registro de responsável;
- rastreabilidade;
- tratamento de licença vencida.

Seu valor dentro da iniciativa é legítimo.

Entretanto, qualquer política de segurança/compliance que se torne regra transversal deve ser consolidada em:

```text
docs/seguranca/
```

ou família jurídica/compliance oficial, caso exista.

Este documento não deve ser tratado como parecer jurídico.

## 01-Hinario-Especificacao.md

A especificação mistura:

- visão funcional;
- models;
- managers;
- signals;
- compliance;
- multi-tenancy;
- auditoria;
- planejamento por fases.

Isso é aceitável como documento de iniciativa durante desenvolvimento.

Quando o módulo estiver estabilizado, o conteúdo deve ser distribuído entre as fontes canônicas:

```text
apps/
→ comportamento funcional

backend/
→ arquitetura de implementação

seguranca/
→ compliance e controles

usuario/
→ jornada de uso
```

Não manter indefinidamente uma especificação de produto como segunda fonte técnica.

## 02-Hinario-Portal-Usuario.md

Este arquivo descreve a jornada de uso do Hinário dentro do Portal:

```text
Meu Portal
↓
Recursos Devocionais
↓
Acessar Hinário
↓
Catálogo
↓
Detalhe do hino
```

Também registra regras de visibilidade e compliance.

Enquanto a iniciativa estiver em evolução, o documento pode permanecer aqui.

Quando a jornada estiver estabilizada, sua orientação de uso deve ser refletida em:

```text
docs/usuario/
```

e o comportamento funcional correspondente na família de app adequada.

## Fases de produto

Documentos de fase devem distinguir claramente:

```text
planejado
em implementação
concluído
cancelado
```

Nunca promover uma fase planejada a comportamento oficial apenas porque foi descrita.

Registros de conclusão de fase podem ser úteis durante desenvolvimento, mas depois devem ser avaliados contra:

- `docs/release-notes/`;
- `docs/relatorios/`;
- documentação canônica do módulo.

## Produto versus Apps

A fronteira principal é:

```text
produto/
→ por que criar e como a iniciativa evolui

apps/
→ o que existe hoje e quais regras estão vigentes
```

Exemplo:

```text
produto/01-Hinario-Especificacao.md
→ especifica a iniciativa

apps/<documento-canônico-do-domínio>.md
→ registra o comportamento efetivamente implementado
```

Quando a implementação estiver estável, `apps/` prevalece.

## Produto versus Usuário

```text
produto/
→ define experiência desejada

usuario/
→ ensina a utilizar a experiência existente
```

Um protótipo de jornada ou proposta ainda não implementada não deve aparecer em manual de usuário.

## Produto versus Release Notes

```text
produto/
→ intenção, escopo, fases

release-notes/
→ entrega comprovada por versão
```

A frase:

```text
“Fase 2 será implementada”
```

é conteúdo de produto/planejamento.

A frase:

```text
“v1.x.y entregou Selectors e Services do Hinário”
```

é conteúdo de release note.

## Regra para criar novo documento de Produto

Antes de criar:

1. confirme que existe uma iniciativa de produto real;
2. verifique se o conteúdo não pertence diretamente a um app já estabilizado;
3. descreva problema e objetivo;
4. informe público ou perfil afetado;
5. delimite escopo;
6. registre restrições;
7. diferencie atual de planejado;
8. indique critérios de sucesso quando aplicável;
9. evite duplicar arquitetura técnica detalhada;
10. defina o destino canônico esperado quando a iniciativa amadurecer.

## Estrutura recomendada para novas iniciativas

Quando uma iniciativa justificar documentação própria, preferir:

```text
XX-Nome-Visao.md
XX-Nome-Especificacao.md
XX-Nome-Jornada.md
XX-Nome-Fases.md
```

somente quando cada documento tiver função distinta.

Não criar múltiplos arquivos apenas para reproduzir etapas de implementação.

## Estado da família

Classificação atual:

```text
Status: VÁLIDA, MAS RESTRITA
Papel: iniciativas e especificações em evolução
Autoridade funcional final: NÃO
Autoridade técnica final: NÃO
Novos documentos: somente com iniciativa comprovada
```

A família pode continuar existindo, mas não deve crescer como pasta-curinga.

## Princípio de manutenção

Produto documenta intenção e evolução.

**Quando a intenção vira implementação estável, a fonte de verdade deve migrar para a família canônica correspondente.**
