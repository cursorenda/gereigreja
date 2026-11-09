# Auditoria de Arquivos Legados Específicos — GereIgreja

Data: Setembro de 2026  
Status: CONCLUÍDA  
Destino recomendado: `docs/auditoria/`

## Escopo

Foram revisados arquivos antigos que ainda aparecem em buscas, referências históricas ou documentação de transição:

```text
ARQUITETURA_TEMPLATES.md
GRUPOS_PERMISSOES.md
DECORATORS_SEGURANCA.md
SELETOR_IGREJA.md
ANALISE_MENUS_BASEADOS_PERMISSOES.md
LGPD_IMPLEMENTACAO.md
WhatsApp-Bulk-Celular-Edit.md
Deploy-Release-V1.10.1.md
```

O objetivo não é apagar história, mas distinguir:

```text
fonte canônica vigente
registro histórico
documento transitório
documento duplicado
documento mal classificado
```

## 1. ARQUITETURA_TEMPLATES.md

### Estado

```text
CONSOLIDADO / REMOVIDO
```

O conteúdo foi consolidado em:

```text
docs/frontend/05-Templates.md
```

A antiga pasta `docs/templates/` não faz mais parte da árvore ativa.

### Referências

Referências em releases antigas podem permanecer.

`RELEASE_v1.14.8_SUMMARY.md` já preserva corretamente o caminho histórico e informa a consolidação posterior.

### Ação

```text
não recriar
não restaurar
não usar como fonte atual
```

## 2. GRUPOS_PERMISSOES.md

### Estado

O arquivo ainda existe e possui amplo conteúdo histórico sobre grupos e permissões.

Entretanto, sua autoridade foi fragmentada por documentação mais moderna:

```text
docs/apps/09-Usuarios.md
docs/backend/11-Permissions.md
docs/seguranca/03-Gestao-de-Identidade.md
docs/seguranca/04-Autorizacao-e-Controle-de-Acesso.md
docs/seguranca/05-Seguranca-Multi-Tenant.md
docs/frameworks/02-GAF-GereIgreja-Authentication-Framework.md
docs/frameworks/03-GSF-GereIgreja-Security-Framework.md
```

Além disso, existem outros documentos antigos relacionados:

```text
HIERARQUIA_PERMISSOES.md
PERMISSOES_HIERARQUIA.md
ANALISE_GRUPOS_PERMISSOES.md
ESTRUTURA_GRUPOS_COMPLETA.md
DOCUMENTACAO_PADRAO_GRUPOS.md
```

### Risco

Há alta probabilidade de duplicação e divergência histórica.

### Ação recomendada

```text
NÃO apagar agora
NÃO tratar como fonte canônica
```

Executar consolidação específica de Permissões:

1. comparar regras ainda válidas;
2. mover comportamento funcional para `apps/09-Usuarios.md`;
3. mover padrões técnicos para `backend/11-Permissions.md`;
4. mover controles de autorização/tenant para `seguranca/`;
5. atualizar referências correntes;
6. classificar o residual como histórico;
7. retirar o documento antigo somente após referência zero ou deliberadamente histórica.

## 3. DECORATORS_SEGURANCA.md

### Estado

O arquivo ainda existe, mas representa uma documentação antiga de implementação de segurança.

As fontes atuais de autoridade são:

```text
docs/backend/11-Permissions.md
docs/seguranca/04-Autorizacao-e-Controle-de-Acesso.md
docs/seguranca/06-Seguranca-da-Aplicacao.md
docs/frameworks/02-GAF-GereIgreja-Authentication-Framework.md
docs/frameworks/03-GSF-GereIgreja-Security-Framework.md
```

Também existe material histórico relacionado como:

```text
ANALISE_DECORATORS_SISTEMA.md
IMPLEMENTACAO_DECORATOR_DASHBOARD.md
```

### Ação

```text
CONSOLIDAR
→ não promover como fonte vigente
```

Comparar exemplos e regras ainda válidos com Backend e Segurança.

Depois da absorção e atualização de referências, retirar ou arquivar como histórico.

## 4. SELETOR_IGREJA.md

### Estado

O arquivo continua existindo.

Ele documenta um tema crítico de contexto multi-tenant e seleção de igreja ativa.

Pela auditoria de `sistema/`, deve ser tratado como conteúdo transitório, não como autoridade definitiva.

### Destinos canônicos possíveis

O conteúdo deve ser distribuído conforme natureza:

```text
arquitetura/08-Arquitetura-Multi-Tenant.md
→ arquitetura do contexto de tenant

seguranca/05-Seguranca-Multi-Tenant.md
→ isolamento e controles

backend/
→ resolução técnica de contexto, middleware/helpers

frontend/
→ comportamento técnico do seletor visual

usuario/
→ instruções de uso, se necessário
```

### Ação

```text
MANTER TEMPORARIAMENTE
→ consolidar por partes
→ retirar de sistema/ somente após absorção e referências
```

Não mover o arquivo inteiro para uma nova pasta sem separar arquitetura, segurança, implementação e uso.

## 5. ANALISE_MENUS_BASEADOS_PERMISSOES.md

### Estado

É uma análise histórica, não uma especificação normativa.

Seu conteúdo pode ajudar a compreender decisões anteriores sobre navegação e permissões.

### Autoridades atuais

```text
docs/apps/09-Usuarios.md
docs/backend/11-Permissions.md
docs/frontend/
docs/seguranca/04-Autorizacao-e-Controle-de-Acesso.md
```

### Ação

Se possuir recomendações ainda não absorvidas, consolidá-las nas fontes atuais.

O residual deve preferencialmente ser tratado como:

```text
relatorio/análise histórica
```

e não como regra vigente.

## 6. LGPD_IMPLEMENTACAO.md

### Estado

```text
EXISTENTE
MAL CLASSIFICADO EM deploy/
HISTÓRICO DE IMPLEMENTAÇÃO
```

A fonte normativa atual é:

```text
docs/seguranca/14-Conformidade-e-LGPD.md
```

A própria documentação moderna de Segurança já utiliza `LGPD_IMPLEMENTACAO.md` como registro histórico de implementação.

### Ação

Não duplicar seu conteúdo em Deploy.

Antes de mover ou arquivar:

1. verificar todas as referências;
2. manter em Segurança somente fatos atuais e controles;
3. preservar o registro histórico quando tiver valor evidencial;
4. remover a associação conceitual com Deploy.

Destino futuro mais coerente, se for mantido como evidência:

```text
docs/relatorios/
```

ou arquivo histórico equivalente definido pela governança.

Não mover automaticamente antes da revisão de referências.

## 7. WhatsApp-Bulk-Celular-Edit.md

### Estado

O arquivo ainda existe e descreve funcionalidade estável de edição em massa de celulares associada a Comunicação.

Ele não é uma automação operacional propriamente dita.

### Fonte funcional recomendada

```text
docs/apps/04-Comunicacao.md
```

Aspectos técnicos específicos podem ser absorvidos por Frontend/Backend quando realmente reutilizáveis.

### Ação

```text
CONSOLIDAR EM apps/04-Comunicacao.md
```

Preservar releases v1.10.1 como registro histórico.

Depois da absorção:

```text
retirar arquivo isolado
```

somente após conferir referências.

## 8. Deploy-Release-V1.10.1.md

### Estado

É um guia de deploy específico de uma versão.

Isso é compatível com `docs/deploy/` enquanto for preservado como registro de implantação histórica.

### Ação

```text
MANTER COMO HISTÓRICO DE DEPLOY
```

Não transformar em procedimento geral de deploy.

Não alterar para refletir o procedimento atual se isso apagar a forma como a v1.10.1 foi publicada.

## 9. Matriz de decisão

| Arquivo | Estado | Autoridade atual | Ação |
|---|---|---|---|
| `ARQUITETURA_TEMPLATES.md` | removido/consolidado | `frontend/05-Templates.md` | não recriar |
| `GRUPOS_PERMISSOES.md` | legado ativo | Apps/Backend/Segurança/GAF/GSF | consolidar antes de retirar |
| `DECORATORS_SEGURANCA.md` | legado técnico | Backend/Segurança | consolidar |
| `SELETOR_IGREJA.md` | transitório | Arquitetura/Segurança/Backend/Frontend | distribuir conteúdo |
| `ANALISE_MENUS_BASEADOS_PERMISSOES.md` | análise histórica | Apps/Backend/Frontend/Segurança | absorver decisões úteis; manter residual histórico |
| `LGPD_IMPLEMENTACAO.md` | histórico mal classificado | `seguranca/14` | reclassificar após referências |
| `WhatsApp-Bulk-Celular-Edit.md` | funcional isolado | `apps/04-Comunicacao.md` | consolidar |
| `Deploy-Release-V1.10.1.md` | histórico de deploy | `deploy/` | manter |

## 10. Ordem recomendada de saneamento

A sequência mais segura é:

```text
1. GRUPOS_PERMISSOES.md + família antiga de permissões
2. DECORATORS_SEGURANCA.md
3. SELETOR_IGREJA.md
4. ANALISE_MENUS_BASEADOS_PERMISSOES.md
5. WhatsApp-Bulk-Celular-Edit.md
6. LGPD_IMPLEMENTACAO.md
```

`ARQUITETURA_TEMPLATES.md` já está resolvido.

`Deploy-Release-V1.10.1.md` não exige saneamento estrutural imediato.

## 11. Regra de remoção

Nenhum legado deve ser apagado apenas porque existe uma fonte canônica mais nova.

A regra é:

```text
comparar
→ extrair conteúdo único ainda válido
→ atualizar fonte canônica
→ atualizar referências vigentes
→ preservar referências históricas deliberadas
→ somente então retirar o legado
```

## Conclusão

A auditoria não encontrou necessidade de criar novas famílias.

O maior bloco residual agora é a **família histórica de permissões**, porque vários documentos antigos continuam coexistindo com as fontes modernas.

A próxima auditoria deve concentrar-se especificamente em:

```text
GRUPOS_PERMISSOES.md
HIERARQUIA_PERMISSOES.md
PERMISSOES_HIERARQUIA.md
ANALISE_GRUPOS_PERMISSOES.md
ESTRUTURA_GRUPOS_COMPLETA.md
DOCUMENTACAO_PADRAO_GRUPOS.md
DECORATORS_SEGURANCA.md
ANALISE_DECORATORS_SISTEMA.md
```

Esse conjunto deve ser tratado como um único problema de consolidação, não arquivo por arquivo de forma independente.
