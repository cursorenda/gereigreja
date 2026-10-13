Pasta:
docs/apps/

Arquivo:
02-Secretaria.md

Documento:
APP-02

Família:
Apps — Documentação Funcional

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Setembro de 2026

# 02 — Secretaria

> A Secretaria é o domínio operacional responsável por organizar pessoas, documentos, registros e rotinas administrativas da igreja dentro do contexto ativo e das permissões aplicáveis.

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Atores
5. Contexto de Igreja e Multi-Tenancy
6. Regras de Acesso
7. Capacidades Funcionais
8. Cadastro e Gestão de Pessoas
9. Documentos da Secretaria
10. Certificados
11. Carta de Recomendação
12. Reunião de Membros
13. Dashboard da Secretaria
14. Indicadores, Filtros e Exportações
15. Integrações com Outros Domínios
16. Segurança e Privacidade
17. Auditoria
18. Estados, Regras e Exceções
19. Testes e Qualidade
20. Evolução e Backlog
21. Documentos Relacionados
22. Princípios Finais
23. Status

---

# 1. Objetivo

Este documento consolida a visão funcional canônica do módulo Secretaria do GereIgreja.

Seu objetivo é registrar:

- o que o módulo faz;
- quem pode utilizá-lo;
- quais fluxos pertencem ao domínio;
- quais regras funcionais são relevantes;
- como o contexto da igreja influencia o comportamento;
- quais integrações existem com outros módulos;
- quais documentos técnicos ou históricos detalham implementações específicas.

Este documento não substitui documentação de Backend, Frontend, Segurança, API, Qualidade ou registros históricos de release.

---

# 2. Escopo

A Secretaria concentra funções administrativas ligadas principalmente a:

- pessoas;
- membros;
- visitantes e demais tipos cadastrados;
- documentos;
- certificados;
- carta de recomendação;
- reunião de membros;
- dashboards e indicadores operacionais;
- rotinas administrativas relacionadas ao cadastro e acompanhamento de pessoas.

O escopo funcional poderá evoluir, mas novas capacidades deverão ser incorporadas a este documento quando passarem a fazer parte permanente do domínio.

---

# 3. Papel deste Documento

Este é o documento funcional canônico da Secretaria em `docs/apps/`.

A relação esperada é:

```text
docs/apps/02-Secretaria.md
        ↓
Visão funcional do domínio
        ↓
docs/backend/
docs/frontend/
docs/seguranca/
docs/qualidade/
docs/relatorios/
docs/release-notes/
        ↓
Detalhes técnicos, operacionais e históricos
```

Documentos antigos ou especializados continuam válidos como fontes de detalhe, mas não devem competir com este arquivo pela definição funcional do domínio.

---

# 4. Atores

Os atores identificados na documentação existente incluem:

- Secretário Local;
- Pastor Local;
- Admin Ministério;
- Superusuário;
- usuário comum;
- operadores autorizados da igreja;
- responsáveis técnicos por configuração de modelos e suporte.

Os direitos de cada ator não devem ser inferidos apenas pela interface.

A autorização efetiva deve seguir as regras centralizadas de acesso, o perfil organizacional, o escopo de igrejas e o contexto de igreja aplicável.

---

# 5. Contexto de Igreja e Multi-Tenancy

A Secretaria opera dentro do escopo organizacional autorizado para o usuário. A igreja ativa, quando presente e válida, fornece um contexto concreto para os fluxos que exigem recorte por igreja; ela não é, isoladamente, uma concessão de permissão nem equivale a todas as igrejas do escopo.

Toda consulta, alteração, relatório, exportação ou documento deverá respeitar o escopo organizacional aplicável.

O isolamento multi-tenant é requisito funcional e de segurança.

Em termos funcionais:

```text
User autenticado
   ↓
PerfilUsuario / Ministério
   ↓
Escopo selecionável de igrejas
   ↓
Contexto de igreja, quando aplicável
    ↓
Grupo / papel
    ↓
Política funcional da Secretaria
   ↓
Dados e ações disponíveis
```

`get_igrejas_selecionaveis()` define o escopo organizacional canônico que pode ser selecionado no contexto de igreja. Esse escopo, por si só, não concede permissão funcional à Secretaria. A autorização funcional é decidida por `pode_acessar_secretaria()` e pelas regras das páginas e ações protegidas.

Quando houver igreja ativa, ela deve pertencer ao escopo válido do usuário. A ausência de igreja ativa não significa necessariamente ausência de toda visão da Secretaria: há fluxos consolidados que operam sobre o conjunto de igrejas permitido para o request.

Nenhuma funcionalidade da Secretaria deve assumir que o simples conhecimento de um identificador permite acesso a dados de outra igreja.

O `igreja_id` e o contexto ativo devem ser tratados de forma consistente pelas camadas técnicas responsáveis.

---

# 6. Regras de Acesso

A regra funcional local é centralizada por `pode_acessar_secretaria()` e depende de usuário autenticado, papel/grupo aplicável, perfil organizacional, igreja concreta quando exigida e escopo autorizado.

## Papéis locais: Secretário Local e Pastor Local

Para Secretário Local e Pastor Local, a operação local da Secretaria exige cumulativamente:

- o grupo/papel local correspondente;
- `PerfilUsuario` vinculado a um Ministério;
- a igreja concreta explicitamente presente em `PerfilUsuario.igrejas_permitidas`;
- compatibilidade da igreja com o Ministério do perfil.

O escopo desses papéis é por igreja concreta. Não existe expansão hierárquica automática: uma igreja Regional explicitamente vinculada não concede, por si só, acesso às Congregações subordinadas. Escopo local vazio falha fechado, e a ausência de uma igreja concreta permitida não autoriza a operação local.

## Admin Ministério

Admin Ministério segue política distinta dos papéis locais. Para esse papel, `get_igrejas_selecionaveis()` pode disponibilizar as igrejas do próprio Ministério sem exigir que cada uma esteja em `PerfilUsuario.igrejas_permitidas`; isso não substitui a validação funcional de `pode_acessar_secretaria()`.

| Tipo da igreja concreta selecionável | Política Admin Ministério isolada para operação local da Secretaria |
|---|---|
| Sede | Pode conceder acesso local se a igreja concreta for válida e selecionável. |
| Independente | Pode conceder acesso local se a igreja concreta for válida e selecionável. |
| Regional | Não concede operação local pela política Admin Ministério isolada. |
| Congregação | Não concede operação local pela política Admin Ministério isolada. |

Se o mesmo `User` também acumular Secretário Local ou Pastor Local, a autorização deve ser avaliada também pela política local correspondente, com o respectivo vínculo explícito de igreja. Usuário comum não recebe acesso à Secretaria apenas por possuir contexto de igreja.

Essa regra deve ser aplicada de forma consistente em:

- dashboard;
- telas internas;
- menu;
- proteção das views;
- ações sensíveis;
- relatórios;
- exports.

A interface não deve apresentar acesso que a camada de autorização posteriormente bloqueie, nem ocultar controles que a regra efetivamente permita.

---

# 7. Capacidades Funcionais

A Secretaria possui capacidades com estados funcionais distintos:

| Capacidade | Estado atual | Limite funcional relevante |
|---|---|---|
| Cadastro e gestão de pessoas | `IMPLEMENTED` | Opera sobre pessoas e membros dentro do escopo autorizado. |
| Filtros de pessoas | `IMPLEMENTED` | Devem respeitar a igreja ativa quando aplicável e o escopo permitido. |
| Certificado de apresentação | `IMPLEMENTED` | Usa igreja resolvida dentro do escopo autorizado. |
| Certificado de batismo | `IMPLEMENTED` | Usa igreja resolvida dentro do escopo autorizado. |
| Carta de recomendação | `PARTIAL` | A implementação existe, mas sua disponibilidade é condicionada por feature flag. |
| Relatório para reunião de membros | `IMPLEMENTED` | É relatório; não documenta, sem evidência adicional, um fluxo completo de entidade Reunião. |
| Dashboard, KPIs e gráficos | `IMPLEMENTED` | Opera sobre o escopo efetivo do request. |
| Filtro de período | `IMPLEMENTED` | Aplicado aos indicadores e datasets do dashboard. |
| Exportação CSV do dashboard | `IMPLEMENTED` | Deve refletir o escopo e período efetivos. |
| Exportação Excel | `UNVERIFIED` | Não confirmada como capacidade vigente. |
| Insights automáticos determinísticos | `PLANNED` | Não confirmados como entrega atual. |
| Integração com Escola Bíblica | `IMPLEMENTED` no escopo comprovado | Exige consistência de pessoa, igreja e autorização. |
| Integração com Financeiro | `PARTIAL` | Não concede autorização financeira por derivação. |

Capacidades documentadas apenas como plano ou fase futura não devem ser consideradas entregues sem evidência no sistema atual.

---

# 8. Cadastro e Gestão de Pessoas

A Secretaria possui forte relação com o cadastro de pessoas.

O domínio deve manter consistência entre:

- tipo de pessoa;
- status;
- dados cadastrais;
- vínculos;
- igreja;
- permissões;
- integrações com outros módulos.

Essas camadas não são equivalentes:

- `Pessoa`/`Membro` representam o cadastro de domínio;
- `User` representa a identidade autenticada;
- `PerfilUsuario` associa o usuário ao Ministério e ao escopo organizacional aplicável;
- grupos e papéis participam da autorização funcional;
- `Cargo` e `MembroCargo` representam atribuições de pessoas e podem contribuir para grupos efetivos quando `Cargo.grupo_permissao` estiver configurado;
- `DepartamentoVinculo` registra vínculo histórico de uma pessoa com equipe de departamento.

`DepartamentoVinculo` não concede acesso à Secretaria nem amplia escopo de igreja. `Cargo` e `MembroCargo` também não concedem, isoladamente, autorização local: mesmo quando um cargo ativo contribui para um grupo efetivo, permanecem obrigatórios o `PerfilUsuario`, o tenant, o escopo concreto de igreja e a política funcional da página.

O cadastro deve evitar inconsistências como:

- pessoa vinculada ao tenant incorreto;
- status incompatível com a regra de negócio;
- duplicidade;
- dados obrigatórios ausentes;
- exposição de dados de outra igreja.

Regras detalhadas de cadastro devem permanecer em documentos específicos quando existirem, sendo referenciadas por este documento.

---

# 9. Documentos da Secretaria

A organização funcional evoluiu para concentrar documentos em uma área própria da Secretaria.

A documentação da versão 1.12.0 registra a reorganização do menu com foco em:

```text
Secretaria
└── Documentos
    ├── Certificados
    ├── Carta de Recomendação
    └── Reunião de Membros
```

O objetivo funcional dessa organização é reduzir dispersão e tornar os fluxos documentais mais previsíveis para a operação diária.

---

# 10. Certificados

A Secretaria possui fluxos de emissão de certificados.

A documentação existente registra, entre outros:

- certificado de apresentação;
- certificado de batismo;
- múltiplos modelos visuais;
- prévia antes da impressão;
- estratégia de impressão buscando fidelidade ao layout exibido.

Para certificado de batismo, foram documentados modelos como:

- clássico;
- elegante;
- solene;
- caligráfico.

A escolha visual não deve alterar regras funcionais de elegibilidade, dados utilizados ou escopo da igreja.

---

# 11. Carta de Recomendação

A Carta de Recomendação foi introduzida no domínio de Documentos da Secretaria.

O fluxo documentado inclui:

1. seleção ou resolução do modelo permitido;
2. preenchimento das informações;
3. visualização da prévia;
4. impressão;
5. respeito ao escopo organizacional do modelo.

A documentação de v1.12.0 registrou que a funcionalidade estava protegida por feature flag para usuários comuns durante validação interna.

Portanto, a existência do código ou da rota não deve ser interpretada automaticamente como disponibilidade atual em produção.

## 11.1 Governança de modelos

Os modelos de carta podem ser:

- padrão;
- exclusivos.

Regras documentadas:

- modelo exclusivo deve estar vinculado ao ministério correspondente;
- modelo padrão não deve possuir vínculo exclusivo;
- um ministério não deve receber modelo exclusivo pertencente a outro;
- quando o modelo selecionado não for permitido, a resolução deve evitar exposição cruzada e utilizar comportamento seguro previsto pela implementação.

Essa governança reduz risco de compartilhamento indevido de identidade visual entre organizações.

---

# 12. Relatório para Reunião de Membros

A Secretaria possui relatório para reunião de membros, com aplicação do escopo efetivo de pessoas e igrejas autorizadas.

O relatório é uma capacidade implementada de consulta e impressão. Este documento não o descreve como fluxo completo de uma entidade de negócio denominada Reunião, pois não há evidência suficiente para definir regras, estados ou ciclo de vida dessa entidade.

---

# 13. Dashboard da Secretaria

A Secretaria possui dashboard voltado à leitura operacional do domínio.

A implementação atual inclui, conforme o escopo efetivo:

- KPIs;
- gráficos;
- séries temporais;
- cards de prioridade;
- indicadores de pendências e distribuição;
- recortes por igreja e período.

Materiais históricos também registram propostas de:

- inteligência de pessoas;
- drill-down.

O objetivo funcional do dashboard é apoiar tomada de decisão e operação diária, e não apenas exibir métricas.

---

# 14. Indicadores, Filtros e Exportações

O dashboard atual possui filtro de período com escopo consistente e exportação CSV. Entre os períodos implementados estão:

- 30 dias;
- 90 dias;
- 6 meses;
- 12 meses;
- período personalizado, quando aceito pelo fluxo.

O princípio funcional é que o mesmo período selecionado deve ser aplicado de forma consistente aos KPIs, cards e gráficos relacionados.

As exportações CSV devem refletir exatamente o escopo e os filtros da informação exibida. Exportação Excel permanece não confirmada como capacidade vigente.

Insights automáticos determinísticos permanecem planejados e não devem ser tratados como implementados.

---

# 15. Integrações com Outros Domínios

A Secretaria se relaciona com diversos domínios.

## Configurações

Utilizada para regras e modelos ligados à organização, ministério e configuração de documentos.

## Escola Bíblica

Existem fluxos implementados de vínculo entre alunos e registros de pessoas da Secretaria no escopo comprovado.

Essa integração exige consistência de pessoa, igreja e autorização.

## Financeiro

Permissões e visibilidade financeira não devem ser ampliadas implicitamente pelo acesso à Secretaria.

A integração é parcial: o dashboard pode apresentar indicadores financeiros dentro do escopo aplicável, mas a Secretaria não concede autorização financeira. As permissões do Financeiro permanecem avaliadas pelo seu próprio domínio, inclusive para Secretário Local.

## Departamentos e Ministério

Ministério, igreja, cargos e modelos podem compor o contexto organizacional. `DepartamentoVinculo` não autoriza acesso à Secretaria nem amplia escopo de igreja. `Cargo` e `MembroCargo` podem contribuir para grupos efetivos quando configurados, mas não substituem as exigências de perfil, tenant, escopo concreto e política de acesso.

## Usuários

A identidade autenticada, `PerfilUsuario`, grupos/papéis, escopo de igrejas e contexto concreto aplicável determinam as capacidades disponíveis no módulo. O cadastro de `Pessoa`/`Membro` não se confunde com a identidade `User` nem com a autorização funcional.

---

# 16. Segurança e Privacidade

A Secretaria processa dados pessoais e organizacionais potencialmente confidenciais.

Deve seguir:

- GSF;
- política de Segurança de Dados e Privacidade;
- política de Conformidade e LGPD;
- arquitetura multi-tenant;
- princípios de menor privilégio.

Cuidados obrigatórios incluem:

- escopo organizacional autorizado e igreja ativa válida, quando aplicável;
- prevenção de exposição cruzada;
- controle de acesso;
- proteção de documentos pessoais;
- segurança de exports;
- tratamento adequado de logs;
- minimização de dados.

Dados de pessoas não devem ser utilizados fora da finalidade funcional apenas porque estão disponíveis tecnicamente.

---

# 17. Auditoria

Ações relevantes da Secretaria devem possuir rastreabilidade quando aplicável.

Exemplos:

- alterações cadastrais relevantes;
- emissão de documentos sensíveis;
- exportações;
- mudanças de permissões;
- mudanças de configuração com impacto no domínio;
- ações administrativas de alto impacto.

O nível de auditoria deve ser proporcional ao risco e seguir os padrões centrais do GSF.

---

# 18. Estados, Regras e Exceções

Regras funcionais não devem ser espalhadas entre templates e views sem fonte clara de autoridade.

Exceções relevantes devem ser explícitas.

Exemplos já identificados:

- Secretário Local e Pastor Local exigem vínculo explícito da igreja concreta no `PerfilUsuario`, sem expansão hierárquica;
- Admin Ministério exige igreja concreta selecionável e admite operação local apenas em Sede ou Independente pela sua política isolada;
- modelos exclusivos de carta pertencem ao respectivo ministério;
- feature flags podem impedir disponibilidade mesmo quando a implementação técnica existe.

Ao evoluir o domínio, estados e transições críticas devem ser documentados aqui ou em documento funcional especializado referenciado.

---

# 19. Testes e Qualidade

A Secretaria possui evidências históricas de QA e testes.

A documentação auditada inclui checklist de QA específico da Secretaria e registra cobertura dos principais cenários da regra de acesso por perfil e tipo de igreja.

A validação do módulo deve incluir, conforme aplicável:

- acesso por perfil;
- tipo de igreja;
- isolamento multi-tenant;
- dados do tenant correto;
- documentos;
- certificados;
- carta de recomendação;
- filtros;
- exports;
- feature flags;
- integrações;
- regressões de permissões.

O processo geral de testes pertence ao GQF e à pasta `qualidade/`.

---

# 20. Evolução e Backlog

A documentação histórica deve ser distinguida da funcionalidade atual.

Itens ainda não comprovados como entrega vigente, encontrados em planos de evolução, incluem:

- exportação Excel;
- insights automáticos determinísticos;
- dashboard personalizável;
- cache por perfil;
- centralização de notificações.

Esses itens não devem ser marcados como concluídos sem verificação do código e do comportamento vigente.

A inclusão de novas capacidades permanentes no módulo deve resultar na atualização deste documento canônico.

---

# 21. Documentos Relacionados

## Governança e arquitetura

- `docs/00-Guia-de-Documentacao.md`
- `docs/apps/README.md`
- `docs/arquitetura/02-Arquitetura-da-Plataforma.md`
- `docs/arquitetura/08-Arquitetura-Multi-Tenant.md`

## Segurança

- `docs/frameworks/03-GSF-GereIgreja-Security-Framework.md`
- `docs/seguranca/08-Seguranca-de-Dados-e-Privacidade.md`
- `docs/seguranca/14-Conformidade-e-LGPD.md`

## Secretaria — registros especializados e históricos

- `docs/sistema/ATUALIZACAO_v1.12.0.md` — referência histórica/legada; não define comportamento funcional vigente.
- `docs/release-notes/PLANO_PROXIMA_FASE_SECRETARIA.md`
- `docs/release-notes/CHECKLIST_QA_SECRETARIA_v1.13.2.md`
- `docs/relatorios/Relatorio-Acesso-Secretaria-Tipo-Igreja.md`

## Engenharia

- `docs/backend/README.md`
- `docs/frontend/README.md`
- `docs/qualidade/README.md`

---

# 22. Princípios Finais

A Secretaria deve ser tratada como domínio funcional, não como agrupamento casual de telas.

Suas regras precisam permanecer coerentes entre:

```text
User autenticado
+
PerfilUsuario / Ministério
+
escopo selecionável de igrejas
+
contexto de igreja, quando aplicável
+
grupo / papel e política funcional
+
dados do tenant
```

A documentação técnica deve explicar **como** essas regras são implementadas.

Este documento deve explicar **o que a Secretaria representa e como deve se comportar funcionalmente**.

---

# 23. Status

**Pasta:** `docs/apps/`

**Arquivo:** `02-Secretaria.md`

**Documento:** `APP-02`

**Versão:** `1.0`

**Status:** **OFICIAL**

Este documento consolida a documentação funcional da Secretaria a partir de fontes técnicas, históricas e operacionais existentes.

Funcionalidades descritas em planos ou registros antigos devem ser validadas no sistema atual antes de serem tratadas como capacidade vigente.
