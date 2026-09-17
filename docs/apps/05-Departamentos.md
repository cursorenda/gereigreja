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

Admin Ministério terá, por padrão, somente visão consolidada e somente leitura das equipes locais. Ser Admin Ministério não autoriza operação local. Qualquer operação futura exigirá contexto/autorização explícita e nova decisão documentada.

Capacidade declarada no departamento não concede autorização. As políticas canônicas de cada módulo continuam sendo a fonte de autorização.

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

## 10. Princípios finais

O vínculo departamental representa organização e histórico local. Ele não representa autorização. Toda operação deverá combinar papel autorizado, escopo explícito de igreja e validação do objeto no backend.
