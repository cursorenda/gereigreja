Pasta:
docs/apps/

Arquivo:
09-Usuarios.md

Documento:
APP-09

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

# 09 — Usuários

> O domínio Usuários representa identidades autenticáveis, vínculos com pessoas e igrejas, grupos, cargos e regras de autorização que determinam o que cada usuário pode acessar e operar no GereIgreja.

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Conceitos Centrais
5. Usuário, Pessoa e Igreja
6. Igreja Ativa e Contexto
7. Grupos de Permissão
8. Hierarquia de Grupos
9. Cargos e Permissões
10. Grupos Efetivos
11. Vínculo entre Cargo e Usuário
12. Escopo Hierárquico
13. Page Access
14. Superusuário
15. Usuário Comum
16. Autenticação e Autorização
17. Multi-Tenancy
18. Gestão de Usuários
19. Ativação, Desativação e Histórico
20. Segurança e Privacidade
21. Auditoria
22. Testes e Qualidade
23. Integrações com Outros Domínios
24. Documentação de Usuário Final
25. Pontos a Validar
26. Documentos Relacionados
27. Princípios Finais
28. Status

---

# 1. Objetivo

Este documento consolida a visão funcional canônica do domínio Usuários no GereIgreja.

Seu objetivo é registrar:

- o que representa um usuário no sistema;
- como usuário, pessoa e igreja se relacionam;
- como grupos e cargos influenciam acesso;
- como a hierarquia de permissões funciona funcionalmente;
- como o contexto da igreja limita ações;
- como permissões manuais e derivadas de cargos coexistem;
- quais regras pertencem a Segurança/Autenticação e quais pertencem ao domínio funcional.

Este documento não substitui o GAF, o GSF, a documentação técnica de permissões ou os manuais de usuário final.

---

# 2. Escopo

O domínio Usuários cobre, conforme a documentação auditada:

- identidade autenticável;
- vínculo com pessoa;
- vínculo com igreja;
- igreja ativa;
- grupos;
- cargos;
- permissões efetivas;
- hierarquia de acesso;
- regras de page access;
- escopo hierárquico;
- ativação e situação do usuário;
- relacionamento com Secretaria e demais módulos.

---

# 3. Papel deste Documento

Este é o documento funcional canônico de Usuários em `docs/apps/`.

A relação esperada é:

```text
docs/apps/09-Usuarios.md
        ↓
Visão funcional do domínio
        ↓
docs/frameworks/02-GAF...
docs/seguranca/
docs/sistema/HIERARQUIA_PERMISSOES.md
docs/sistema/CARGOS_USUARIOS.md
docs/usuario/
        ↓
Autenticação, autorização, operação e manual
```

A pasta `docs/usuario/` continua sendo destinada à documentação para usuário final.

`docs/apps/09-Usuarios.md` documenta o domínio funcional do sistema.

---

# 4. Conceitos Centrais

Os conceitos principais são distintos:

```text
Pessoa
↓
identidade humana/cadastral

Usuário
↓
identidade autenticável

Igreja
↓
contexto organizacional

Cargo
↓
função exercida

Grupo
↓
papel de autorização

Permissão
↓
capacidade efetiva
```

Esses conceitos podem se relacionar, mas não devem ser tratados como equivalentes.

---

# 5. Usuário, Pessoa e Igreja

Uma pessoa cadastrada não deve ser automaticamente tratada como usuário autenticável.

Da mesma forma, um usuário autenticado pode depender de vínculo correto com pessoa e igreja para operar determinadas funcionalidades.

A documentação operacional de cargos registra explicitamente a necessidade de validar se o usuário associado ao membro existe e está ativo.

Portanto:

```text
Pessoa existente
≠
Usuário ativo
```

---

# 6. Igreja Ativa e Contexto

O GereIgreja é multi-tenant.

A autorização funcional deve considerar não apenas quem é o usuário, mas também em qual igreja ele está operando.

Fluxo funcional:

```text
Usuário
   ↓
Igreja ativa
   ↓
Grupos / cargos
   ↓
Regra da página
   ↓
Escopo do objeto
   ↓
Ação permitida ou negada
```

O mesmo usuário pode possuir contexto e capacidade diferentes conforme a igreja ativa e seus vínculos.

---

# 7. Grupos de Permissão

Grupos representam papéis de autorização do sistema.

A documentação atual registra como grupos oficiais:

- Admin Ministerio;
- Secretaria Ministerial;
- Tesouraria Ministerial;
- Pastor Regional;
- Pastor Local;
- Secretario Local;
- Tesoureiro;
- Superintendente EBD;
- Equipe de Eventos;
- Equipe de Mídia;
- Equipe de Recepção;
- Professores EBD;
- Secretaria EBD;
- Membro Comum.

Os nomes dos grupos devem permanecer consistentes com as constantes centrais do sistema.

---

# 8. Hierarquia de Grupos

A documentação técnica atual mantém uma hierarquia ordenada de grupos.

Essa hierarquia permite responder perguntas como:

```text
Este usuário possui nível igual ou superior ao papel exigido?
```

A hierarquia não deve ser reimplementada manualmente em cada módulo.

A política central de autorização é a fonte de verdade técnica.

---

# 9. Cargos e Permissões

Cargo representa função ministerial ou operacional.

Exemplos documentados:

- Secretário Local;
- Tesoureiro;
- Líder de Grupo.

Um cargo pode possuir um grupo de permissão associado.

Quando isso ocorre, ocupantes ativos do cargo podem receber o grupo correspondente.

Cargo sem grupo também é válido, funcionando apenas como registro organizacional.

---

# 10. Grupos Efetivos

A documentação operacional registra a seguinte regra:

```text
grupos efetivos
=
grupos vindos de cargos ativos
+
grupos manuais administrativos
```

Essa composição existe para evitar que a sincronização de cargos apague permissões concedidas administrativamente.

Portanto, uma origem de grupo não deve sobrescrever indiscriminadamente a outra.

---

# 11. Vínculo entre Cargo e Usuário

O fluxo documentado é:

```text
Pessoa/Membro
   ↓
Ocupante de cargo
   ↓
Cargo possui grupo?
   ├── Não → apenas vínculo funcional
   └── Sim → grupo aplicado ao usuário associado
```

Ao encerrar um vínculo:

- o vínculo se torna histórico;
- o grupo derivado daquele cargo pode ser removido;
- o grupo deve permanecer se outro cargo ativo ainda justificar o mesmo acesso.

Ao editar o grupo de um cargo, os grupos efetivos dos usuários impactados devem ser recalculados.

---

# 12. Escopo Hierárquico

O módulo de cargos possui escopo hierárquico documentado.

Regras atuais registradas:

## Admin Ministério

Pode visualizar e gerenciar todos os cargos.

## Pastor Regional

Pode gerenciar cargos de Pastor Regional para baixo na hierarquia.

## Pastor Local

Pode gerenciar cargos de Pastor Local para baixo.

## Outros perfis

Não possuem acesso a essa gestão, salvo regra posterior explicitamente documentada.

Esse escopo evita que um perfil local administre papéis hierarquicamente superiores.

---

# 13. Page Access

O projeto utiliza política centralizada de acesso por página.

A documentação registra o padrão:

```text
@page_access_required("<chave>")
```

com regras mantidas em:

```text
contas/page_permissions.py
```

Funcionalmente, isso significa que:

- acesso não deve ser decidido por template;
- visibilidade do menu não é autorização;
- cada página protegida deve usar a regra central vigente;
- módulos não devem duplicar regras arbitrárias de grupos.

---

# 14. Superusuário

Há uma nuance importante na documentação atual:

em páginas protegidas via `page_access_required`, não existe bypass automático universal apenas por `is_superuser`.

Se uma tela exigir comportamento especial de superusuário, isso deve estar explicitamente implementado.

Portanto:

```text
is_superuser
≠
bypass implícito de toda regra de page access
```

Essa regra deve ser validada conforme a política técnica vigente sempre que houver mudança no framework de autorização.

---

# 15. Usuário Comum

O grupo `Membro Comum` representa o nível mais baixo da hierarquia documentada.

Usuário comum não deve receber acesso administrativo apenas por estar autenticado.

O acesso funcional deve depender da matriz de permissões aplicável.

---

# 16. Autenticação e Autorização

Autenticação responde:

```text
Quem é o usuário?
```

Autorização responde:

```text
O que esse usuário pode fazer neste contexto?
```

O domínio Usuários depende das duas, mas suas regras técnicas pertencem ao GAF e ao GSF.

Este documento registra apenas o comportamento funcional esperado.

---

# 17. Multi-Tenancy

Permissão não deve ser avaliada sem considerar tenant.

Toda operação de usuário deve preservar:

- igreja ativa;
- escopo do papel;
- escopo do objeto;
- vínculos válidos.

Um usuário com papel elevado em uma igreja não deve receber automaticamente o mesmo alcance em outra igreja.

---

# 18. Gestão de Usuários

A documentação auditada contém material de evolução de usuários e permissões, mas não oferece uma especificação única e atual de todas as telas de gestão.

Por isso, este documento não inventa CRUD, campos ou estados não confirmados.

Funcionalmente, a gestão deve garantir:

- associação correta a pessoa;
- associação correta à igreja;
- situação ativa;
- grupos corretos;
- ausência de escalonamento indevido;
- consistência com cargos;
- rastreabilidade de mudanças relevantes.

---

# 19. Ativação, Desativação e Histórico

Usuário inativo não deve continuar operando áreas protegidas.

Quando cargo é encerrado, o histórico funcional deve ser preservado.

A documentação de cargos enfatiza encerramento do vínculo em vez de apagar histórico.

A mesma filosofia deve orientar a gestão de identidades quando houver necessidade de preservar rastreabilidade.

---

# 20. Segurança e Privacidade

Usuários são parte crítica da superfície de segurança.

O domínio deve seguir:

- GAF;
- GSF;
- menor privilégio;
- controle de acesso;
- isolamento multi-tenant;
- proteção de dados;
- auditoria.

Cuidados obrigatórios incluem:

- não confiar em menu oculto;
- não confiar apenas em grupo enviado pela interface;
- não conceder acesso por cargo sem política explícita;
- evitar escalonamento de privilégio;
- preservar escopo hierárquico;
- proteger alterações administrativas.

---

# 21. Auditoria

Mudanças críticas de acesso devem ser auditáveis quando aplicável.

Exemplos:

- adição/removação de grupo;
- alteração de cargo com grupo;
- vínculo ou encerramento de ocupante;
- ativação/desativação de usuário;
- mudança relevante de escopo;
- concessão administrativa manual.

A auditoria específica deve seguir os padrões gerais do GSF.

---

# 22. Testes e Qualidade

A documentação atual recomenda testar pelo menos:

- superusuário;
- staff sem grupo;
- staff com grupo correto;
- staff com grupo incorreto;
- usuário comum.

Também existem testes específicos de autorização de cargos.

Testes devem verificar:

- page access;
- escopo hierárquico;
- igreja correta;
- grupos derivados de cargos;
- coexistência com grupos manuais;
- remoção segura após encerramento;
- acesso direto por URL.

---

# 23. Integrações com Outros Domínios

## Secretaria

É onde atualmente está documentada a gestão de cargos e ocupantes.

## Membros

Pessoa/Membro pode estar associado a um usuário e ocupar cargos.

## Financeiro

Tesoureiro e grupos financeiros influenciam acesso, mas autorização financeira deve continuar pertencendo ao domínio Financeiro.

## EBD

Professores, Secretaria EBD e Superintendência possuem papéis específicos.

## Eventos e Comunicação

Equipes podem receber acesso através dos grupos correspondentes.

## Configurações

Contexto de igreja e estruturas organizacionais podem afetar o escopo do usuário.

---

# 24. Documentação de Usuário Final

A pasta `docs/usuario/` contém materiais como:

- manual geral;
- guias de melhorias;
- guia de EBD;
- documentação de IgrejaUser;
- assinatura e planos.

Esses documentos explicam o sistema para quem o utiliza.

Eles não devem ser confundidos com esta especificação funcional do domínio Usuários.

---

# 25. Pontos a Validar

A auditoria identificou pontos que precisam ser confirmados no código atual antes de expansão normativa:

1. fluxo atual de criação de usuário;
2. relação exata entre Pessoa e User;
3. regras atuais de convite/onboarding;
4. recuperação e troca de credenciais;
5. política atual de ativação/desativação;
6. regras de remoção de usuário;
7. escopo de Admin Django versus painel web;
8. sincronização completa entre cargos e grupos;
9. comportamento atual de superusuário em todas as page keys;
10. existência de MFA ou outros fatores de autenticação.

Esses tópicos pertencem parcialmente ao GAF e não justificam duplicação automática neste documento.

---

# 26. Documentos Relacionados

## Funcionais

- `docs/apps/README.md`
- `docs/apps/01-Membros.md`
- `docs/apps/02-Secretaria.md`

## Permissões e cargos

- `docs/sistema/HIERARQUIA_PERMISSOES.md`
- `docs/sistema/CARGOS_USUARIOS.md`
- `docs/sistema/CARGOS_SISTEMA.md`
- `docs/sistema/DOCUMENTACAO_PADRAO_GRUPOS.md`

## Frameworks e segurança

- `docs/frameworks/02-GAF-GereIgreja-Authentication-Framework.md`
- `docs/frameworks/03-GSF-GereIgreja-Security-Framework.md`
- `docs/seguranca/04-Autorizacao-e-Controle-de-Acesso.md`
- `docs/seguranca/05-Seguranca-Multi-Tenant.md`

## Usuário final

- `docs/usuario/README.md`
- `docs/usuario/USUARIO_MANUAL.md`
- `docs/usuario/README_IGREJA_USER.md`
- `docs/usuario/MELHORIAS_USUARIOS_v1.7.2.md`
- `docs/usuario/MELHORIAS_USUARIOS_v1.8.0_a_v1.8.67.md`
- `docs/usuario/MELHORIAS_USUARIOS_v1.8.75.md`

---

# 27. Princípios Finais

O domínio Usuários deve preservar a diferença entre:

```text
Pessoa
+
Usuário
+
Igreja
+
Cargo
+
Grupo
+
Permissão
```

Nenhum desses conceitos deve ser usado como substituto informal de outro.

O acesso efetivo deve resultar de política centralizada, contexto correto e menor privilégio.

---

# 28. Status

**Pasta:** `docs/apps/`

**Arquivo:** `09-Usuarios.md`

**Documento:** `APP-09`

**Versão:** `1.0`

**Status:** **OFICIAL**

A lacuna documental foi confirmada em `docs/apps/`.

Este documento consolida o domínio funcional de Usuários sem duplicar o GAF, o GSF ou os manuais destinados ao usuário final.
