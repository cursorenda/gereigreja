# Auditoria de Consolidação — Permissões, Grupos e Decorators Legados

Data: Setembro de 2026  
Status: CONCLUÍDA  
Destino recomendado: `docs/auditoria/`

## Escopo

Esta auditoria trata como um único problema documental o conjunto legado de permissões, grupos, hierarquia e decorators:

```text
GRUPOS_PERMISSOES.md
DOCUMENTACAO_PERMISSOES.md
HIERARQUIA_PERMISSOES.md
PERMISSOES_HIERARQUIA.md
ANALISE_GRUPOS_PERMISSOES.md
ESTRUTURA_GRUPOS_COMPLETA.md
DOCUMENTACAO_PADRAO_GRUPOS.md
DECORATORS_SEGURANCA.md
ANALISE_DECORATORS_SISTEMA.md
governanca/10-Padroes-de-Permissoes.md
```

O objetivo é determinar autoridade, conflitos, destino e ordem segura de consolidação.

## 1. Diagnóstico executivo

O conjunto legado não pode mais ser tratado como uma família normativa coerente.

Há quatro problemas simultâneos:

```text
duplicação
+
documentos de épocas diferentes
+
mistura de regra funcional e técnica
+
contradições explícitas
```

Portanto, a decisão correta não é escolher um desses arquivos como “novo oficial”.

A decisão correta é:

```text
distribuir autoridade
→ Apps
→ Backend
→ Segurança
→ Frameworks
```

e retirar gradualmente os documentos legados depois da absorção de conteúdo único ainda válido.

## 2. Conflito crítico comprovado

`GRUPOS_PERMISSOES.md` afirma que:

```text
is_superuser=True
→ todas as permissões
→ ignora grupos
→ acesso total
```

e descreve isso como regra prática do sistema.

Já `DOCUMENTACAO_PERMISSOES.md` afirma explicitamente:

```text
Superusuário não recebe bypass automático em page_access_required.
```

O mesmo documento diz que o acesso depende da regra de `page_key`, salvo checagem explícita de `is_superuser`.

Essas duas regras não são equivalentes.

Logo:

```text
GRUPOS_PERMISSOES.md
≠
fonte confiável isolada para regra atual
```

Esse conflito é suficiente para impedir qualquer promoção do legado como documentação vigente sem verificação do código atual.

## 3. Problema de temporalidade

`GRUPOS_PERMISSOES.md` está versionado como:

```text
Versão 1.3.0
Última atualização: 12/02/2026
```

Ele declara:

```text
14 grupos
7 níveis hierárquicos
```

e lista permissões concretas para cada grupo.

Esse conteúdo pode ter sido correto em fevereiro de 2026, mas não deve ser transportado automaticamente para a documentação atual.

A família moderna `docs/apps/09-Usuarios.md` foi atualizada em setembro de 2026 e já possui seções próprias para:

```text
grupos de permissão
hierarquia de grupos
cargos e permissões
grupos efetivos
vínculo entre cargo e permissão
igreja ativa e contexto
```

Portanto, a regra é:

```text
listas antigas de grupos
→ verificar contra implementação atual
→ não copiar cegamente
```

## 4. Autoridade atual por assunto

### 4.1 Comportamento funcional de usuários e grupos

Fonte principal:

```text
docs/apps/09-Usuarios.md
```

Deve responder:

- como o usuário se relaciona com Pessoa e Igreja;
- qual o papel funcional dos grupos;
- como contexto de igreja interfere no acesso;
- como cargos e grupos se relacionam;
- quais efeitos funcionais o usuário percebe.

Não deve explicar profundamente implementação de decorators.

### 4.2 Implementação de permissões

Fonte principal:

```text
docs/backend/11-Permissions.md
```

Deve responder:

- como implementar checagens;
- onde ficam helpers e regras;
- uso de permissões Django;
- grupos e roles na implementação;
- padrões de decorators/mixins;
- como evitar lógica duplicada.

### 4.3 Política e controle de acesso

Fontes principais:

```text
docs/seguranca/03-Gestao-de-Identidade.md
docs/seguranca/04-Autorizacao-e-Controle-de-Acesso.md
docs/seguranca/05-Seguranca-Multi-Tenant.md
docs/seguranca/06-Seguranca-da-Aplicacao.md
```

Devem responder:

- autenticação;
- autorização;
- least privilege;
- segregação de responsabilidades;
- isolamento por tenant;
- validação no backend;
- controles de acesso;
- bypasses excepcionais;
- auditoria.

### 4.4 Princípios transversais

Fontes superiores:

```text
docs/frameworks/02-GAF-GereIgreja-Authentication-Framework.md
docs/frameworks/03-GSF-GereIgreja-Security-Framework.md
```

Não usar arquivos antigos de grupos para redefinir princípios de autenticação ou segurança.

## 5. `DOCUMENTACAO_PERMISSOES.md`

Este arquivo é especialmente importante porque registra uma arquitetura concreta baseada em:

```text
@login_required
@page_access_required('<chave>')
PAGE_ACCESS_RULES
contas/page_permissions.py
```

Também declara uma lista de `page_keys` e regras sobre decorators legados.

Isso é tecnicamente valioso.

Porém, sua última revisão informada é abril de 2026.

Portanto:

```text
valor técnico: ALTO
autoridade atual automática: NÃO
```

Antes de absorver seu conteúdo em `backend/11-Permissions.md`, deve ser verificado no código atual:

- `PAGE_ACCESS_RULES` ainda existe?
- continua sendo a matriz central?
- todas as `page_keys` listadas continuam válidas?
- `page_access_required` continua sendo o padrão?
- `check_permission` ainda existe?
- `admin_ministerio_required` continua sendo exceção?
- comportamento de superuser permanece sem bypass automático?

Sem essa verificação, não transformar esse documento antigo em verdade normativa.

## 6. `GRUPOS_PERMISSOES.md`

Classificação:

```text
LEGADO FUNCIONAL + TÉCNICO MISTURADO
```

Problemas:

- mistura Django Admin com interface web;
- lista grupos concretos;
- define responsabilidades funcionais;
- define permissões;
- define hierarquia;
- explica flags `is_staff` e `is_superuser`;
- contém regra conflitante com `DOCUMENTACAO_PERMISSOES.md`.

Destino do conteúdo:

```text
grupos e responsabilidades
→ apps/09-Usuarios.md

mecanismos técnicos
→ backend/11-Permissions.md

segurança e bypass
→ seguranca/04 e seguranca/06
```

Ação:

```text
NÃO manter como documento canônico
NÃO atualizar isoladamente
CONSOLIDAR
```

## 7. `HIERARQUIA_PERMISSOES.md` e `PERMISSOES_HIERARQUIA.md`

A coexistência de dois documentos com nomes praticamente invertidos já é sinal de duplicação histórica.

Eles não devem permanecer como duas autoridades paralelas.

Destino:

```text
hierarquia funcional
→ apps/09-Usuarios.md

regra de precedência/autorização
→ backend/11-Permissions.md + seguranca/04
```

Ação:

```text
comparar
→ extrair diferenças reais
→ absorver conteúdo único
→ retirar ambos
```

Se um deles for apenas resumo do outro, não preservar duplicação por tradição.

## 8. `ESTRUTURA_GRUPOS_COMPLETA.md`

Arquivo extenso, antigo e provavelmente útil como fotografia histórica de estrutura.

Classificação:

```text
HISTÓRICO / FONTE DE CONSOLIDAÇÃO
```

Não usar o termo “completa” como sinal de autoridade atual.

Ação:

- extrair regras ainda válidas;
- comparar com `apps/09-Usuarios.md`;
- manter apenas se tiver valor histórico comprovado;
- caso contrário, retirar após consolidação.

## 9. `ANALISE_GRUPOS_PERMISSOES.md`

Classificação:

```text
ANÁLISE HISTÓRICA
```

Não deve ser convertida em norma.

Destino conceitual do residual:

```text
docs/relatorios/
```

somente se houver valor histórico real após a consolidação.

Se suas conclusões já estiverem integralmente refletidas na documentação atual, pode ser retirada após verificação de referências.

## 10. `DOCUMENTACAO_PADRAO_GRUPOS.md`

O título sugere autoridade normativa, mas a governança atual não deve permitir um padrão de grupos isolado concorrendo com Backend/Segurança/Apps.

Ação:

```text
conteúdo de nomenclatura técnica
→ backend/11-Permissions.md

conteúdo funcional
→ apps/09-Usuarios.md
```

Depois disso:

```text
RETIRAR
```

se não houver conteúdo residual independente.

## 11. `DECORATORS_SEGURANCA.md`

Classificação:

```text
LEGADO TÉCNICO DE SEGURANÇA
```

Destino:

```text
padrão de implementação
→ backend/11-Permissions.md

controles e requisitos
→ seguranca/04
→ seguranca/06
```

Não criar um novo documento `Decorators.md` apenas para preservar o nome antigo.

Decorators são mecanismo, não domínio documental independente.

## 12. `ANALISE_DECORATORS_SISTEMA.md`

Classificação:

```text
ANÁLISE HISTÓRICA
```

Ação:

- usar como fonte para identificar dívida/decisões;
- absorver somente conclusões ainda válidas;
- preservar em `relatorios/` apenas se tiver valor histórico útil;
- não manter como especificação corrente.

## 13. `governanca/10-Padroes-de-Permissoes.md`

Este documento representa a antiga camada normativa centralizada em Governança.

Hoje sua autoridade está distribuída.

Destino:

```text
princípios transversais
→ GAF / GSF

implementação
→ backend/11-Permissions.md

controle de acesso
→ seguranca/04

multi-tenancy
→ seguranca/05
```

Ação:

```text
CONSOLIDAR E RETIRAR GRADUALMENTE
```

Não mover o arquivo inteiro para Backend ou Segurança.

## 14. Matriz final

| Documento | Classificação | Destino principal | Decisão |
|---|---|---|---|
| `GRUPOS_PERMISSOES.md` | legado misto | Apps + Backend + Segurança | consolidar e retirar |
| `DOCUMENTACAO_PERMISSOES.md` | legado técnico valioso | Backend + Segurança | verificar código e absorver |
| `HIERARQUIA_PERMISSOES.md` | legado duplicado | Apps + Backend | consolidar e retirar |
| `PERMISSOES_HIERARQUIA.md` | legado duplicado | Apps + Backend | consolidar e retirar |
| `ESTRUTURA_GRUPOS_COMPLETA.md` | histórico/legado | Apps | extrair e avaliar residual |
| `ANALISE_GRUPOS_PERMISSOES.md` | análise histórica | Relatórios | manter só se houver valor histórico |
| `DOCUMENTACAO_PADRAO_GRUPOS.md` | padrão legado | Backend | absorver e retirar |
| `DECORATORS_SEGURANCA.md` | legado técnico | Backend + Segurança | absorver e retirar |
| `ANALISE_DECORATORS_SISTEMA.md` | análise histórica | Relatórios | preservar só se útil |
| `governanca/10-Padroes-de-Permissoes.md` | norma antiga | Frameworks + Backend + Segurança | consolidar e retirar |

## 15. Ordem segura de execução

### Fase 1 — validar implementação atual

Verificar no código versionado:

```text
PAGE_ACCESS_RULES
page_access_required
check_permission
admin_ministerio_required
user_passes_test_or_403
is_superuser
is_staff
grupos vigentes
hierarquia vigente
escopo de igreja/tenant
```

Sem essa fase, não consolidar afirmações concretas de 2026-02/04 como regras atuais.

### Fase 2 — atualizar fontes canônicas

Nesta ordem:

```text
1. apps/09-Usuarios.md
2. backend/11-Permissions.md
3. seguranca/04-Autorizacao-e-Controle-de-Acesso.md
4. seguranca/05-Seguranca-Multi-Tenant.md
5. seguranca/06-Seguranca-da-Aplicacao.md
```

Frameworks só devem ser atualizados se houver princípio transversal novo, não para absorver detalhe de implementação.

### Fase 3 — corrigir referências atuais

Pesquisar referências aos documentos legados e trocar apenas aquelas que pretendem apontar para documentação vigente.

Referências históricas em releases podem permanecer.

### Fase 4 — retirar legados

Somente depois de:

```text
conteúdo único absorvido
+
referências atuais corrigidas
+
histórico deliberado preservado
```

retirar os documentos redundantes.

## 16. O que não fazer

Não:

- escolher `GRUPOS_PERMISSOES.md` como novo canônico;
- copiar a lista de 14 grupos sem validar código atual;
- assumir sete níveis como regra permanente;
- assumir bypass de superuser;
- assumir ausência de bypass de superuser;
- criar novo documento só para decorators;
- mover todos os arquivos para `seguranca/`;
- manter duas hierarquias paralelas;
- apagar releases antigas que referenciam esses arquivos.

## 17. Conclusão

O problema de Permissões não é falta de documentação.

É excesso de documentação concorrente.

A solução correta é:

```text
menos documentos
+
autoridade mais clara
+
verificação no código
+
consolidação nas famílias modernas
```

O maior risco técnico identificado é a contradição explícita sobre o comportamento de `is_superuser` entre documentos legados.

Portanto, o próximo passo não deve ser editar documentos imediatamente.

O próximo passo deve ser:

```text
AUDITAR A IMPLEMENTAÇÃO ATUAL DE PERMISSÕES NO CÓDIGO
```

e somente então consolidar as regras concretas nas fontes canônicas.
