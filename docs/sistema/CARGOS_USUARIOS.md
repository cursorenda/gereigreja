# Manual de Cargos para Usuarios

Data de criacao: 08/04/2026  
Ultima atualizacao: 08/04/2026 (revisado)

---

## 1. Objetivo

Este documento explica, de forma pratica, como usar a tela de cargos:

- Cadastro e edicao de cargos
- Vinculo de ocupantes
- Encerramento de vinculos
- Como os grupos de permissao sao aplicados

Tela principal: /secretaria/cargos/

---

## 2. Conceitos Rapidos

- Cargo: funcao ministerial ou operacional (ex.: Secretario Local, Tesoureiro, Lider de Grupo).
- Ocupante: pessoa vinculada ao cargo.
- Vinculo ativo: quando nao possui data de fim.
- Vinculo historico: quando possui data de fim.
- Grupo de permissao do cargo: grupo do sistema associado ao cargo.

---

## 3. Fluxo Recomendado de Uso

### 3.1 Criar cargo

1. Acesse Secretaria > Cargos.
2. Clique em Criar Cargo.
3. Preencha Nome do Cargo.
4. Se necessario, selecione o Grupo de Permissao.
5. Salve.

Observacao:
- Se o cargo tiver grupo associado, os ocupantes ativos desse cargo receberao esse acesso automaticamente.

### 3.2 Vincular ocupante ao cargo

1. Na lista de cargos, abra Gerenciar Ocupantes.
2. Selecione o membro.
3. Informe data de inicio.
4. Salve.

Resultado esperado:
- O membro passa a ser ocupante ativo.
- Se houver grupo de permissao no cargo, o usuario associado ao membro recebe o grupo automaticamente.

### 3.3 Encerrar vinculo (nao excluir historico)

1. Em Gerenciar Ocupantes, finalize o vinculo do ocupante.
2. O sistema grava data de fim.

Resultado esperado:
- O vinculo vira historico.
- O grupo vindo daquele cargo e removido, se nao existir outro cargo ativo que mantenha o mesmo grupo.

### 3.4 Editar cargo

1. Altere nome ou grupo de permissao.
2. Salve.

Resultado esperado:
- O sistema recalcula os grupos efetivos dos usuarios impactados.

### 3.5 Excluir cargo

Regra importante:
- Nao e permitido excluir cargo com vinculos (ativos ou historicos).
- Primeiro finalize/regularize os vinculos e depois exclua.

---

## 4. Como as Permissoes Funcionam na Pratica

Regra da etapa atual:

grupos efetivos = grupos vindos de cargos ativos + grupos manuais administrativos

Isso evita:

- Perda de acesso por sobrescrita acidental
- Conflito entre painel hierarquico e cargos

---

## 5. Erros Comuns e Como Evitar

1. Tentar excluir cargo com historico
- Solucao: manter historico e nao excluir ate regularizar politica local.

2. Encerrar cargo e esperar que tudo continue igual
- Solucao: lembre que o grupo daquele cargo pode ser removido automaticamente.

3. Criar cargo sem grupo quando esperava liberar acesso
- Solucao: revise o campo Grupo de Permissao do cargo.

4. Achar que so painel de permissoes controla acesso
- Solucao: cargo ativo tambem controla acesso quando possui grupo associado.

---

## 6. Checklist Operacional (Secretaria)

Antes de fechar o dia:

1. Revisar cargos com ocupantes sem data de inicio.
2. Revisar vinculos que deveriam estar encerrados.
3. Confirmar se cargos com acesso critico possuem grupo correto.
4. Validar se o usuario vinculado ao membro existe e esta ativo.

---

## 7. FAQ Rapido

1. Um membro pode ter mais de um cargo ativo?
- Sim.

2. Se dois cargos diferentes apontam para o mesmo grupo, o que acontece?
- O grupo permanece enquanto existir pelo menos um desses cargos ativo.

3. Posso usar cargo sem grupo de permissao?
- Sim. Nesse caso, o cargo organiza funcao, mas nao altera acesso no sistema.

4. Quem pode gerenciar cargos?
- Admin Ministerio, Pastor Regional e Pastor Local (escopo local da igreja ativa).

5. Posso renomear grupo de permissao no Admin Django?
- Para grupos centralizados da hierarquia, nao. O nome e protegido para manter consistencia com as regras do sistema.
- A edicao permitida no Admin e a lista de permissoes do grupo.
