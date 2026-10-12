Pasta:
docs/apps/

Arquivo:
05-Departamentos.md

Documento:
APP-05

Seção:
Apps

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Agosto de 2026

# 05 - Departamentos

## 1. Objetivo

Este documento define o domínio de departamentos do GereIgreja e o contrato da primeira versão de equipes e responsáveis locais.

## 2. Estrutura oficial

```text
Ministério
└── DepartamentoMinisterial (definição estrutural)
    └── Departamento (instância operacional da igreja)
        └── DepartamentoVinculo (membro/equipe local e função)
```

- `DepartamentoMinisterial` é criado e mantido no Ministério.
- `Departamento` representa o provisionamento operacional em uma igreja.
- A igreja ativa ou desativa definições ministeriais; não cria novas definições estruturais localmente nesta fase.
- `DepartamentoVinculo` será a fonte de verdade para afirmar que uma pessoa pertence à equipe de um departamento local.

## 3. Vínculo departamental

- `data_fim IS NULL` significa vínculo ativo.
- Só poderá existir um vínculo ativo por `(departamento, membro)`.
- Um vínculo encerrado nunca será reaberto nem sobrescrito.
- Retorno ao departamento ou troca de cargo cria novo vínculo, preservando o histórico.
- Nesta versão, cada vínculo ativo possui no máximo um cargo opcional. Múltiplos cargos exigem novo ADR.

## 4. Cargo e autorização

`Cargo` será reutilizado apenas como classificação organizacional da função exercida no departamento.

O `DepartamentoVinculo`:

- não altera nem cria `MembroCargo`;
- não dispara sincronização de grupos;
- não cria grupo Django;
- não concede Financeiro, Agenda, Eventos, Comunicação ou qualquer módulo;
- não transforma capacidades do departamento em permissões.

Mesmo que o `Cargo` escolhido possua `grupo_permissao`, essa associação não será aplicada pelo vínculo departamental. Somente o fluxo oficial de `MembroCargo` poderá sincronizar grupos.

## 5. Escopo e autorização

Pastor Local e Secretário Local poderão administrar equipes somente em igrejas explicitamente permitidas e na igreja em contexto. O escopo local não poderá ser ampliado por hierarquia ou por igrejas subordinadas.

Admin Ministério/Pastor Presidente não recebe operação local automática em todas as igrejas do Ministério. Na Sede e na Igreja Independente, pode acessar módulos operacionais locais quando a política real e contextual de cada módulo permitir; esse acesso não decorre de um poder irrestrito sobre equipes ou dados. Em Regionais e Congregações, o papel ministerial concede supervisão pela área ou visão ministerial, e não operação local. A operação local nesses contextos exige papel local explícito na igreja. Quando o mesmo usuário acumula papel ministerial e papel local explícito, as permissões são aditivas, mas cada papel preserva seu próprio escopo.

Capacidade declarada no departamento não concede autorização. As políticas canônicas de cada módulo continuam sendo a fonte de autorização.

### Política do Hub Operacional do Departamento

Um `DepartamentoVinculo` ativo permite exclusivamente a visualização do Hub pessoal; vínculo, Cargo e capability não concedem permissão operacional. Atalhos dependem da política contextual real de cada módulo e, para atalhos genéricos da igreja, exigem correspondência com a igreja ativa. Admin Ministério/Pastor Presidente sem papel local explícito não recebe atalhos locais em Regional ou Congregação; na Sede e na Igreja Independente, os atalhos permanecem sujeitos à política contextual do módulo. A dupla atuação com papel local explícito pode autorizar atalhos locais em Regional ou Congregação, dentro do escopo desse papel.

No Financeiro, o acesso do Admin Ministério/Pastor Presidente em Sede ou Igreja Independente depende da política financeira contextual; esse acesso não o transforma automaticamente em Tesoureiro. Regional e Congregação não recebem operação financeira local apenas pelo papel Admin Ministério.

## 6. Segurança multi-tenant e IDOR

IDs recebidos por URL, query string ou POST nunca definem o escopo. O backend deverá:

1. resolver as igrejas explicitamente permitidas ao usuário;
2. restringir pela igreja ativa válida, quando presente;
3. buscar o departamento dentro desse escopo;
4. buscar o membro na mesma igreja do departamento;
5. validar o cargo permitido para a operação;
6. executar criação ou encerramento de forma transacional.

Departamento e membro de igrejas diferentes não poderão ser vinculados, mesmo dentro do mesmo Ministério. Objetos fora do escopo deverão resultar em 404 ou 403 apropriado, sem alteração de dados.

## 7. Histórico e auditoria

A remoção funcional será realizada pelo encerramento do vínculo, preservando o registro histórico. Criação, encerramento e troca de cargo deverão registrar usuário responsável e datas aplicáveis. Tentativas negadas relevantes deverão seguir o mecanismo oficial de auditoria de acesso.

## 8. Fora do escopo desta versão

- múltiplos cargos simultâneos;
- grupos Django ou novos cargos padrão;
- mudanças em `MembroCargo`;
- permissões de Financeiro ou outros módulos;
- equipe ministerial geral;
- portal do líder, notificações, escalas, tarefas ou almoxarifado.

## 9. Documentos relacionados

- `docs/adr/01-DepartamentoVinculo-Historico-e-Cargo.md`
- `docs/sistema/CARGOS_SISTEMA.md`
- `docs/sistema/GUIA_ESCOPO_VIEWS.md`
- `docs/arquitetura/08-Arquitetura-Multi-Tenant.md`
- `docs/seguranca/05-Seguranca-Multi-Tenant.md`

## 10. Dívida técnica de performance

A tela `Meus Departamentos` deve reutilizar, por request, os escopos e as decisões de autorização já calculados, sem cache global ou persistente. A consulta funcional de vínculos e capacidades não deve crescer por departamento.

A auditoria de agosto de 2026 identificou custo transversal no middleware, menu, context processors, auditoria, plano/beta, onboarding e seletor global. Essas camadas permanecem fora do escopo da otimização local. A meta inicial para uma futura otimização coordenada da requisição completa é de 28 a 35 queries, preservando integralmente autorização e isolamento multi-tenant.

## 11. Hub Operacional do Departamento V1

O Hub é uma tela pessoal, somente leitura, acessível exclusivamente por um `DepartamentoVinculo` ativo da Pessoa autenticada. O identificador do departamento na URL é apenas candidato: Departamento, Igreja e Ministério são derivados do vínculo encontrado no backend. Um vínculo encerrado ou pertencente a outra Pessoa resulta em resposta não reveladora de recurso.

- capacidades são informações organizacionais e não concedem acesso;
- Cargo e `DepartamentoVinculo` não concedem grupos, módulos ou permissões;
- somente o Financeiro possui contexto departamental real nesta versão, por meio de `DepartamentoFinanceiro` resolvido a partir do Departamento autorizado;
- Pessoas, Agenda, Eventos e Comunicação são apenas atalhos da igreja e exigem política real, escopo oficial e correspondência com a igreja ativa já validada;
- o Hub não troca a igreja ativa implicitamente nem aceita query string para alterar contexto;
- quando a igreja do departamento for selecionável pela política canônica e
  diferir da igreja ativa, o Hub poderá oferecer troca explícita por formulário
  POST para o endpoint canônico, com retorno interno seguro ao próprio Hub;
- `DepartamentoVinculo`, Cargo e capacidades não autorizam essa troca: a igreja
  deve pertencer a `core.utils.get_igrejas_selecionaveis()` e o endpoint faz nova
  validação antes de alterar a sessão;
- Escalas, Tarefas e Almoxarifado permanecem somente como capacidades informativas;
- não há equipe, métricas, próximos eventos ou operações de escrita nesta versão.

## 12. Princípios finais

O vínculo departamental representa organização e histórico local. Ele não representa autorização. Toda operação deverá combinar papel autorizado, escopo explícito de igreja e validação do objeto no backend.
