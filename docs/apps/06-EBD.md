Pasta:
docs/apps/

Arquivo:
06-EBD.md

Documento:
APP-06

Família:
Apps — Documentação Funcional

Versão:
1.0

Status:
Em consolidação

Responsável:
Equipe de Engenharia

Última atualização:
Setembro de 2026

# 06 — Escola Bíblica Dominical (EBD)

> A EBD é o domínio responsável pela organização do ensino bíblico por igreja, período, classes, turmas, alunos, professores, lições, chamada, avaliações, ofertas e relatórios. Esta documentação funcional está em consolidação e deve ser lida junto das políticas de acesso, do escopo de igreja e da implementação vigente.

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Atores
5. Configuração da EBD
6. Church-first e Fallback Ministerial
7. Ano Letivo e Períodos
8. Classes e Turmas
9. Professores e Colaboradores
10. Alunos e Matrículas
11. Lições e Cronograma
12. Chamada e Frequência
13. Avaliações
14. Ofertas
15. Dashboard e Resumo Semanal
16. Relatórios
17. Preparação do Ano Letivo
18. Cópia e Continuidade entre Anos
19. Permissões e Escopo
20. Multi-Tenancy
21. Integridade e Idempotência
22. Auditoria
23. Segurança e Privacidade
24. Testes e Qualidade
25. Operação por Perfil
26. Riscos e Pontos de Atenção
27. Evolução e Material Histórico
28. Documentos Relacionados
29. Princípios Finais
30. Status

---

# 1. Objetivo

Este documento consolida a visão funcional em consolidação do módulo Escola Bíblica Dominical do GereIgreja.

Seu objetivo é registrar:

- o que a EBD faz;
- quem opera o módulo;
- como ano, período, igreja e turma definem o escopo;
- quais regras funcionais governam lições, frequência, avaliações e ofertas;
- como a configuração local da igreja é resolvida;
- como a preparação anual deve preservar integridade e isolamento;
- quais materiais antigos são apenas históricos ou operacionais.

Este documento não substitui documentação técnica de Models, Services, Views, permissões, performance ou runbooks.

---

# 2. Escopo

A EBD cobre, conforme a documentação auditada:

- configuração local da EBD;
- período e dia da semana;
- horário;
- ano letivo;
- períodos físicos;
- classes;
- turmas;
- professores;
- colaboradores;
- alunos;
- matrículas;
- lições;
- chamada;
- frequência;
- avaliações;
- ofertas por turma;
- dashboard;
- resumo semanal;
- relatórios;
- preparação do próximo ano;
- cópia de turmas e vínculos;
- automação de calendário;
- auditoria de operações relevantes.

---

# 3. Papel deste Documento

Este é o documento funcional da EBD em consolidação em `docs/apps/`.

A relação esperada é:

```text
docs/apps/06-EBD.md
        ↓
Visão funcional do domínio
        ↓
docs/sistema/
docs/usuario/
docs/seguranca/
docs/qualidade/
docs/release-notes/
        ↓
Detalhes técnicos, operacionais e históricos
```

Documentos de auditoria antiga não devem prevalecer sobre políticas vigentes, documentação canônica especializada ou sobre a implementação atual.

---

# 4. Atores

Os perfis encontrados na documentação incluem:

- Secretaria EBD;
- Superintendente EBD;
- Professor EBD;
- colaboradores vinculados às turmas;
- liderança;
- superusuário;
- usuários com acesso permitido ao módulo.

O acesso ao módulo e às suas jornadas combina, conforme a operação:

- autenticação;
- habilitação do módulo EBD;
- grupos centrais e política da página;
- escopo de igrejas permitido;
- vínculo operacional com a turma, quando o fluxo for de professor;
- permissões vigentes para a operação concreta.

A igreja ativa participa da definição do escopo quando estiver autorizada, mas não é fonte autônoma de permissão.

A interface não deve ser usada como única barreira de segurança.

---

# 5. Configuração da EBD

A EBD utiliza três parâmetros funcionais principais:

- tipo de período;
- dia da semana;
- horário.

Valores documentados para período incluem:

- trimestre;
- quadrimestre;
- semestre;
- ano.

Essas configurações orientam:

- calendário;
- geração de lições;
- chamada;
- frequência;
- agenda;
- relatórios;
- preparação anual.

---

# 6. Church-first e Fallback Ministerial

A configuração atual documentada segue estratégia **church-first**.

A resolução funcional atual ocorre pelo objeto/contexto de configuração, e não por fallback campo a campo:

```text
Igreja em escopo
   ↓
Existe qualquer override EBD local?
   ├── Sim → usar configuração da igreja
   └── Não → usar configuração ministerial
```

Campos locais documentados na igreja:

- `ebd_periodo`;
- `ebd_dia_semana`;
- `ebd_horario`.

A existência de qualquer um dos campos locais faz a resolução usar a configuração da igreja como um todo para a EBD. Quando não há override local, aplica-se a configuração ministerial. A estratégia permite migração gradual sem quebra do comportamento legado.

O módulo deve deixar claro qual configuração está sendo utilizada quando isso for relevante para operação ou suporte.

---

# 7. Ano Letivo e Períodos

A EBD trabalha com `AnoLetivo` e `PeriodoEBD`.

A documentação de governança define que operações devem ocorrer dentro de período válido.

O período oficial serve como referência para:

- lições;
- chamada;
- frequência;
- ofertas;
- relatórios;
- gráficos.

O módulo possui automação para garantir períodos do ano atual e do próximo ano conforme a configuração vigente.

---

# 8. Classes e Turmas

Classes representam agrupamentos pedagógicos.

Turmas representam a execução concreta de uma classe em determinado contexto de igreja e ano letivo.

A documentação operacional exemplifica classes como:

- Crianças;
- Jovens;
- Homens;
- Mulheres.

Regras de integridade documentadas:

- turma de destino em cópia anual é identificada por nome + igreja + ano letivo;
- classes e turmas copiadas permanecem na mesma igreja;
- exclusão de turma com histórico deve ser tratada com cautela;
- professores e colaboradores devem permanecer vinculados corretamente.

---

# 9. Professores e Colaboradores

Professores operacionalmente reconhecidos podem operar jornadas compatíveis com suas próprias turmas.

No comportamento atual, o reconhecimento operacional do professor depende da combinação de:

- `request.user.membro_secretaria`;
- membro vinculado à turma;
- `MembroCargo` ativo;
- cargo marcado como EBD;
- nome do cargo contendo "professor";
- módulo EBD habilitado;
- turma dentro do escopo permitido.

O grupo `Professor EBD` também pode participar da política da página de professor. Ser listado como professor de uma turma, isoladamente, não deve ser documentado como autorização automática.

Quando essas condições e a política da jornada são atendidas, o professor pode:

- acessar sua turma;
- realizar a chamada;
- registrar observações;
- informar situações que dependam da Secretaria;
- não alterar chamadas de outra turma.

Mudança de professor deve atualizar os vínculos operacionais e de cargo antes da próxima operação para evitar acesso indevido ou ausência de acesso.

Na cópia seletiva, colaboradores associados às turmas podem ser copiados quando o fluxo incluir membros. A cópia anual completa não deve ser interpretada como replicação automática de professores ou colaboradores.

---

# 10. Alunos e Matrículas

Alunos devem permanecer vinculados ao contexto correto de turma, igreja e ano.

A documentação atual estabelece que:

- aluno avaliado deve pertencer à mesma turma da lição;
- matrícula precisa estar vigente na data da lição;
- consultas históricas devem respeitar a vigência real da matrícula;
- cópias anuais não devem duplicar o mesmo aluno na turma de destino.

A integração com Secretaria deve preservar identidade de pessoa e evitar cadastros incoerentes.

---

# 11. Lições e Cronograma

Lições devem obedecer ao período válido da turma.

Regras documentadas:

- a data da lição precisa cair dentro de `PeriodoEBD` válido;
- deve existir unicidade por turma + data;
- cronograma deve seguir dia da semana configurado;
- geração deve ser idempotente.

O módulo possui auto-sync que gera lições para o período vigente ou próximo quando necessário.

Pontos de entrada documentados para disparar a automação incluem:

- Dashboard EBD;
- Chamada por turma;
- Lista de turmas.

---

# 12. Chamada e Frequência

A chamada é um dos principais fluxos operacionais.

A documentação atual estabelece:

- frequência não permite data futura;
- a data deve estar em período válido;
- a data deve coincidir com o dia configurado para EBD;
- o POST da chamada deve aceitar somente alunos ativos da turma acessada;
- identificadores manipulados de alunos de outra turma devem ser rejeitados;
- reenvios legítimos da mesma chamada não devem criar registros duplicados para o mesmo contexto;
- proteção contra concorrência deve ser preservada.

A rotina semanal da EBD depende da chamada estar concluída corretamente.

---

# 13. Avaliações

A documentação atual registra regras de integridade para avaliações:

- aluno avaliado pertence à turma da lição;
- matrícula deve estar vigente na data da lição;
- validação ocorre tanto na interface quanto no domínio técnico.

Essas regras são especialmente importantes para consultas históricas.

---

# 14. Ofertas

A EBD possui registro de ofertas por turma.

Regras documentadas:

- oferta vinculada a turma deve ocorrer dentro de período válido;
- a classe da oferta deve corresponder à classe da turma;
- ofertas podem fazer parte da rotina semanal e de relatórios consolidados;
- acesso a dados de oferta deve respeitar o perfil autorizado.

Como existe natureza financeira no dado, não se deve presumir que todo perfil da EBD pode visualizar todas as informações financeiras.

---

# 15. Dashboard e Resumo Semanal

O Dashboard é o ponto de acompanhamento operacional da EBD.

A documentação operacional registra uso de:

- filtros por igreja;
- ano;
- período;
- fila operacional;
- Resumo Semanal da EBD;
- frequência;
- turmas pendentes;
- ofertas;
- progresso das aulas.

Os totais devem considerar apenas turmas previstas no recorte selecionado.

Antes de interpretar qualquer indicador, o usuário deve confirmar igreja, ano e período.

---

# 16. Relatórios

A EBD possui relatórios de:

- frequência;
- operação diária;
- alunos;
- turmas;
- pendências;
- ofertas;
- progresso.

O guia operacional registra um “Relatório instantâneo” usado para identificar turmas sem chamada, ofertas ou informações pendentes.

Relatórios devem respeitar:

- igreja;
- ano;
- período;
- data;
- turmas do usuário;
- permissões.

---

# 17. Preparação do Ano Letivo

A preparação anual é um fluxo formal do módulo.

A documentação atual orienta:

1. selecionar classes que continuarão;
2. selecionar turmas;
3. selecionar alunos;
4. no fluxo seletivo, decidir se os colaboradores vinculados serão copiados;
5. criar períodos necessários;
6. gerar lições para o novo ano.

A cópia seletiva pode incluir membros/colaboradores das turmas selecionadas. A cópia completa atualmente cria ou reutiliza classes, turmas e alunos ativos, sem ser documentada como replicação automática de membros ou professores.

O ano sugerido deve ser calculado dinamicamente, não fixado manualmente em regra permanente.

---

# 18. Cópia e Continuidade entre Anos

Os fluxos seletivo e completo possuem comportamentos próprios, mas ambos devem preservar, conforme os elementos envolvidos:

- mesma igreja;
- integridade de classes e turmas;
- ausência de alunos duplicados;
- vínculos selecionados;
- histórico;
- rastreabilidade.

## Fluxo seletivo

Pode copiar somente classes, turmas e alunos selecionados e pode incluir membros, professores ou colaboradores quando a opção correspondente fizer parte desse fluxo.

## Fluxo completo

Copia, cria ou reutiliza classes, turmas e alunos ativos elegíveis, sem afirmar replicação automática de professores ou colaboradores.

Nos fluxos web atuais auditados, as gravações correspondentes são executadas dentro de transação. As proteções de reexecução são contextuais e dependem das chaves de destino, constraints, verificações de existência e `get_or_create` utilizados em cada fluxo.

Os fluxos de cópia que utilizam `log_ebd_audit_event` emitem evento estruturado no logger da aplicação com informações úteis para rastrear o processo.

---

# 19. Permissões e Escopo

A auditoria histórica de Professor EBD foi explicitamente marcada como documento antigo e potencialmente divergente após evolução do sistema de acesso.

Por isso, ela deve ser usada apenas como referência histórica.

O acesso não é resumido por uma única matriz funcional. As políticas de página `escola_biblica` e `escola_biblica_professor` são distintas e combinam grupos centrais, habilitação do módulo e regras específicas do fluxo.

Exemplos implementados:

- criação e edição de turma usam a política `escola_biblica`;
- exclusão de turma exige Superintendente;
- avaliações usam rotas compatíveis com o caminho de professor para listagem, criação e edição, enquanto a exclusão exige Superintendente;
- ofertas podem usar política de criação/edição distinta da política de exclusão;
- o dashboard utiliza política compatível com professor.

Administração, Secretaria EBD, Superintendência EBD, Pastor Local e Professor EBD não devem ser apresentados como equivalentes: cada jornada aplica sua própria política. Para fluxos de professor, o vínculo operacional reconhecido também é relevante. O acesso a alunos, turmas, chamadas e relatórios deve respeitar tanto a política da jornada quanto o escopo de igreja.

As regras transversais vigentes de autorização local também se aplicam aos fluxos EBD:

- pertencer ao mesmo Ministério, sozinho, não concede acesso operacional local;
- papéis locais dependem do escopo explícito registrado em `PerfilUsuario.igrejas_permitidas`; escopo permitido vazio falha fechado;
- não existe expansão automática de autorização pela hierarquia de igrejas;
- a igreja ativa é contexto operacional, não fonte de autorização, não representa “todas as igrejas” e somente pode contextualizar a operação quando estiver no escopo autorizado;
- `get_igrejas_selecionaveis()` define possibilidades de seleção e contexto, mas não substitui autorização funcional;
- `DepartamentoVinculo` não concede autorização nem amplia escopo de igreja;
- capabilities não concedem permissão isoladamente;
- `Cargo` e `MembroCargo` não concedem autorização local isoladamente; `Cargo.grupo_permissao` pode contribuir para os grupos efetivos do usuário, mas não substitui o escopo explícito de igreja;
- Admin Ministério não possui operação local irrestrita.

A política central vigente de acesso e a implementação da jornada devem prevalecer sobre decorators ou recomendações históricas isoladas.

---

# 20. Multi-Tenancy

A EBD é fortemente dependente de isolamento operacional por igreja.

Operações e consultas devem validar coerência entre:

```text
igreja
+
ano letivo
+
período
+
classe
+
turma
+
aluno
+
professor
+
lição
```

Consultas e operações aplicam escopo de igreja às turmas, classes, alunos e registros relacionados. `Classe.igreja` e `Turma.igreja` podem ser nulos em estruturas legadas; nesses casos, os filtros usam os vínculos disponíveis para limitar o escopo. `AnoLetivo` e `PeriodoEBD` são referências globais/compartilhadas, e não devem ser descritos como entidades com igreja obrigatória.

O conjunto de igrejas autorizadas deve ser determinado antes da escolha do contexto ativo; a igreja ativa não pode ampliá-lo. Ausência de escopo permitido falha fechado. Pertencer ao mesmo Ministério não é condição suficiente para acesso local, e a hierarquia não autoriza presumir acesso a igrejas descendentes ou ancestrais. Essas regras complementam a política de autorização da seção anterior.

Nenhuma cópia, chamada, avaliação ou relatório deve atravessar igrejas de forma implícita dentro dos fluxos que aplicam esses filtros. A configuração local também participa da segmentação operacional, inclusive nas chaves de cache utilizadas pelo auto-sync.

---

# 21. Integridade e Idempotência

Fluxos específicos da EBD possuem proteções contextuais contra duplicidade e efeitos indevidos de reexecução.

É documentada para:

- geração de períodos;
- geração de lições;
- preparação anual;
- cópia de turmas;
- chamada.

O objetivo é evitar duplicação e inconsistência em reexecuções legítimas. Cada fluxo possui sua própria estratégia, baseada, conforme o caso, em chaves, `get_or_create`, unicidades, verificações de existência, bloqueios ou controles de concorrência; isso não constitui promessa universal para chamadas externas, concorrência arbitrária ou uso isolado de qualquer service.

Também existem regras de integridade para:

- turma + data de lição;
- matrícula vigente;
- aluno da turma;
- oferta da classe correta;
- dia configurado;
- período válido.

---

# 22. Auditoria

Os fluxos que utilizam `log_ebd_audit_event` emitem eventos estruturados no logger da aplicação. Esses eventos auxiliam a rastreabilidade e a observabilidade e podem registrar, conforme aplicável:

- usuário;
- igreja;
- ano de origem;
- ano de destino;
- totais processados;
- resultado da operação.

Persistência, retenção e consulta desses registros dependem da infraestrutura de logging. O helper não cria, por si só, modelo próprio de auditoria, não garante imutabilidade e não equivale a uma trilha persistente própria da EBD. Outras ações críticas podem exigir controles proporcionais ao risco, conforme o GSF.

---

# 23. Segurança e Privacidade

A EBD processa dados pessoais, inclusive potencialmente de crianças e adolescentes.

Deve seguir:

- GSF;
- Segurança de Dados e Privacidade;
- Conformidade e LGPD;
- menor privilégio;
- isolamento por tenant;
- minimização.

Cuidados especiais:

- não expor alunos de outra turma ou igreja;
- evitar relatórios excessivamente amplos;
- proteger dados de menores;
- preservar histórico sem exposição indevida;
- restringir ofertas e informações financeiras;
- caso exportações sejam adicionadas, limitar exports ao escopo autorizado.

O módulo EBD atual não expõe rota própria de exportação. Eventuais exportações futuras devem aplicar escopo autorizado, minimização e requisitos de LGPD.

---

# 24. Testes e Qualidade

A documentação atual registra testes para:

- orçamento de consultas da chamada;
- regressão N+1;
- validação de alunos da turma;
- isolamento entre igrejas;
- idempotência;
- integridade de cópia anual;
- período válido;
- frequência;
- ofertas;
- avaliações.

O próprio documento de governança marca essas proteções como implementadas.

Testes de permissão devem utilizar a política atual e não depender de uma auditoria histórica antiga.

---

# 25. Operação por Perfil

Esta seção descreve responsabilidades funcionais esperadas; ela não substitui a autorização efetiva de cada rota.

## Secretaria / Superintendência

Esses perfis participam de jornadas administrativas e de acompanhamento, como estruturas, vínculos, preparação do ano, pendências, relatórios e revisão do resumo semanal, conforme a política aplicada à operação. Algumas ações sensíveis, como exclusões estruturais, exigem Superintendente.

## Professor

O professor operacionalmente reconhecido participa de jornadas compatíveis com suas turmas, como chamada e avaliações permitidas pelo caminho de professor. Ajustes cadastrais ou estruturais dependem da política específica da operação e podem demandar encaminhamento à Secretaria.

## Liderança e demais perfis com acesso

Podem participar de jornadas de acompanhamento, indicadores, pendências, progresso ou relatórios quando a política da página e o escopo autorizado permitirem. O acesso ao dashboard não deve ser interpretado isoladamente como autorização para qualquer alteração operacional.

---

# 26. Riscos e Pontos de Atenção

Riscos já documentados:

## Mudança de configuração no meio do ano

Alterar período ou dia da semana pode mudar a janela operacional esperada.

Deve haver política e comunicação adequadas.

## Dados legados fora das regras

Novas validações bloqueiam inconsistências futuras, mas dados antigos podem exigir saneamento específico.

## Permissões históricas

Documentos antigos de permissão podem não refletir a arquitetura atual.

## Configuração dual-source

Enquanto houver fallback ministerial, suporte e operação devem considerar qual origem está sendo aplicada.

## Histórico de turma

Excluir ou modificar estruturas com histórico pode afetar relatórios e rastreabilidade.

---

# 27. Evolução e Material Histórico

Existem documentos de roadmap, auditorias e runbooks relacionados à EBD.

Eles devem ser classificados corretamente:

- roadmap = planejamento/evolução;
- auditoria de permissões = evidência histórica;
- runbook = operação/suporte;
- guia operacional = orientação ao usuário;
- governança de período em família transitória = apoio técnico sujeito à comparação com a implementação e fontes canônicas especializadas.

Itens de roadmap não devem ser tratados como implementados apenas porque foram propostos.

---

# 28. Documentos Relacionados

## Canônicos e governança

- `docs/apps/README.md`
- `docs/apps/01-Membros.md`
- `docs/apps/02-Secretaria.md`
- `docs/arquitetura/08-Arquitetura-Multi-Tenant.md`

## EBD — guia de usuário

- `docs/usuario/GUIA_OPERACIONAL_EBD.md`

## EBD — apoio técnico e operacional

Os documentos abaixo ficam em família transitória ou descrevem suporte técnico; devem ser usados como apoio e confrontados com a implementação e com fontes canônicas especializadas quando houver conflito:

- `docs/sistema/ESCOLA_DOMINICAL_GOVERNANCA_PERIODO.md`
- `docs/sistema/ESCOLA_DOMINICAL_CONFIG_LOCAL_IGREJA.md`
- `docs/sistema/EBD_RUNBOOK_FASE1.md`
- `docs/sistema/EBD_RUNBOOK_OPERACAO_SUPORTE.md`

## EBD — histórico e planejamento

- `docs/sistema/AUDITORIA_PERMISSOES_PROFESSOR_EBD.md` — histórico
- `docs/sistema/ESCOLA_DOMINICAL_ROADMAP_PREMIUM.md` — roadmap
- `docs/CHANGELOG_EBD_2026-08.md` — histórico de mudanças

## Segurança e qualidade

- `docs/seguranca/08-Seguranca-de-Dados-e-Privacidade.md`
- `docs/seguranca/14-Conformidade-e-LGPD.md`
- `docs/qualidade/README.md`

---

# 29. Princípios Finais

A EBD deve preservar coerência entre:

```text
igreja
+
configuração
+
ano letivo
+
período
+
turma
+
aluno
+
professor
+
lição
+
permissão
```

A automação deve reduzir trabalho manual sem reduzir controle.

Integridade histórica, isolamento por igreja e proteções contextuais contra duplicidade e reexecução são requisitos centrais dos fluxos EBD.

---

# 30. Status

**Pasta:** `docs/apps/`

**Arquivo:** `06-EBD.md`

**Documento:** `APP-06`

**Versão:** `1.0`

**Status:** **EM CONSOLIDAÇÃO**

Este documento consolida a visão funcional em consolidação da Escola Bíblica Dominical a partir da implementação atual, do guia operacional e de documentação de apoio técnico ou histórico.

Políticas de acesso, escopo, configuração e operações devem ser confirmadas na implementação e nas fontes canônicas especializadas. Auditorias antigas e roadmaps devem ser lidos como histórico ou planejamento, não como fonte automática da regra vigente.
