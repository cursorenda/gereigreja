# Ambientes do GereIgreja — Local, Demo e Produção

Data: Setembro de 2026  
Status: CANÔNICO PARA DESENVOLVIMENTO E OPERAÇÃO

## 1. Objetivo

O GereIgreja deve ser entendido e operado a partir de três contextos:

```text
LOCAL
DEMO
PRODUÇÃO
```

Regra central:

```text
LOCAL      → desenvolver e testar
DEMO       → demonstrar o produto
PRODUÇÃO   → operar igrejas reais
```

A Demo não substitui o ambiente local de desenvolvimento, e Produção nunca deve ser usada como laboratório.

## 2. Visão geral

| Contexto | Finalidade principal | Dados | Pode experimentar? |
|---|---|---|---|
| LOCAL | Desenvolvimento, testes, permissões, migrations e validação funcional | Fictícios | Sim |
| DEMO | Demonstração do produto | Controlados de demonstração | Não como ambiente de desenvolvimento |
| PRODUÇÃO | Operação real das igrejas clientes | Reais | Não |

## 3. LOCAL

O ambiente Local é o ambiente de desenvolvimento.

Endereço típico:

```text
http://127.0.0.1:8000
```

Configuração esperada:

```text
core.settings_local
```

Banco local esperado:

```text
C:\Gereigreja\db.sqlite3
```

O desenvolvimento normal deve ocorrer neste ambiente.

Finalidades:

```text
desenvolver funcionalidades
testar permissões
testar regras de negócio
validar migrations
executar testes automatizados
fazer testes visuais
criar e apagar dados fictícios
testar diferentes perfis de usuário
validar fluxos multi-tenant
```

Deve existir apenas um banco SQLite local para o desenvolvimento normal. Evitar múltiplos bancos por perfil de usuário.

Estrutura fictícia recomendada:

```text
MINISTÉRIO TESTE LOCAL

├── Igreja Sede Local
├── Regional Teste
└── Congregação Teste
```

Usuários funcionais previsíveis:

```text
admin_ministerio_local
pastor_local
secretario_local
tesoureiro_local
membro_local
multi_funcao_local
```

Um usuário técnico como `admin_local` pode existir para administração técnica local, mas não deve ser usado como referência para testes funcionais, porque:

```text
superuser Django
≠
papel funcional real do GereIgreja
```

A direção recomendada é possuir um único comando de preparação:

```powershell
python manage.py popular_ambiente_local --settings=core.settings_local
```

Esse comando deve preparar ou atualizar o Ministério fictício, igrejas, usuários, grupos, vínculos, permissões e dados mínimos. Deve ser idempotente sempre que possível.

O ambiente Local deve possuir sinalização visual explícita, por exemplo:

```text
🧪 LOCAL — dados fictícios
```

## 4. DEMO

A Demo é um contexto de demonstração do produto.

Ela pode utilizar a mesma aplicação publicada utilizada pela Produção, mas deve ser tratada como um tenant especial de demonstração.

Conceitualmente:

```text
Aplicação publicada
├── tenants reais
└── tenant Demonstração
```

A Demo existe para:

```text
apresentar funcionalidades
permitir avaliação comercial
simular experiência do produto
mostrar fluxos controlados
```

Ela não deve ser usada para:

```text
testar código novo
experimentar migrations
validar permissões em desenvolvimento
executar testes destrutivos
substituir o SQLite local
```

A Demo acompanha o deploy da aplicação publicada, mas não vira uma etapa de desenvolvimento.

Ela deve possuir proteções específicas para integrações externas como WhatsApp, e-mail, webhooks, notificações e terceiros.

A identificação visual deve ser própria, por exemplo:

```text
🎯 Ambiente de Demonstração
```

## 5. PRODUÇÃO

Produção é o ambiente onde operam igrejas reais e usuários finais reais.

Regra:

```text
Produção não é ambiente de teste.
```

Não usar Produção para:

```text
experimentar funcionalidade
criar dados aleatórios de teste
apagar dados para verificar comportamento
testar permissões informalmente
rodar comandos de teste
testar migrations manualmente
usar contas reais como laboratório
```

Após deploy, podem ser executados apenas smoke tests pequenos e controlados, por exemplo:

```text
aplicação abre?
login funciona?
dashboard abre?
rotas principais respondem?
usuário autorizado entra no Financeiro?
não existem erros HTTP 500 evidentes?
```

## 6. Fluxo oficial

```text
CÓDIGO
  ↓
LOCAL — 127.0.0.1
  ↓
testes automatizados
  ↓
teste funcional/visual local
  ↓
commit
  ↓
revisão de release
  ↓
deploy
  ↓
PRODUÇÃO
  ↓
smoke test mínimo
```

A Demo acompanha a aplicação publicada:

```text
                     ┌──────────── DEMO
                     │
CÓDIGO → LOCAL → DEPLOY
                     │
                     └──────────── PRODUÇÃO
```

## 7. Regra mental simplificada

Se aparece `127.0.0.1`:

```text
LOCAL
→ pode testar
→ dados fictícios
→ pode quebrar
```

Se está no contexto Demo:

```text
DEMO
→ demonstrar
→ não desenvolver
→ comportamento controlado
```

Se é GereIgreja publicado com conta real:

```text
PRODUÇÃO
→ dados reais
→ não experimentar
```

## 8. Ambiente ≠ tenant

Um ponto importante:

```text
ambiente
≠
tenant
```

LOCAL e Produção são ambientes distintos.

Demo, quando hospedada junto da aplicação publicada, é um tenant especial dentro do ambiente publicado.

Portanto:

```text
LOCAL
→ ambiente de desenvolvimento

PRODUÇÃO
→ ambiente publicado

DEMO
→ tenant especial de demonstração no ambiente publicado
```

## 9. Segurança

LOCAL:

```text
usar core.settings_local
usar SQLite local
usar dados fictícios
não conectar banco remoto
não usar credenciais de produção
```

DEMO:

```text
dados controlados
integrações potencialmente neutralizadas
não usar como laboratório
não presumir que teste em Demo valida Produção
```

PRODUÇÃO:

```text
dados reais
sem experimentação
sem comandos destrutivos improvisados
sem migrations manuais fora do processo de release
somente smoke tests controlados após deploy
```

## 10. Relação com permissões

Testes de autorização devem ocorrer prioritariamente no ambiente Local.

Exemplo:

```text
tesoureiro_local
→ validar Tesouraria

admin_ministerio_local
→ validar administração ministerial

secretario_local
→ validar Secretaria

multi_funcao_local
→ validar múltiplos grupos/funções
```

Isso permite reproduzir papéis reais sem depender de `is_superuser`.

## 11. Relação com migrations

A política operacional deve continuar respeitando:

```text
desenvolvimento local normal
→ core.settings_local

testes automatizados
→ core.settings_test

testes reais de migrations
→ core.settings_test_migrations
```

Produção não deve ser utilizada para experimentar migrations.

## 12. Estado desejado

O projeto deve evoluir para possuir:

```text
1. um único SQLite local;
2. um único Ministério fictício local;
3. um conjunto pequeno de usuários funcionais previsíveis;
4. um comando único de preparação do ambiente local;
5. identificação visual explícita de LOCAL;
6. identificação visual explícita de DEMO;
7. nenhuma conexão acidental do desenvolvimento local com Produção;
8. smoke tests mínimos e controlados após deploy.
```

## 13. Responsabilidade documental

Este documento define os três contextos operacionais do GereIgreja.

Documentos específicos podem detalhar:

```text
desenvolvimento local
→ docs/desenvolvimento/

deploy e release
→ docs/deploy/ e docs/release-notes/

operações
→ docs/operacoes/

segurança
→ docs/seguranca/
```

Esses documentos não devem redefinir de forma incompatível os conceitos de LOCAL, DEMO e PRODUÇÃO estabelecidos aqui.

## 14. Resumo normativo

```text
LOCAL
= desenvolver e testar com dados fictícios.

DEMO
= demonstrar a aplicação publicada com controles próprios.

PRODUÇÃO
= operar dados reais sem experimentação.
```

Regra final:

```text
Desenvolver no LOCAL.
Demonstrar na DEMO.
Operar na PRODUÇÃO.
```
