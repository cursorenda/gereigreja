Pasta: docs/seguranca/

Arquivo: 14-Conformidade-e-LGPD.md

Documento: GSF-14

Código: GSF-COMPLIANCE-LGPD

Família: GSF --- GereIgreja Security

Framework: GSF --- GereIgreja Security Framework

Versão: 1.0

Status: Oficial

Responsável: Equipe de Engenharia

Última atualização: Setembro de 2026

# GSF-14 --- Conformidade e LGPD

> Conformidade no GereIgreja deve transformar requisitos de privacidade
> e proteção de dados em controles verificáveis, rastreáveis e
> sustentáveis ao longo do ciclo de vida da informação.

------------------------------------------------------------------------

# Sumário

1.  Objetivo\
2.  Escopo\
3.  Papel deste Documento\
4.  Relação com o GSF\
5.  Princípios de Conformidade\
6.  Limites deste Documento\
7.  Governança de Dados Pessoais\
8.  Inventário e Classificação\
9.  Finalidade, Necessidade e Minimização\
10. Base de Tratamento e Consentimento\
11. Transparência\
12. Direitos do Titular\
13. Acesso aos Dados\
14. Correção de Dados\
15. Portabilidade e Exportação\
16. Revogação e Gestão de Consentimento\
17. Exclusão, Anonimização e Retenção\
18. Situação Atual da Implementação LGPD\
19. Lacuna Crítica: Exclusão/Anonimização\
20. Multi-Tenant e Isolamento por Igreja\
21. Dados Financeiros, Ministeriais e Sensíveis por Contexto\
22. Crianças e Adolescentes\
23. Logs, Auditoria e Evidências\
24. Backups e Retenção\
25. Integrações e Terceiros\
26. Incidentes envolvendo Dados Pessoais\
27. Privacidade por Design\
28. Secure Development Lifecycle\
29. Testes e Evidências de Conformidade\
30. Responsabilidades\
31. Anti-Padrões\
32. Checklist de Conformidade\
33. Pendências e Decisões Abertas\
34. Documentos Relacionados\
35. Princípios Finais\
36. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece a política operacional e normativa de
conformidade e LGPD da plataforma GereIgreja.

Seu objetivo é garantir que o tratamento de dados pessoais seja
realizado de forma:

-   rastreável;
-   proporcional;
-   segura;
-   compatível com a finalidade declarada;
-   tecnicamente controlável;
-   auditável;
-   alinhada ao GereIgreja Security Framework;
-   integrada ao ciclo de vida real dos dados.

O GSF-14 não substitui avaliação jurídica especializada.

Ele transforma os princípios de segurança e privacidade do GereIgreja em
requisitos de engenharia, operação, auditoria e governança.

------------------------------------------------------------------------

# 2. Escopo

Este documento aplica-se a dados pessoais e dados relacionados a pessoas
processados em:

-   Secretaria;
-   Financeiro;
-   Escola Bíblica;
-   Eventos;
-   Comunicação;
-   Patrimônio;
-   Departamentos;
-   Usuários;
-   Configurações;
-   relatórios;
-   dashboards;
-   APIs;
-   integrações;
-   tarefas;
-   automações;
-   logs;
-   backups;
-   exports;
-   imports;
-   ambientes de desenvolvimento;
-   homologação;
-   produção.

Também se aplica a dados processados por:

-   Área de Gestão;
-   Django Admin;
-   Portal Público;
-   serviços internos;
-   integrações de terceiros.

------------------------------------------------------------------------

# 3. Papel deste Documento

O GSF-14 define a camada de conformidade e LGPD da família de Segurança.

Sua posição é:

``` text
GSF — Framework de Segurança
        ↓
GSF-08 — Segurança de Dados e Privacidade
        ↓
GSF-14 — Conformidade e LGPD
        ↓
Controles técnicos, fluxos, evidências e operação
```

O GSF-08 responde principalmente:

``` text
Como os dados devem ser protegidos durante seu ciclo de vida?
```

O GSF-14 responde:

``` text
Quais controles e evidências devem existir para demonstrar tratamento responsável e aderente às obrigações de privacidade?
```

------------------------------------------------------------------------

# 4. Relação com o GSF

O GereIgreja Security Framework determina que a segurança seja tratada
como responsabilidade transversal da plataforma.

A conformidade deverá respeitar os princípios gerais do GSF:

-   menor privilégio;
-   defesa em profundidade;
-   segregação de responsabilidades;
-   proteção por padrão;
-   mínimo acesso necessário;
-   auditoria permanente;
-   melhoria contínua.

A conformidade não deverá ser tratada como camada administrativa
separada da arquitetura.

Ela depende diretamente de:

-   autenticação;
-   autorização;
-   isolamento multi-tenant;
-   segurança de dados;
-   logging;
-   auditoria;
-   backup;
-   resposta a incidentes;
-   desenvolvimento seguro.

------------------------------------------------------------------------

# 5. Princípios de Conformidade

Toda funcionalidade que trate dados pessoais deverá observar:

-   finalidade;
-   necessidade;
-   minimização;
-   transparência;
-   rastreabilidade;
-   segurança;
-   controle de acesso;
-   retenção controlada;
-   exclusão ou anonimização responsável;
-   capacidade de resposta a solicitações do titular;
-   documentação das decisões relevantes.

A mera existência de capacidade técnica para coletar ou armazenar um
dado não constitui justificativa para seu tratamento.

------------------------------------------------------------------------

# 6. Limites deste Documento

Este documento:

-   não constitui parecer jurídico;
-   não define sozinho a base legal específica de cada tratamento;
-   não substitui políticas públicas, Termos de Uso ou Política de
    Privacidade;
-   não presume que uma implementação histórica continue correta;
-   não transforma comentários de código ou documentos antigos em
    requisito jurídico permanente.

Quando houver dúvida sobre interpretação legal, a decisão deverá ser
validada por responsável jurídico ou de compliance apropriado.

A Engenharia deverá documentar a decisão e implementar os controles
aprovados.

------------------------------------------------------------------------

# 7. Governança de Dados Pessoais

Todo tratamento relevante deverá possuir, quando aplicável:

-   finalidade identificada;
-   categoria de dado;
-   módulo responsável;
-   tenant responsável;
-   responsáveis autorizados;
-   origem do dado;
-   destino;
-   integrações;
-   retenção;
-   forma de exclusão ou anonimização;
-   controles de acesso;
-   logs e evidências;
-   dependências externas.

Nenhum módulo deverá assumir que um dado pode ser reutilizado livremente
apenas porque já existe no banco.

------------------------------------------------------------------------

# 8. Inventário e Classificação

A classificação oficial de informação do GSF utiliza:

``` text
Pública
Interna
Restrita
Confidencial
```

Dados pessoais, financeiros e ministeriais devem receber proteção
compatível com sua sensibilidade e contexto.

A análise deverá considerar não apenas campos isolados, mas também a
combinação entre informações.

Exemplo:

``` text
nome
+
vínculo ministerial
+
histórico de participação
=
conjunto potencialmente confidencial
```

O inventário de dados deverá considerar:

-   banco principal;
-   arquivos;
-   cache;
-   logs;
-   exports;
-   imports;
-   APIs;
-   integrações;
-   backups;
-   ambientes não produtivos.

------------------------------------------------------------------------

# 9. Finalidade, Necessidade e Minimização

Antes de coletar ou adicionar um novo campo, deverá ser possível
responder:

``` text
Por que precisamos deste dado?
Quem precisa utilizá-lo?
Por quanto tempo?
Ele precisa ser exportado?
Ele precisa sair do GereIgreja?
```

Se não houver finalidade clara, o dado não deverá ser coletado.

Dados existentes também deverão ser reavaliados quando sua finalidade
deixar de existir.

------------------------------------------------------------------------

# 10. Base de Tratamento e Consentimento

A definição da base de tratamento deverá ser feita de forma explícita e
documentada para os tratamentos que a exigirem.

Consentimento não deverá ser utilizado automaticamente como resposta
para todo tratamento.

Quando o consentimento for utilizado, deverão ser preservadas evidências
suficientes para demonstrar:

-   quem consentiu;
-   quando;
-   qual versão do documento estava vigente;
-   qual ação foi executada;
-   contexto técnico necessário à auditoria.

A implementação histórica do GereIgreja registra consentimento com
versão dos documentos, IP e User Agent.

Essas evidências deverão ser tratadas como registros de auditoria e não
deverão ser alteradas silenciosamente.

------------------------------------------------------------------------

# 11. Transparência

O titular deverá possuir meios adequados para compreender, conforme o
fluxo aplicável:

-   quais dados estão associados à sua conta;
-   quais dados são exibidos pelo sistema;
-   quais consentimentos foram registrados;
-   quais opções de exportação estão disponíveis;
-   quais solicitações podem ser realizadas.

A interface deverá evitar linguagem ambígua ou técnica desnecessária.

------------------------------------------------------------------------

# 12. Direitos do Titular

A implementação e os processos operacionais deverão considerar os
direitos previstos para o titular conforme a legislação aplicável e a
política vigente do GereIgreja.

O sistema já possui evidências históricas de implementação para:

-   consulta dos próprios dados;
-   visualização de consentimentos;
-   exportação;
-   acesso a dados em formato estruturado;
-   acesso em formato legível.

Correção, revogação, exclusão e anonimização deverão ser verificadas no
fluxo atual antes de serem declaradas como integralmente implementadas.

------------------------------------------------------------------------

# 13. Acesso aos Dados

A funcionalidade histórica `/contas/meus-dados/` foi documentada como
ponto de visualização dos dados associados ao usuário.

A implementação descrita inclui categorias como:

-   dados da conta;
-   ministério/organização;
-   dados pessoais;
-   consentimentos;
-   atividades.

Dados sensíveis apresentados em tela deverão utilizar controles
adequados de:

-   autenticação;
-   autorização;
-   mascaramento;
-   contexto de tenant;
-   prevenção contra exposição acidental.

------------------------------------------------------------------------

# 14. Correção de Dados

A correção de dados deverá respeitar:

-   autorização do titular ou operador autorizado;
-   regras do domínio;
-   integridade referencial;
-   rastreabilidade quando relevante;
-   escopo do tenant;
-   prevenção de alteração de dados de outra igreja.

Nem todo dado histórico deverá ser editável diretamente.

Quando a correção exigir preservação de histórico, deverá ser utilizado
mecanismo compatível com o domínio.

------------------------------------------------------------------------

# 15. Portabilidade e Exportação

A documentação histórica registra exportações em:

-   JSON;
-   PDF.

Esses fluxos deverão ser tratados como funcionalidades sensíveis.

Toda exportação deverá considerar:

-   autenticação;
-   autorização;
-   escopo do usuário;
-   escopo do tenant;
-   dados incluídos;
-   logs;
-   prevenção contra vazamento;
-   nome e armazenamento temporário do arquivo;
-   expiração quando aplicável.

Exportar dados aumenta o risco porque os dados deixam os controles
normais da aplicação.

------------------------------------------------------------------------

# 16. Revogação e Gestão de Consentimento

O histórico de consentimentos deverá ser preservado de forma auditável.

Quando houver revogação, o sistema deverá distinguir:

-   revogação do consentimento;
-   encerramento da conta;
-   bloqueio de tratamento;
-   exclusão;
-   anonimização.

Esses eventos não deverão ser representados como se fossem equivalentes.

Mudanças futuras na modelagem deverão preservar o histórico mínimo
necessário à auditoria e às obrigações aplicáveis.

------------------------------------------------------------------------

# 17. Exclusão, Anonimização e Retenção

Exclusão e anonimização deverão ser tratadas como processos distintos.

Antes de qualquer implementação, deverão ser analisados:

-   ForeignKeys;
-   `PROTECT`;
-   `CASCADE`;
-   registros financeiros;
-   históricos;
-   logs;
-   auditoria;
-   backups;
-   ownership administrativo;
-   dependências entre tenants e usuários;
-   obrigações de retenção.

A existência de integridade referencial não justifica manter dados
pessoais indefinidamente.

Da mesma forma, a exclusão física indiscriminada não deverá destruir
registros cuja preservação seja necessária.

A solução deverá ser definida por categoria de dado e finalidade.

------------------------------------------------------------------------

# 18. Situação Atual da Implementação LGPD

A documentação histórica `deploy/LGPD_IMPLEMENTACAO.md` registra como
concluídas as seguintes etapas:

1.  consentimento no registro;
2.  visualização de dados pessoais;
3.  exportação JSON;
4.  exportação PDF;
5.  histórico detalhado de consentimentos.

Esses registros constituem **evidência histórica de implementação**.

Antes de considerar cada item como controle atual de produção, deverá
ser feita validação contra:

-   código vigente;
-   URLs vigentes;
-   modelos vigentes;
-   permissões;
-   templates;
-   testes;
-   comportamento real em produção.

Este documento não presume automaticamente que uma implementação de
março de 2026 continua intacta.

------------------------------------------------------------------------

# 19. Lacuna Crítica: Exclusão/Anonimização

A documentação histórica registra como pendente a fase de
exclusão/anonimização de conta.

Foi identificado conflito com integridade referencial envolvendo
`administrador_principal` protegido por `on_delete=PROTECT`.

Esse problema deverá ser tratado como decisão arquitetural, funcional e
de compliance.

As opções históricas consideradas incluíram:

-   anonimização;
-   transferência de propriedade seguida de exclusão;
-   abordagem híbrida.

Nenhuma dessas opções deverá ser adotada automaticamente apenas porque
apareceu como recomendação em documento antigo.

A decisão atual deverá considerar:

-   arquitetura vigente;
-   usuários administradores;
-   existência de substituto;
-   dados financeiros;
-   históricos ministeriais;
-   logs;
-   backups;
-   revogação de credenciais;
-   auditoria;
-   experiência do titular;
-   validação jurídica aplicável.

Se a decisão alterar significativamente a arquitetura de ownership,
deverá ser registrada em ADR.

------------------------------------------------------------------------

# 20. Multi-Tenant e Isolamento por Igreja

Toda operação relacionada a dados pessoais deverá respeitar o tenant
ativo e o `igreja_id` aplicável.

Nenhum fluxo LGPD poderá:

-   consultar dados de outra igreja;
-   exportar dados de outro tenant;
-   corrigir dados fora do escopo;
-   anonimizar pessoa pertencente a contexto diferente sem autorização;
-   usar parâmetros fornecidos pelo cliente como única garantia de
    isolamento.

A proteção multi-tenant deverá existir em:

-   queries;
-   selectors;
-   services;
-   views;
-   exports;
-   relatórios;
-   APIs;
-   tarefas assíncronas;
-   integrações.

------------------------------------------------------------------------

# 21. Dados Financeiros, Ministeriais e Sensíveis por Contexto

O GereIgreja trata dados cujo impacto depende do contexto.

Deverão receber atenção reforçada:

-   movimentações financeiras;
-   doações e receitas;
-   despesas;
-   vínculos ministeriais;
-   cargos;
-   histórico de participação;
-   dados cadastrais;
-   documentos pessoais;
-   informações combinadas em relatórios.

A necessidade de retenção e exclusão poderá variar entre essas
categorias.

Uma política única de "apagar tudo" não deverá ser aplicada
indiscriminadamente.

------------------------------------------------------------------------

# 22. Crianças e Adolescentes

Funcionalidades como Escola Bíblica, ministérios, eventos e cadastros
podem envolver dados de crianças e adolescentes.

Esses dados exigem avaliação específica de:

-   necessidade;
-   minimização;
-   acesso;
-   exposição;
-   exportação;
-   retenção;
-   responsáveis autorizados;
-   legislação aplicável.

A mera existência de vínculo com responsável ou igreja não elimina a
necessidade de controles próprios.

------------------------------------------------------------------------

# 23. Logs, Auditoria e Evidências

Eventos relevantes de privacidade e LGPD deverão ser auditáveis.

Podem incluir:

-   aceite de termos;
-   alteração de consentimento;
-   exportação;
-   correção relevante;
-   solicitação de exclusão;
-   anonimização;
-   revogação;
-   alteração de permissões;
-   ação administrativa sensível.

Logs não deverão conter dados pessoais além do necessário.

A auditoria deverá preservar rastreabilidade sem transformar logs em
nova fonte desnecessária de exposição.

------------------------------------------------------------------------

# 24. Backups e Retenção

A política de retenção deverá considerar cópias de segurança.

Excluir um registro do banco primário não significa que o dado
desapareceu imediatamente de backups.

A estratégia deverá definir:

-   período de retenção;
-   expiração;
-   restauração;
-   reprocessamento após restore;
-   tratamento de dados excluídos ou anonimizados;
-   controle de acesso aos backups.

Backups não deverão ser usados para restaurar silenciosamente dados que
já haviam sido objeto de exclusão ou anonimização sem tratamento
correspondente.

------------------------------------------------------------------------

# 25. Integrações e Terceiros

Integrações que recebam dados pessoais deverão ser identificadas e
avaliadas.

Antes de compartilhar dados, verificar:

-   finalidade;
-   dados mínimos necessários;
-   autenticação;
-   criptografia;
-   logs;
-   retenção;
-   provedor;
-   possibilidade de revogação;
-   impacto de incidente;
-   requisitos contratuais e de compliance aplicáveis.

A documentação técnica da integração deverá apontar para esta política
quando houver tratamento de dados pessoais.

------------------------------------------------------------------------

# 26. Incidentes envolvendo Dados Pessoais

Incidentes com potencial impacto em dados pessoais deverão seguir o
processo formal de gestão de incidentes do GSF.

Fluxo mínimo:

``` text
Detecção
    ↓
Classificação
    ↓
Contenção
    ↓
Preservação de evidências
    ↓
Análise de impacto
    ↓
Correção
    ↓
Recuperação
    ↓
Avaliação de comunicação/notificação
    ↓
Lições aprendidas
```

A necessidade de comunicação externa ou notificação deverá ser avaliada
conforme o caso e a legislação aplicável.

A Engenharia não deverá assumir automaticamente que todo incidente exige
a mesma resposta regulatória.

------------------------------------------------------------------------

# 27. Privacidade por Design

Toda nova funcionalidade deverá considerar privacidade ainda na fase de
desenho.

Perguntas obrigatórias:

``` text
O dado é necessário?
A finalidade está clara?
O tenant está corretamente definido?
Quem poderá visualizar?
Quem poderá alterar?
Será exportado?
Será enviado a terceiro?
Quanto tempo ficará armazenado?
Como será excluído ou anonimizado?
Como será auditado?
```

Se essas respostas não existirem, a funcionalidade não está pronta do
ponto de vista de privacidade.

------------------------------------------------------------------------

# 28. Secure Development Lifecycle

Mudanças que afetem dados pessoais deverão ser consideradas no processo
de desenvolvimento seguro.

Revisões deverão avaliar:

-   novos campos;
-   novos relacionamentos;
-   novas integrações;
-   alterações de permissões;
-   exports;
-   relatórios;
-   caches;
-   logs;
-   tarefas;
-   endpoints;
-   comportamento multi-tenant;
-   retenção e exclusão.

Mudanças relevantes deverão atualizar documentação, testes e evidências.

------------------------------------------------------------------------

# 29. Testes e Evidências de Conformidade

Controles LGPD não deverão ser considerados confiáveis sem validação.

Testes recomendados:

-   usuário acessa apenas os próprios dados permitidos;
-   tenant A não acessa dados do tenant B;
-   exportação respeita escopo;
-   dados sensíveis são mascarados quando aplicável;
-   permissões administrativas são verificadas;
-   histórico de consentimentos é preservado;
-   logs não expõem conteúdo excessivo;
-   fluxos de exclusão/anonimização não quebram integridade;
-   restore de backup não reintroduz dados sem tratamento;
-   integrações recebem somente os dados previstos.

Evidências podem incluir:

-   testes automatizados;
-   testes manuais;
-   logs controlados;
-   screenshots de homologação;
-   relatórios de QA;
-   ADRs;
-   registros de incidentes;
-   checklists de release.

------------------------------------------------------------------------

# 30. Responsabilidades

## Engenharia

Responsável por:

-   implementar controles;
-   manter isolamento multi-tenant;
-   garantir autorização;
-   manter testes;
-   atualizar documentação técnica.

## Segurança

Responsável por:

-   definir controles;
-   revisar riscos;
-   acompanhar incidentes;
-   avaliar evidências.

## Operações

Responsável por:

-   execução de procedimentos;
-   backups;
-   restauração;
-   resposta operacional;
-   preservação de evidências.

## Produto / Responsáveis Funcionais

Responsáveis por:

-   declarar finalidade;
-   evitar coleta desnecessária;
-   revisar fluxos;
-   apoiar decisões de retenção.

## Responsável Jurídico / Compliance

Quando aplicável, responsável por validar interpretações legais, bases
de tratamento, comunicação regulatória e decisões de alto impacto.

------------------------------------------------------------------------

# 31. Anti-Padrões

São anti-padrões:

``` text
"Tem consentimento, então podemos fazer qualquer coisa."
```

``` text
"O dado está no banco, então qualquer módulo pode usar."
```

``` text
"Excluir usuário significa apagar tudo em cascata."
```

``` text
"Anonimização sempre resolve qualquer obrigação."
```

``` text
"Backup não conta como retenção."
```

``` text
"Log pode guardar tudo porque é auditoria."
```

``` text
"Se a implementação existia em 2026, ainda está conforme."
```

``` text
"Tenant foi validado no frontend, então está seguro."
```

------------------------------------------------------------------------

# 32. Checklist de Conformidade

Antes de publicar ou alterar funcionalidade que trate dados pessoais:

-   [ ] finalidade definida;
-   [ ] dados mínimos identificados;
-   [ ] classificação revisada;
-   [ ] tenant/`igreja_id` protegido;
-   [ ] autenticação revisada;
-   [ ] autorização revisada;
-   [ ] base de tratamento identificada quando necessária;
-   [ ] consentimento tratado corretamente quando aplicável;
-   [ ] transparência revisada;
-   [ ] exportação avaliada;
-   [ ] retenção definida;
-   [ ] exclusão/anonimização considerada;
-   [ ] logs revisados;
-   [ ] backups considerados;
-   [ ] terceiros identificados;
-   [ ] testes executados;
-   [ ] evidências preservadas;
-   [ ] documentação atualizada;
-   [ ] análise jurídica solicitada quando necessária.

------------------------------------------------------------------------

# 33. Pendências e Decisões Abertas

Pendências identificadas durante a restauração deste documento:

1.  validar no código atual as fases registradas em
    `LGPD_IMPLEMENTACAO.md`;
2.  definir a solução atual para exclusão/anonimização de conta;
3.  validar o fluxo de transferência de ownership quando houver
    administrador principal;
4.  definir política formal de retenção por categoria de dado;
5.  verificar comportamento de backups após exclusão/anonimização;
6.  mapear integrações que recebem dados pessoais;
7.  revisar dados de crianças e adolescentes nos módulos aplicáveis;
8.  validar testes automatizados dos fluxos de privacidade;
9.  revisar a localização de `deploy/LGPD_IMPLEMENTACAO.md`, que deve
    ser tratado como registro histórico de implementação e não como
    política normativa de deploy.

Essas pendências não justificam a criação automática de novos documentos
GSF.

Quando uma decisão possuir impacto arquitetural duradouro, utilizar ADR.

------------------------------------------------------------------------

# 34. Documentos Relacionados

-   `docs/frameworks/03-GSF-GereIgreja-Security-Framework.md`
-   `docs/seguranca/08-Seguranca-de-Dados-e-Privacidade.md`
-   `docs/seguranca/13-Gestao-de-Incidentes-de-Seguranca.md`
-   `docs/seguranca/15-Secure-Development-Lifecycle.md`
-   `docs/seguranca/16-Governanca-de-Seguranca.md`
-   `docs/seguranca/17-Mapa-e-Indice-da-Seguranca.md`
-   `docs/deploy/LGPD_IMPLEMENTACAO.md`
-   `docs/arquitetura/07-Arquitetura-da-Seguranca.md`
-   `docs/frameworks/02-GAF-GereIgreja-Authentication-Framework.md`
-   `docs/frameworks/04-GQF-GereIgreja-Quality-Framework.md`
-   `docs/frameworks/06-GOC-GereIgreja-Operations-Center.md`

------------------------------------------------------------------------

# 35. Princípios Finais

Conformidade não deverá ser tratada como checklist jurídico isolado.

No GereIgreja, conformidade depende de arquitetura, segurança,
privacidade, multi-tenancy, autorização, logging, retenção, backup,
incidentes e operação.

O objetivo não é apenas declarar aderência.

O objetivo é possuir controles verificáveis e decisões rastreáveis.

------------------------------------------------------------------------

# 36. Status do Documento

**Pasta:** `docs/seguranca/`

**Arquivo:** `14-Conformidade-e-LGPD.md`

**Documento:** `GSF-14`

**Versão:** `1.0`

**Status:** **OFICIAL --- RESTAURADO**

Este documento restaura o item GSF-14, que existia nominalmente na
família de Segurança, mas estava sem conteúdo.

Sua restauração foi construída a partir do GSF oficial, do GSF-08 de
Segurança de Dados e Privacidade, do mapa GSF-17 e do registro histórico
`LGPD_IMPLEMENTACAO.md`.

As alegações de implementação histórica deverão ser revalidadas contra o
código vigente antes de serem tratadas como evidência atual de produção.
