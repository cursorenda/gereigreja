# Auditoria Final de Referências Legadas — GereIgreja

Data: Setembro de 2026  
Status: CONCLUÍDA  
Escopo: referências a caminhos documentais removidos ou consolidados.

## Caminhos auditados

```text
docs/design/
docs/ui/
docs/templates/
docs/marketing/
docs/administrador/
```

## Resultado executivo

A reorganização estrutural está consistente.

Não foi encontrada evidência de `docs/administrador/` como família ativa.

As referências restantes aos caminhos removidos se dividem em três classes:

```text
1. referência histórica válida
2. referência deliberada explicando consolidação
3. referência atual obsoleta que precisa correção
```

Apenas a terceira classe deve ser corrigida.

## 1. Referências históricas que devem permanecer

### RELEASE_v1.14.0_SUMMARY.md

A release v1.14.0 registrou a estrutura documental existente naquela época.

Menções a famílias como:

```text
docs/design/
docs/ui/
docs/marketing/
```

podem permanecer porque documentam o estado histórico daquela release.

Recomendação:

- não reescrever silenciosamente o passado;
- quando necessário, acrescentar nota de consolidação posterior;
- não transformar o release summary em documentação vigente.

### RELEASE_v1.14.8_SUMMARY.md

A referência:

```text
docs/templates/ARQUITETURA_TEMPLATES.md
```

já está corretamente acompanhada da informação de que o documento foi posteriormente consolidado em:

```text
docs/frontend/05-Templates.md
```

Nenhuma ação necessária.

### Release Notes antigas

Referências a arquivos que existiam na época devem permanecer quando descrevem entregas históricas.

Exemplo:

```text
ARQUITETURA_TEMPLATES.md
```

em releases antigas.

Histórico não deve ser reescrito apenas porque a estrutura atual mudou.

## 2. Referências deliberadas e corretas

Os documentos atuais abaixo mencionam caminhos removidos para explicar a consolidação:

```text
docs/README.md
docs/INDEX.md
docs/00-Guia-de-Documentacao.md
docs/frontend/README.md
```

Essas referências não são links operacionais para famílias ativas.

Elas registram explicitamente que os caminhos foram removidos ou consolidados.

Portanto, devem permanecer.

## 3. Correção necessária — estrategia-digital/README.md

O README atual de:

```text
docs/estrategia-digital/
```

ainda contém texto produzido antes da remoção de `docs/marketing/`, tratando a pasta como existente e vazia.

Esse estado ficou obsoleto depois da consolidação.

Substituir a seção sobre Marketing por algo equivalente a:

```markdown
## Relação com Marketing

A antiga pasta:

`docs/marketing/`

foi consolidada nesta família e não faz mais parte da árvore documental ativa.

A autoridade atual é:

estrategia-digital/
→ posicionamento, SEO, conteúdo, aquisição, conversão e métricas

Campanhas operacionais futuras somente justificam uma família própria se houver volume, lifecycle e responsabilidade claramente distintos que não possam ser absorvidos por `estrategia-digital/`.

Não recriar `marketing/` apenas para separar conteúdo por conveniência.
```

Essa é a principal referência estrutural atual que precisa correção.

## 4. Problema adicional crítico — README principal do projeto

O arquivo:

```text
C:\Gereigreja\README.md
```

não está sincronizado com a documentação atual.

Ele ainda contém links antigos como:

```text
docs/ARQUITETURA_TEMPLATES.md
docs/GRUPOS_PERMISSOES.md
docs/LGPD_IMPLEMENTACAO.md
docs/DECORATORS_SEGURANCA.md
docs/SELETOR_IGREJA.md
docs/ANALISE_MENUS_BASEADOS_PERMISSOES.md
docs/WHATSAPP_BULK_CELULAR_EDIT.md
docs/DEPLOY_RELEASE_v1.10.1.md
```

Além disso, o README principal ainda apresenta uma estrutura documental e versão do sistema antigas.

Esses links não devem ser corrigidos isoladamente sem revisão completa do README.

Recomendação:

```text
README principal do projeto
→ AUDITORIA COMPLETA
→ substituir referências antigas por pontos de entrada canônicos
```

Os principais links documentais do README principal deveriam preferir:

```text
docs/README.md
docs/INDEX.md
docs/00-Guia-de-Documentacao.md
docs/apps/
docs/arquitetura/
docs/backend/
docs/frontend/
docs/seguranca/
docs/usuario/
docs/release-notes/
CHANGELOG.md
```

Evitar links profundos para documentos legados quando houver uma família canônica.

## 5. LGPD

O documento:

```text
docs/deploy/LGPD_IMPLEMENTACAO.md
```

ainda existe como registro histórico/mal classificado.

A autoridade vigente é:

```text
docs/seguranca/14-Conformidade-e-LGPD.md
```

Referências em documentos modernos que apontam para `deploy/LGPD_IMPLEMENTACAO.md` devem fazê-lo apenas como evidência histórica.

Não tratar esse arquivo como norma vigente.

A remoção ou arquivamento futuro exige primeiro verificar todas as referências.

## 6. Resultado por caminho

| Caminho legado | Estado | Ação |
|---|---|---|
| `docs/design/` | removido | manter apenas referências históricas/explicativas |
| `docs/ui/` | removido | manter apenas referências históricas/explicativas |
| `docs/templates/` | removido | referência histórica válida; canônico é Frontend |
| `docs/marketing/` | removido | corrigir `estrategia-digital/README.md` |
| `docs/administrador/` | inexistente | nenhuma ação; não recriar |

## 7. Critério para referências antigas

Usar a seguinte regra:

```text
Documento vigente apontando para caminho antigo como se existisse
→ CORRIGIR

Documento vigente dizendo que caminho foi removido/consolidado
→ MANTER

Release/changelog registrando caminho que existia naquela época
→ MANTER

Release histórica usada como instrução atual
→ CORRIGIR contexto, não apagar história
```

## 8. Próxima prioridade

A reorganização de `docs/` está estruturalmente fechada.

O próximo documento que merece auditoria é:

```text
C:\Gereigreja\README.md
```

Motivo:

- contém links documentais quebrados/legados;
- descreve estrutura antiga;
- mistura documentação funcional histórica com apresentação atual;
- apresenta informações de versão antigas;
- é o primeiro ponto de entrada do repositório.

Depois do README principal, revisar:

```text
AGENTS.md
```

somente para garantir que os caminhos documentais e regras de leitura estejam alinhados ao GDF atual.

## Conclusão

A árvore `docs/` está consistente.

O principal residual interno é:

```text
docs/estrategia-digital/README.md
→ atualizar relação com marketing/
```

O maior residual fora da árvore é:

```text
README.md da raiz do projeto
→ revisão completa necessária
```
