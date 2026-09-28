# Regras obrigatórias para agentes no GereIgreja

Este arquivo define regras operacionais obrigatórias para agentes de IA, automações e assistentes que atuem no repositório GereIgreja.

As regras abaixo existem para evitar ações ambíguas, acesso indevido a ambientes, uso incorreto de settings, alterações sem contexto documental e mudanças que contradigam a arquitetura vigente.

## 1. Princípio geral

Toda ação deve ser:

- local por padrão;
- explícita quanto ao ambiente;
- limitada ao escopo pedido;
- coerente com a documentação canônica;
- reversível quando possível;
- auditável;
- segura para dados e infraestrutura.

Nunca ampliar o escopo apenas porque uma alteração relacionada parece conveniente.

## 2. Autoridade documental

Antes de alterar código, configuração, documentação ou operação, consulte a documentação oficial aplicável.

Ordem de referência:

```text
docs/00-Guia-de-Documentacao.md
→ define onde e como documentar

docs/INDEX.md
→ define o mapa global de famílias e autoridades

README.md da família
→ define escopo e fronteiras locais

documento canônico do domínio
→ define a regra vigente

release notes / changelog / relatórios / auditorias
→ registram histórico e evidências
```

Registros históricos não substituem documentação normativa vigente.

Se código e documentação canônica divergirem:

```text
PARAR
→ reportar a divergência
→ não assumir silenciosamente qual lado está correto
```

## 3. Regra documental

Princípio obrigatório:

> **Evoluir antes de criar. Consolidar antes de duplicar. Criar somente diante de uma lacuna demonstrável.**

Antes de criar novo `.md`:

1. procurar documento existente;
2. avaliar se uma seção pode ser atualizada;
3. verificar se há documento canônico do domínio;
4. verificar se o conteúdo pertence a outra família;
5. criar novo arquivo somente se houver lifecycle e autoridade próprios.

Não criar documentos para preencher sequência numérica.

## 4. Ambiente seguro por padrão

- Toda operação é local por padrão.
- Nunca leia, carregue, copie, exiba ou utilize o arquivo `.env`.
- Nunca revele credenciais, tokens, secrets ou chaves.
- Nunca conecte a PostgreSQL remoto, Supabase ou outro banco remoto sem autorização explícita do usuário para aquela operação.
- Nunca trate pedidos genéricos como autorização para produção.
- Ambiente, settings ou banco ambíguo significa **parar e pedir confirmação**.
- Não inferir ambiente correto pela ausência de `--settings`.

## 5. Settings obrigatórios

Use:

```text
core.settings_local
→ desenvolvimento e comandos locais

core.settings_test
→ testes Django

core.settings_test_migrations
→ testes reais de migrations
```

Não use:

```text
core.settings
```

em comandos locais.

Esse módulo permanece reservado ao fluxo produtivo legado enquanto a separação de ambientes não estiver formalmente concluída.

## 6. Banco de dados

Antes de qualquer comando que possa acessar ou alterar banco:

1. identificar o settings;
2. identificar o ENGINE;
3. identificar o NAME/host alvo;
4. confirmar se é local, teste ou produção;
5. interromper se houver ambiguidade.

Nunca usar `.env` para descobrir credenciais de produção.

Prefira inspecionar somente:

- código versionado;
- nomes de variáveis;
- settings locais/teste;
- documentação de infraestrutura.

## 7. Migrations

Não execute migrations durante tarefas locais comuns.

Comandos como:

```text
migrate
makemigrations
showmigrations
sqlmigrate
```

devem ser tratados conforme seu efeito e ambiente.

Antes de qualquer operação de migration com potencial de escrita:

- confirmar o banco alvo;
- confirmar o settings;
- confirmar escopo;
- avaliar impacto;
- verificar documentação relevante;
- preservar backup quando aplicável.

Para produção, exigir:

```text
autorização explícita
+
ambiente inequívoco
+
backup atual
+
restore comprovado
+
plano da migration
+
alvo exato
```

Nunca executar `--fake` automaticamente.

Nunca corrigir uma migration falha de forma improvisada sem primeiro identificar a causa.

## 8. Testes

Use:

```text
python manage.py test --settings=core.settings_test
```

ou a estratégia documentada em:

```text
docs/desenvolvimento/Como-Rodar-Testes.md
```

Quando pytest for aplicável, usar a configuração oficial do projeto.

Não utilizar testes como justificativa para acessar produção.

Não executar migrations reais apenas porque uma suíte falhou.

## 9. Produção

Nenhuma operação produtiva pode ser inferida implicitamente.

Produção exige autorização explícita para a ação concreta.

São exemplos de ações que exigem confirmação inequívoca:

- migrations;
- alterações de dados;
- deploy;
- rollback;
- restauração de backup;
- rotação de secrets;
- acesso a banco remoto;
- alteração de infraestrutura;
- execução de comandos destrutivos.

Se o pedido disser apenas:

```text
rode
corrija
teste
verifique
aplique
```

isso **não** equivale a autorização para produção.

## 10. Multi-tenancy e isolamento

O GereIgreja é multi-tenant.

Qualquer alteração que toque dados, permissões ou consultas deve considerar explicitamente:

```text
usuário
igreja ativa
igreja_id
ministério
escopo permitido
```

Ocultar informação no frontend não constitui segurança.

Validação de escopo deve existir no backend.

Nunca remover filtros de tenant apenas para “fazer funcionar”.

## 11. Segurança

Ao alterar autenticação, autorização, permissões, sessão, middleware, decorators, APIs ou escopo de tenant, consultar:

```text
docs/frameworks/02-GAF-GereIgreja-Authentication-Framework.md
docs/frameworks/03-GSF-GereIgreja-Security-Framework.md
docs/seguranca/
```

Princípios distintos:

```text
Autenticação
→ quem é o usuário

Autorização
→ o que pode fazer

Tenant
→ sobre quais dados pode operar
```

Não misturar esses conceitos.

## 12. Arquitetura

Mudanças estruturais devem consultar:

```text
docs/arquitetura/
```

Quando a alteração envolver decisão com alternativas relevantes e consequências duradouras, avaliar criação ou atualização de ADR em:

```text
docs/adr/
```

Não usar ADR para descrever simplesmente o estado atual.

## 13. Backend

Para implementação Django, consultar:

```text
docs/backend/
```

Não recriar padrões locais de:

- Models;
- Services;
- Selectors;
- Managers;
- Views;
- Forms;
- Validators;
- Permissions;
- Middlewares;
- Signals;
- Tasks;
- Logging;
- Exceptions;
- Testing;
- Code Standards;

quando já houver documento canônico.

## 14. Frontend e Design System

Consultar:

```text
docs/frontend/
docs/design-system/
```

Separação:

```text
design-system/
→ o que a interface deve parecer

frontend/
→ como implementar
```

Não recriar antigas famílias:

```text
docs/design/
docs/ui/
docs/templates/
```

## 15. APIs

Mudanças de contrato, endpoint, payload, autenticação, versionamento, webhook ou erro de API devem consultar:

```text
docs/api/
```

Não inventar endpoints ou capacidades que não existam.

## 16. Infraestrutura, Operações e Deploy

Separação obrigatória:

```text
docs/infraestrutura/
→ plataforma e ambiente

docs/operacoes/
→ operação recorrente e runbooks

docs/deploy/
→ publicação e implantação

docs/qualidade/
→ critérios de validação
```

Não mover procedimento de um domínio para outro apenas por proximidade temática.

## 17. Inteligência Artificial

Para mudanças relacionadas a IA, consultar:

```text
docs/ai/
```

A família GAI possui baseline:

```text
GAI-01 ... GAI-35
```

Estado:

```text
GAI Framework 1.0
FREEZE ESTRUTURAL
```

Não criar `GAI-36+` sem Gap Analysis formal.

## 18. Famílias em consolidação

### `docs/governanca/`

Válida, mas em consolidação.

Documentos técnicos antigos podem ter sido superados por Backend, Arquitetura, Segurança, Qualidade ou GDF.

Não assumir que um padrão antigo em `governanca/` é a autoridade atual sem comparar com as famílias canônicas.

### `docs/sistema/`

Família transitória.

```text
NOVOS DOCUMENTOS: NÃO
```

Conteúdo existente pode servir como fonte histórica para consolidação, mas não deve ser tratado como destino padrão.

## 19. Arquivos legados e referências antigas

Não renomear, mover ou excluir documento legado automaticamente.

Fluxo obrigatório:

```text
identificar
→ comparar
→ extrair conteúdo válido
→ atualizar fonte canônica
→ corrigir referências
→ classificar residual
→ arquivar/remover
```

Releases e changelogs podem preservar caminhos históricos.

Não “corrigir” história apagando referências que eram verdadeiras na época.

## 20. Alterações de código

Antes de alterar:

- entender a finalidade do arquivo;
- verificar padrão do domínio;
- localizar testes relacionados;
- verificar impactos de permissão e tenant;
- evitar refatoração não solicitada;
- não ampliar a mudança por conveniência.

Depois de alterar:

- executar validações compatíveis com o escopo;
- não acessar produção;
- verificar `git diff`;
- verificar inconsistências;
- atualizar documentação quando necessário.

## 21. Git

Não executar automaticamente:

```text
git add
git commit
git push
git reset --hard
git clean -fd
```

sem pedido explícito.

Inspeções seguras como:

```text
git status
git diff
git diff --check
```

podem ser usadas quando pertinentes.

Não sobrescrever alterações do usuário.

## 22. Arquivos sensíveis

Nunca ler ou expor:

```text
.env
tokens
API keys
senhas
credenciais
secrets
```

Se uma configuração depende desses valores, trabalhar apenas com:

- nomes esperados;
- código que os referencia;
- documentação;
- valores fictícios quando necessário.

## 23. Ações destrutivas

Comandos destrutivos exigem autorização explícita.

Exemplos:

```text
DROP
DELETE em massa
TRUNCATE
flush
git reset --hard
git clean
remoção de migration aplicada
remoção de banco
rollback destrutivo
```

Nunca executar por inferência.

## 24. Regra de parada

Pare e reporte quando houver:

- ambiente ambíguo;
- banco ambíguo;
- settings ambíguo;
- conflito entre código e documentação canônica;
- risco de produção não autorizado;
- operação destrutiva não confirmada;
- dependência de secret;
- escopo maior que o pedido;
- decisão arquitetural não resolvida.

Parar é comportamento correto quando a continuidade exigiria assumir algo crítico.

## 25. Regra final

```text
Segurança
+
Escopo explícito
+
Documentação canônica
+
Validação
+
Rastreabilidade
=
Mudança confiável
```

Quando houver dúvida entre agir e preservar segurança, preservar segurança e reportar a dúvida.

## Revisão visual obrigatória para alterações de arquivos

Para qualquer CRIAÇÃO ou ALTERAÇÃO de arquivo persistente do projeto
dentro do repositório Gereigreja — seja ele já versionado ou novo
arquivo destinado a versionamento:

1. Use obrigatoriamente a ferramenta nativa de edição/patch do agente
   ou da IDE, quando disponível, para alterações normais em arquivos
   persistentes do projeto, de forma que a alteração seja apresentada
   em diff visual para revisão humana.

   Quando o agente ou ambiente não oferecer edição/patch com revisão
   visual, qualquer outra forma de escrita exige autorização explícita
   do usuário para aquela operação específica, conforme o item 7.

2. NÃO use comandos de terminal para escrever ou sobrescrever arquivos
   persistentes do projeto dentro do repositório, já versionados ou
   destinados a versionamento, salvo autorização explícita do usuário
   para aquela operação específica.

3. São proibidos por padrão, quando direcionados a arquivos persistentes
   do projeto dentro do repositório, já versionados ou destinados a
   versionamento:

   - Set-Content
   - Add-Content
   - Out-File
   - redirecionamento > ou >>
   - Python Path.write_text / write_bytes
   - open(..., "w") / open(..., "a")
   - os.write para arquivos persistentes do projeto
   - sed -i
   - perl -pi
   - cópia/sobrescrita de arquivo persistente do projeto
   - scripts PowerShell/Python usados para reescrever código
   - git checkout/restore/reset para modificar o worktree

4. O terminal pode ser usado normalmente para operações somente leitura
   e validação, incluindo:

   - git status
   - git diff
   - git show
   - git log
   - git grep
   - git blame
   - git rev-parse
   - git hash-object
   - testes
   - lint/checks
   - inspeções AST
   - materialização em diretórios temporários FORA do repositório

   Arquivos temporários, diagnósticos ou materializações que não façam
   parte do projeto devem ser criados fora do repositório sempre que
   possível e não estão sujeitos à revisão visual de código.

5. Antes de editar um arquivo persistente do projeto, informar brevemente:
   - qual arquivo será alterado;
   - qual mudança será feita;
   - por quê.

6. A revisão visual do diff pelo usuário deve ocorrer antes de considerar
   a alteração aprovada.

7. Exceções a esta regra exigem autorização explícita do usuário na
   tarefa atual.
