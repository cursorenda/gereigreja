# Documentacao Tecnica de Cargos (Sistema)

Data de criacao: 08/04/2026  
Ultima atualizacao: 08/04/2026 (revisado)

---

## 1. Escopo

Este documento descreve a arquitetura e as regras tecnicas do modulo de cargos, com foco em:

- Modelagem
- Sincronizacao de grupos
- Pontos de escrita em grupos
- Regras de consistencia para deploy

---

## 2. Modelos Envolvidos

### 2.1 Cargo

Campos relevantes:

- nome
- grupo_permissao (opcional)
- is_ebd (quando aplicavel ao fluxo EBD)

Responsabilidade:
- Definir funcao e, opcionalmente, associar grupo de permissao do Django.

### 2.2 MembroCargo

Campos relevantes:

- membro
- cargo
- data_inicio
- data_fim (null = ativo)

Responsabilidade:
- Registrar historico de ocupacao de cargo.

---

## 3. Regra de Negocio Consolidada

Regra principal desta etapa:

grupos efetivos = grupos por cargos ativos + grupos manuais validos

Objetivo:
- Evitar sobrescrita entre fluxos manuais e fluxos automaticos de cargo.

---

## 4. Componente Central

Arquivo central:

- core/group_sync.py

Funcoes principais:

1. grupos_por_cargo_ativo(user)
- Calcula grupos derivados de cargos ativos do usuario.

2. recalcular_grupos_efetivos_usuario(...)
- Aplica merge seguro entre grupos por cargo e grupos manuais.
- Permite escopo de grupos editaveis para nao apagar grupos fora do contexto.

3. grupos_reservados_para_cargo()
- Identifica grupos ligados a cargos, util para limpeza de estado antigo quando necessario.

---

## 5. Integracao com Signals

Arquivo:

- secretaria/signals.py

Fluxo:

1. pre_save cacheia estado anterior de MembroCargo.
2. post_save recalcula grupos do estado anterior e do estado novo quando houve alteracao relevante.
3. post_delete recalcula grupos apos exclusao do vinculo.

Beneficio:
- Estado final deterministico mesmo com mudanca de cargo, membro e data_fim.

---

## 6. Pontos de Escrita Manual em Grupos

Arquivos atualizados para usar merge seguro:

- contas/views_paineis_permissoes.py
- contas/views.py
- secretaria/views.py

Antes:
- groups.set(...) direto em multiplos fluxos.

Agora:
- recalcular_grupos_efetivos_usuario(...)

Resultado:
- Fluxos manuais deixam de sobrescrever grupos vindos de cargo ativo.

---

## 7. Casos Criticos Cobertos

1. Criar vinculo ativo adiciona grupo do cargo.
2. Inativar vinculo remove grupo do cargo quando nao ha outro vinculo ativo equivalente.
3. Dois cargos ativos no mesmo grupo mantem o grupo.
4. Grupo manual nao e perdido ao inativar cargo.
5. Recalculo manual nao remove grupo ainda sustentado por cargo ativo.

Testes de referencia:

- secretaria/tests/test_cargos_permissoes.py

---

## 8. Riscos Conhecidos e Contencao

### 8.1 Estado historico antigo

Risco:
- Usuarios podem estar com grupos incoerentes por regras antigas.

Mitigacao:
- Rodar reconciliacao de grupos antes do deploy produtivo.

### 8.2 Workflows fora do padrao

Risco:
- Novo codigo futuro voltar a usar groups.set direto.

Mitigacao:
- Padrao de equipe: qualquer alteracao de grupos deve passar pelo modulo central.

### 8.3 Ruido de auditoria

Risco:
- Logs de permissao podem crescer devido a recalculos frequentes.

Mitigacao:
- Monitorar volume e, se necessario, otimizar registro de eventos redundantes.

---

## 9. Checklist Tecnico Pre-Deploy

1. manage.py check sem erros.
2. Suite focada de cargos/permissoes verde.
3. Validar fluxos manuais principais:
- painel hierarquico
- edicao de papeis
- acesso na edicao de membro
4. Validar fluxo de cargo:
- criar vinculo
- encerrar vinculo
- editar cargo
5. Executar reconciliacao de grupos para eliminar legado inconsistente.

---

## 10. Padrao para Evolucoes Futuras

1. Nao escrever em user.groups diretamente nas views.
2. Encapsular alteracao de grupos em servico unico.
3. Criar teste de regressao para cada novo ponto que alterar permissao.
4. Manter regra deterministica e documentada.

---

## 11. Atualizacoes Aplicadas em 08/04/2026

1. Nomes oficiais de grupos ministeriais atualizados:
- Secretaria Ministerial (antes: Lideranca Secretaria)
- Tesouraria Ministerial (antes: Lideranca Financeira)

2. Modulo de cargos ajustado para permitir acesso de Pastor Local nas operacoes de:
- lista
- criacao
- edicao
- exclusao
- gerenciar ocupantes

3. Django Admin configurado para proteger o campo nome dos grupos centralizados.
- Permitido: editar permissoes do grupo.
- Bloqueado: renomear grupos centralizados fora de fluxo controlado (codigo + migration).

4. Filtro de escopo hierarquico para cargos implementado (NEW em 08/04/2026 - late update):
   - Pastor Local: vê/gerencia cargos a partir de PASTOR_LOCAL para baixo
   - Pastor Regional: vê/gerencia cargos a partir de PASTOR_REGIONAL para baixo
   - Admin Ministério: sem restrição (vê todos)
   
   Implementação:
   - Funcoes helper em secretaria/views.py:
     * _nomes_grupos_permitidos_para_cargos(user) — determina grupos visíveis
     * _filtrar_cargos_por_escopo_usuario(user, cargos_qs) — filtra queryset
     * _cargo_dentro_escopo_usuario(user, cargo) — valida acesso direto
   
   - Views aplicadas (5):
     * lista_cargos — filtra lista
     * criar_cargo — limita dropdown grupo_permissao
     * editar_cargo — bloqueia + limita form
     * excluir_cargo — bloqueia acesso
     * gerenciar_ocupantes — bloqueia acesso
   
   - Test suite: secretaria/tests/test_cargos_autorizacao_views.py (6 testes, todos OK)
