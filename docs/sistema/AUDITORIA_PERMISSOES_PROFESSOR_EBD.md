> **Aviso:** documento histórico (fev/2026). Pode divergir do estado atual após a migração para `@page_access_required` + `PAGE_ACCESS_RULES`.

## Atualizacao de Estado (28/05/2026)

Este arquivo permanece como auditoria historica de permissoes, mas o modulo EBD evoluiu significativamente no eixo de governanca de periodo e automacao operacional.

### O que mudou no estado atual da EBD

- O periodo EBD passou a seguir a configuracao ministerial (`ebd_periodo`) de forma centralizada.
- O modulo agora possui auto-sync de periodos e licoes para reduzir dependencia de clique manual.
- A automacao e acionada em pontos criticos de uso (dashboard, chamada por turma e lista de turmas).
- Foram adicionadas validacoes de dominio para bloquear registros fora do periodo EBD valido.

### Regras tecnicas em vigor

1. Licao:
- So pode ser salva se a data estiver dentro de um periodo EBD valido para a turma.
- Constraint de unicidade por turma+data.

2. Frequencia:
- Nao permite data futura.
- Exige data dentro do periodo EBD valido da turma.
- Exige aderencia ao dia da semana configurado para EBD no ministerio.

3. Oferta por turma:
- Exige data dentro do periodo EBD valido da turma.

### Referencia tecnica oficial atual

Para arquitetura e operacao atualizadas, consulte:

- `docs/sistema/ESCOLA_DOMINICAL_GOVERNANCA_PERIODO.md`

### Nota

As secoes abaixo deste bloco preservam a auditoria original de 17/02/2026 para rastreabilidade historica.

# 🔐 Auditoria de Permissões: Professor EBD
## Análise Completa de Acesso às Views - Escola Bíblica

> **Data da auditoria:** 17/02/2026  
> **Módulo:** escola_biblica  
> **Total de views:** 41  
> **Foco:** Definir o que Professor EBD pode e não pode acessar

---

## 📊 Sumário Executivo

| Categoria | Qtd Views | Professor Pode? | Observações |
|-----------|-----------|-----------------|-------------|
| **Dashboard/Relatórios** | 5 | ⚠️ Parcial | Dados filtrados por suas turmas |
| **Turmas (listar)** | 1 | ✅ Sim | Apenas suas turmas |
| **Turmas (gerenciar)** | 3 | ❌ Não | Criar/editar/excluir = secretaria |
| **Alunos (listar/ver)** | 2 | ✅ Sim | Apenas alunos de suas turmas |
| **Alunos (gerenciar)** | 2 | ❌ Não | Criar/transferir = secretaria |
| **Chamada de Presença** | 1 | ✅ Sim | **JÁ IMPLEMENTADO** ✅ |
| **Lições** | 5 | ❌ Não | Gestão = secretaria |
| **Classes** | 4 | ❌ Não | Gestão = secretaria |
| **Avaliações** | 4 | ❌ Não | Gestão = secretaria |
| **Ofertas** | 4 | ❌ Não | Financeiro = secretaria |
| **Frequência** | 1 | ⚠️ Parcial | Ver suas turmas |
| **Cargos** | 1 | ❌ Não | Administrativo |
| **Períodos/Cópias** | 4 | ❌ Não | Administrativo |
| **Utilitários** | 1 | ✅ Sim | AJAX helper |

---

## 🎯 ANÁLISE DETALHADA POR VIEW

### 1. DASHBOARD E GRÁFICOS (5 views)

#### ✅ 1.1. `dashboard()` - Dashboard Principal
**URL:** `/` (raiz do módulo)  
**Decorator atual:** `@login_required` apenas  
**Permissão atual:** Qualquer usuário logado

**Análise:**
```python
# Linha 1574-1720
@login_required
def dashboard(request):
    # Mostra estatísticas gerais: turmas, alunos, classes, lições, ofertas
    # Rankings, gráficos de evolução, frequência
```

**🔴 PROBLEMA:** Professor vê dashboard vazio ou com dados incorretos porque:
- `turmas = Turma.objects.all()` → mostra TODAS as turmas
- `alunos = Aluno.objects.all()` → mostra TODOS os alunos
- Não filtra por `get_turmas_professor(request.user)`

**✅ SOLUÇÃO:**
```python
@login_required
def dashboard(request):
    # Verificar se é secretaria ou professor
    is_secretaria = (
        request.user.is_superuser or 
        request.user.groups.filter(name__in=['Secretaria EBD', 'Superintendente EBD']).exists()
    )
    
    if is_secretaria:
        turmas = Turma.objects.all()
        alunos = Aluno.objects.all()
    else:
        # Professor: apenas suas turmas e alunos
        turmas = get_turmas_professor(request.user)
        alunos = Aluno.objects.filter(turma__in=turmas).distinct()
    
    # Resto do código...
```

**Recomendação:** ✅ **PERMITIR com filtro**
- Professor vê apenas dados de suas turmas
- Rankings e gráficos filtrados
- Oferta: ❌ **ESCONDER** (dado financeiro)

---

#### ⚠️ 1.2. `graficos_evolucao()` - Gráficos de Evolução
**URL:** `/graficos-evolucao/`  
**Decorator:** `@login_required` apenas  
**Permissão:** Qualquer usuário

**Análise:**
```python
# Linha 1225-1253
@login_required
def graficos_evolucao(request):
    # Retorna JSON com evolução de alunos, frequência
```

**🔴 PROBLEMA:** Retorna dados de todas as turmas

**Recomendação:** ✅ **PERMITIR com filtro**
```python
is_secretaria = request.user.groups.filter(
    name__in=['Secretaria EBD', 'Superintendente EBD']
).exists()

if is_secretaria:
    alunos = Aluno.objects.all()
else:
    turmas_prof = get_turmas_professor(request.user)
    alunos = Aluno.objects.filter(turma__in=turmas_prof)
```

---

#### ⚠️ 1.3. `dashboard_graficos()` - Dashboard de Gráficos
**URL:** `/graficos/`  
**Decorator:** `@login_required`  

**Análise:**
```python
# Linha 1255-1287
@login_required
def dashboard_graficos(request):
    # Renderiza página com gráficos (usa API acima)
```

**Recomendação:** ✅ **PERMITIR** (usa dados filtrados da API)

---

#### ❌ 1.4. `relatorio_ebd_dia()` - Relatório Consolidado do Dia
**URL:** `/relatorio/ebd-dia/`  
**Decorator:** `@login_required` + `@secretaria_ebd_required` ✅  
**Permissão:** **Secretaria EBD apenas**

**Análise:**
```python
# Linha 102-214
@login_required
@secretaria_ebd_required
def relatorio_ebd_dia(request):
    # Relatório CONSOLIDADO de todas as turmas
    # Comparação com aula anterior
    # Totais gerais (matriculados, presentes, ofertas)
```

**Recomendação:** ❌ **NÃO PERMITIR**
- É relatório gerencial consolidado
- Professor não precisa dessa visão macro
- **Já está protegido corretamente** ✅

---

#### ⚠️ 1.5. `relatorio_frequencia()` - Relatório de Frequência
**URL:** `/relatorio/frequencia/`  
**Decorator:** `@login_required` + `@secretaria_ebd_required` ✅  
**Permissão:** **Secretaria EBD apenas**

**Análise:**
```python
# Linha 1154-1204
@login_required
@secretaria_ebd_required
def relatorio_frequencia(request):
    # Relatório detalhado de frequência por turma/período
    # Com filtros e exportação
```

**🤔 DEBATE:** Professor deveria ver frequência de SUAS turmas?

**Opção A - Manter bloqueado (atual):**
- ❌ Professor não vê
- Razão: Relatório complexo, pode confundir

**Opção B - Permitir com filtro:**
- ✅ Professor vê apenas suas turmas
- Razão: Útil para acompanhamento pedagógico

**💡 Recomendação:** ✅ **PERMITIR COM FILTRO** (melhor UX)
```python
@login_required
def relatorio_frequencia(request):
    is_secretaria = request.user.groups.filter(
        name__in=['Secretaria EBD', 'Superintendente EBD']
    ).exists()
    
    if is_secretaria:
        turmas = Turma.objects.all()
    else:
        turmas = get_turmas_professor(request.user)
        if not turmas.exists():
            messages.info(request, "Você não possui turmas atribuídas.")
            return redirect('escola_biblica:dashboard')
```

---

### 2. TURMAS (4 views)

#### ✅ 2.1. `turma_list()` - Listar Turmas
**URL:** `/turmas/`  
**Decorator:** `@login_required` + `@verificar_assinatura_valida`  
**Permissão:** Qualquer usuário

**Análise:**
```python
# Linha 1774-1956 (CÓDIGO DUPLICADO DETECTADO!)
@login_required
@verificar_assinatura_valida
def turma_list(request):
    # Verifica se é secretaria
    is_secretaria = (
        request.user.is_superuser or 
        request.user.groups.filter(name__in=['Secretaria EBD', 'Superintendente EBD']).exists()
    )
    
    if not is_secretaria:
        # Professor vê apenas suas turmas
        turmas_professor = get_turmas_professor(request.user)
        turmas_list = turmas_list.filter(id__in=turmas_professor.values_list('id', flat=True))
```

**✅ Status:** **JÁ IMPLEMENTADO CORRETAMENTE!**
- Professor vê apenas suas turmas ✅
- Secretaria vê todas ✅

**⚠️ PROBLEMA DETECTADO:** Código duplicado nas linhas 1774-1956
```python
# Bloco 1: linhas 1774-1880
turmas_list = Turma.objects.filter(ano_letivo=ano_letivo_selecionado)
is_secretaria = ...
if not is_secretaria:
    turmas_professor = get_turmas_professor(request.user)
    turmas_list = turmas_list.filter(...)

# Bloco 2: linhas 1898-2000 (DUPLICADO!)
# Mesmo código repetido
```

**🔧 CORREÇÃO NECESSÁRIA:** Remover código duplicado

---

#### ❌ 2.2. `turma_create()` - Criar Turma
**URL:** `/turmas/novo/`  
**Decorator:** `@login_required` + `@secretaria_ebd_required` ✅  

**Recomendação:** ❌ **NÃO PERMITIR** (já protegido)

---

#### ❌ 2.3. `turma_edit()` - Editar Turma
**URL:** `/turmas/<id>/editar/`  
**Decorator:** `@login_required` + `@secretaria_ebd_required` ✅  

**Recomendação:** ❌ **NÃO PERMITIR** (já protegido)

---

#### ❌ 2.4. `turma_delete()` - Excluir Turma
**URL:** `/turmas/<id>/excluir/`  
**Decorator:** `@login_required` + `@superintendente_required` ✅  

**Recomendação:** ❌ **NÃO PERMITIR** (já protegido, só superintendente)

---

### 3. ALUNOS (4 views)

#### ✅ 3.1. `aluno_list()` - Listar Alunos
**URL:** `/alunos/`  
**Decorator:** `@login_required` + `@verificar_assinatura_valida`  

**Análise:**
```python
# Linha 1726-1758
@login_required
@verificar_assinatura_valida
def aluno_list(request):
    # Verifica se é secretaria
    is_secretaria = (
        request.user.is_superuser or 
        request.user.groups.filter(name__in=['Secretaria EBD', 'Superintendente EBD']).exists()
    )
    
    if is_secretaria:
        alunos_list = Aluno.objects.all()
    else:
        # Professor vê apenas alunos de suas turmas
        turmas_professor = get_turmas_professor(request.user)
        alunos_list = Aluno.objects.filter(turma__in=turmas_professor).distinct()
```

**✅ Status:** **JÁ IMPLEMENTADO CORRETAMENTO!**
- Professor vê apenas alunos de suas turmas ✅

---

#### ✅ 3.2. `aluno_detail()` - Ver Detalhes do Aluno
**URL:** `/alunos/<id>/`  
**Decorator:** `@login_required` apenas

**Análise:**
```python
# Linha 1100-1122
@login_required
def aluno_detail(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    # ⚠️ NÃO VERIFICA PERMISSÃO!
```

**🔴 PROBLEMA CRÍTICO:** Qualquer usuário pode ver qualquer aluno!

**✅ CORREÇÃO URGENTE:**
```python
@login_required
def aluno_detail(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    
    # Verifica se pode ver este aluno
    if not pode_ver_aluno(request.user, aluno):
        raise PermissionDenied("Você não tem permissão para ver este aluno.")
    
    # resto do código...
```

**Recomendação:** ✅ **PERMITIR com verificação** (função `pode_ver_aluno()` já existe!)

---

#### ❌ 3.3. `aluno_create()` - Criar Aluno
**URL:** `/alunos/novo/`  
**Decorator:** `@login_required` + `@secretaria_ebd_required` ✅  

**Recomendação:** ❌ **NÃO PERMITIR** (já protegido v1.2.2)

---

#### ❌ 3.4. `transferir_aluno()` - Transferir Aluno
**URL:** `/alunos/<id>/transferir/`  
**Decorator:** `@login_required` + `@secretaria_ebd_required` ✅  

**Recomendação:** ❌ **NÃO PERMITIR** (já protegido)

---

### 4. CHAMADA DE PRESENÇA (1 view)

#### ✅ 4.1. `chamada_presenca()` - Fazer Chamada
**URL:** `/turmas/<id>/chamada/`  
**Decorator:** `@login_required` apenas  
**Verificação interna:** `pode_acessar_chamada_turma()` ✅

**Análise:**
```python
# Linha 216-395
@login_required
def chamada_presenca(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Verifica permissão (secretaria EBD ou professor da turma)
    if not pode_acessar_chamada_turma(request.user, turma):
        raise PermissionDenied("Você não tem permissão...")
```

**✅ Status:** **IMPLEMENTADO CORRETAMENTE NO v1.2.2!**
- Professor pode fazer chamada de suas turmas ✅
- Secretaria pode fazer de todas ✅
- Verificação granular funcionando ✅

---

### 5. LIÇÕES (5 views)

#### ❌ 5.1. `licao_list()` - Listar Lições
**URL:** `/licoes/`  
**Decorator:** `@login_required` apenas  

**Análise:**
```python
# Linha 1427-1479
@login_required
def licao_list(request):
    licoes = Licao.objects.all()  # TODAS as lições
```

**🤔 DEBATE:** Professor deveria ver lições de suas turmas?

**Opção A - Bloquear (atual implícito):**
- ❌ Professor não vê
- Razão: Pode confundir com gestão

**Opção B - Permitir com filtro:**
- ✅ Professor vê apenas lições de suas turmas
- Razão: Útil para planejamento pedagógico

**💡 Recomendação:** ✅ **PERMITIR COM FILTRO** (melhor UX)
```python
@login_required
def licao_list(request):
    is_secretaria = request.user.groups.filter(
        name__in=['Secretaria EBD', 'Superintendente EBD']
    ).exists()
    
    if is_secretaria:
        licoes = Licao.objects.all()
    else:
        turmas = get_turmas_professor(request.user)
        licoes = Licao.objects.filter(turma__in=turmas)
```

---

#### ❌ 5.2-5.5. `licao_create/edit/delete()` + `gerar_cronograma_wizard()`
**Decorators:** `@secretaria_ebd_required` ✅  

**Recomendação:** ❌ **NÃO PERMITIR** (já protegidos)
- Criar/editar/excluir lições = gestão administrativa
- Wizard de geração em lote = secretaria

---

### 6. CLASSES (4 views)

#### ❌ 6.1-6.4. `classe_list/create/edit/delete()`
**Decorators:** `@secretaria_ebd_required` ✅  

**Recomendação:** ❌ **NÃO PERMITIR**
- Gestão de classes = estrutura administrativa
- Professor não precisa criar/editar classes

---

### 7. AVALIAÇÕES (4 views)

#### ❌ 7.1. `avaliacao_list()` - Listar Avaliações
**URL:** `/avaliacoes/`  
**Decorator:** `@login_required` apenas  

**🤔 DEBATE:** Professor deveria gerenciar avaliações de suas turmas?

**Cenário real:**
- Professor aplica provas/avaliações
- Precisa registrar notas

**Opção A - Bloquear (atual):**
- ❌ Professor não gerencia avaliações
- Secretaria registra tudo

**Opção B - Permitir:**
- ✅ Professor cria avaliações de suas turmas
- ✅ Registra notas

**💡 Recomendação:** ⚠️ **DEBATER COM USUÁRIO**
- Depende do fluxo de trabalho da igreja
- Se professor aplica prova → deve poder registrar
- Se secretaria centraliza → manter bloqueado

**Por ora:** ❌ **MANTER BLOQUEADO** (adicionar decorator)
```python
@login_required
@secretaria_ebd_required  # ← ADICIONAR
def avaliacao_list(request):
```

---

#### ❌ 7.2-7.4. `avaliacao_create/edit/delete()`
**Decorator:** `@secretaria_ebd_required` ✅  

**Recomendação:** ❌ **NÃO PERMITIR**

---

### 8. OFERTAS (4 views)

#### ❌ 8.1-8.4. `oferta_classe_*`
**Decorators:** `@secretaria_ebd_required` ✅  

**Recomendação:** ❌ **NÃO PERMITIR**
- Dados financeiros = secretaria/tesoureiro
- Professor não gerencia ofertas

**⚠️ NOTA:** Professor REGISTRA valor da oferta na chamada, mas não gerencia historicamente

---

### 9. FREQUÊNCIA (1 view)

#### ⚠️ 9.1. `frequencia_list()` - Listar Frequências
**URL:** `/frequencia/`  
**Decorator:** `@login_required` apenas  

**Análise:**
```python
# Linha 1983-1995
@login_required
@verificar_assinatura_valida
def frequencia_list(request):
    frequencias_list = Frequencia.objects.all()  # TODAS!
```

**🔴 PROBLEMA:** Mostra frequências de todas as turmas

**Recomendação:** ✅ **PERMITIR COM FILTRO**
```python
is_secretaria = request.user.groups.filter(
    name__in=['Secretaria EBD', 'Superintendente EBD']
).exists()

if is_secretaria:
    frequencias_list = Frequencia.objects.all()
else:
    turmas = get_turmas_professor(request.user)
    frequencias_list = Frequencia.objects.filter(aluno__turma__in=turmas)
```

---

### 10. RELATÓRIOS (1 view)

#### ⚠️ 10.1. `relatorio_alunos()` - Relatório de Alunos
**URL:** `/relatorio/alunos/`  
**Decorator:** `@login_required` apenas  

**Análise:**
```python
# Linha 1338-1378
@login_required
def relatorio_alunos(request):
    alunos = Aluno.objects.all()  # TODOS os alunos
```

**Recomendação:** ✅ **PERMITIR COM FILTRO**
```python
is_secretaria = request.user.groups.filter(
    name__in=['Secretaria EBD', 'Superintendente EBD']
).exists()

if is_secretaria:
    alunos = Aluno.objects.all()
else:
    turmas = get_turmas_professor(request.user)
    alunos = Aluno.objects.filter(turma__in=turmas)
```

---

### 11. CARGOS (1 view)

#### ❌ 11.1. `cargos_ebd_list()` - Listar Cargos EBD
**URL:** `/cargos-ebd/`  
**Decorator:** `@login_required` apenas  

**Análise:**
```python
# Linha 1207-1222
@login_required
def cargos_ebd_list(request):
    # Lista cargos da EBD (professores, secretários)
```

**Recomendação:** ❌ **BLOQUEAR** (adicionar decorator)
```python
@login_required
@secretaria_ebd_required  # ← ADICIONAR
def cargos_ebd_list(request):
```

**Razão:** Professor não gerencia cargos

---

### 12. PERÍODOS E CÓPIAS (4 views)

#### ❌ 12.1. `abrir_novo_periodo()` - Abrir Período
**URL:** `/abrir_novo_periodo/`  
**Decorator:** `@secretaria_ebd_required` ✅  

**Recomendação:** ❌ **NÃO PERMITIR** (já protegido)

---

#### ❌ 12.2. `copiar_turmas_ano_anterior()` - Copiar Turmas
**URL:** `/copiar_turmas_ano_anterior/`  
**Decorator:** `@secretaria_ebd_required` ✅  

**Recomendação:** ❌ **NÃO PERMITIR** (já protegido)

---

#### ❌ 12.3. `copiar_periodo_selecao()` - Copiar Período
**URL:** `/copiar_periodo_selecao/`  
**Decorator:** `@secretaria_ebd_required` ✅  

**Recomendação:** ❌ **NÃO PERMITIR** (já protegido)

---

#### ❌ 12.4. `gerar_cronograma()` - Gerar Cronograma (versão antiga)
**URL:** `/licoes/gerar_cronograma/`  
**Decorator:** `@secretaria_ebd_required` ✅  

**Recomendação:** ❌ **NÃO PERMITIR** (já protegido)

---

### 13. UTILITÁRIOS (1 view)

#### ✅ 13.1. `get_professor_nome()` - AJAX Helper
**URL:** `/get_professor/`  
**Decorator:** `@login_required` apenas  

**Análise:**
```python
# Linha 895-904
@login_required
def get_professor_nome(request):
    # Retorna nome do professor para autocomplete
    # Usado em formulários
```

**Recomendação:** ✅ **PERMITIR**
- Função auxiliar, não expõe dados sensíveis
- Necessária para UX de formulários

---

## 🔥 BUGS CRÍTICOS ENCONTRADOS

### 🐛 Bug 1: `aluno_detail()` sem verificação de permissão
**Severity:** 🔴 CRÍTICO  
**Arquivo:** `views.py` linha 1100  
**Problema:** Qualquer usuário pode ver qualquer aluno

**Correção:**
```python
@login_required
def aluno_detail(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    
    # ✅ ADICIONAR ESTA VERIFICAÇÃO
    if not pode_ver_aluno(request.user, aluno):
        raise PermissionDenied("Você não tem permissão para ver este aluno.")
    
    # resto...
```

**Função já existe:** `pode_ver_aluno()` linha 81-98

---

### 🐛 Bug 2: Código duplicado em `turma_list()`
**Severity:** 🟡 MÉDIO  
**Arquivo:** `views.py` linhas 1774-1956  
**Problema:** Bloco inteiro de código copiado/colado

**Correção:** Remover linhas 1898-1956 (duplicadas)

---

### 🐛 Bug 3: Views sem decorator mas com acesso irrestrito
**Severity:** 🟠 ALTO  

Views que precisam de `@secretaria_ebd_required`:

1. `avaliacao_list()` - linha 1381
2. `cargos_ebd_list()` - linha 1207
3. `licao_list()` - linha 1427 (ou filtrar)
4. `frequencia_list()` - linha 1983 (ou filtrar)
5. `relatorio_alunos()` - linha 1338 (ou filtrar)

---

## 📋 RESUMO DE CORREÇÕES NECESSÁRIAS

### ✅ Prioridade 1 - URGENTE (Segurança)

1. **Adicionar verificação em `aluno_detail()`**
   ```python
   if not pode_ver_aluno(request.user, aluno):
       raise PermissionDenied(...)
   ```

2. **Remover código duplicado em `turma_list()`**
   - Deletar linhas 1898-1956

---

### ⚠️ Prioridade 2 - IMPORTANTE (Funcionalidade)

3. **Filtrar `dashboard()` por professor**
   ```python
   if not is_secretaria:
       turmas = get_turmas_professor(request.user)
       alunos = Aluno.objects.filter(turma__in=turmas)
   ```

4. **Filtrar `graficos_evolucao()` por professor**

5. **Filtrar `relatorio_frequencia()` por professor** (ou bloquear)

6. **Filtrar `licao_list()` por professor** (ou bloquear)

7. **Filtrar `frequencia_list()` por professor**

8. **Filtrar `relatorio_alunos()` por professor**

---

### 🔒 Prioridade 3 - LIMPEZA (Consistência)

9. **Adicionar decorators faltantes:**
   - `@secretaria_ebd_required` em:
     * `avaliacao_list()`
     * `cargos_ebd_list()`

10. **Adicionar `@verificar_assinatura_valida` onde falta**

---

## 🎯 RECOMENDAÇÃO FINAL: O QUE PROFESSOR EBD DEVE VER

| View | Acesso | Filtro | Status Atual |
|------|--------|--------|--------------|
| **dashboard** | ✅ Ver | Só suas turmas | 🔴 Não filtrado |
| **graficos_evolucao** | ✅ Ver | Só suas turmas | 🔴 Não filtrado |
| **dashboard_graficos** | ✅ Ver | - | ✅ OK |
| **relatorio_ebd_dia** | ❌ Não | - | ✅ Já bloqueado |
| **relatorio_frequencia** | ✅ Ver | Só suas turmas | 🔴 Bloqueado |
| **turma_list** | ✅ Ver | Só suas turmas | ✅ OK |
| **turma_create/edit/delete** | ❌ Não | - | ✅ Já bloqueado |
| **aluno_list** | ✅ Ver | Só suas turmas | ✅ OK |
| **aluno_detail** | ✅ Ver | Se for seu aluno | 🔴 **SEM VERIFICAÇÃO** |
| **aluno_create/transferir** | ❌ Não | - | ✅ Já bloqueado |
| **chamada_presenca** | ✅ Fazer | Só suas turmas | ✅ OK (v1.2.2) |
| **licao_list** | ✅ Ver | Só suas turmas | 🔴 Não filtrado |
| **licao_create/edit/delete** | ❌ Não | - | ✅ Já bloqueado |
| **classe_***  | ❌ Não | - | ✅ Já bloqueado |
| **avaliacao_***  | ❌ Não | - | 🟡 Sem decorator |
| **oferta_***  | ❌ Não | - | ✅ Já bloqueado |
| **frequencia_list** | ✅ Ver | Só suas turmas | 🔴 Não filtrado |
| **relatorio_alunos** | ✅ Ver | Só suas turmas | 🔴 Não filtrado |
| **cargos_ebd_list** | ❌ Não | - | 🟡 Sem decorator |
| **períodos/cópias** | ❌ Não | - | ✅ Já bloqueado |
| **get_professor_nome** | ✅ Sim | - | ✅ OK |

**Legenda:**
- ✅ OK = Funcionando corretamente
- 🔴 Não filtrado = Mostra dados de todos
- 🔴 SEM VERIFICAÇÃO = Falha de segurança
- 🟡 Sem decorator = Falta proteção

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Segurança (AGORA)
- [ ] Corrigir `aluno_detail()` (adicionar `pode_ver_aluno()`)
- [ ] Remover código duplicado `turma_list()`
- [ ] Adicionar `@secretaria_ebd_required`:
  - [ ] `avaliacao_list()`
  - [ ] `cargos_ebd_list()`

### Fase 2: Funcionalidade (DEPOIS v1.2.2)
- [ ] Filtrar `dashboard()` por professor
- [ ] Filtrar `graficos_evolucao()` por professor
- [ ] Decidir com usuário: `relatorio_frequencia()`
- [ ] Decidir com usuário: `licao_list()`
- [ ] Filtrar `frequencia_list()` por professor
- [ ] Filtrar `relatorio_alunos()` por professor

### Fase 3: Testes
- [ ] Testar como Professor EBD
- [ ] Testar como Secretaria EBD
- [ ] Testar como Superintendente EBD
- [ ] Verificar mensagens de erro amigáveis

---

## 🎓 DECISÕES PENDENTES (CONSULTAR USUÁRIO)

### 1. Relatório de Frequência
**Pergunta:** Professor deve ver relatório de frequência de suas turmas?
- ✅ SIM: útil para acompanhamento pedagógico
- ❌ NÃO: pode confundir, relatório é complexo

### 2. Lições (visualização)
**Pergunta:** Professor deve ver/consultar lições cadastradas?
- ✅ SIM: útil para planejamento de aula
- ❌ NÃO: pode confundir com gestão

### 3. Avaliações
**Pergunta:** Professor aplica avaliações e registra notas?
- ✅ SIM: precisa criar avaliações de suas turmas
- ❌ NÃO: secretaria centraliza tudo

---

**Documento criado:** 17/02/2026  
**Autor:** Análise automatizada + validação manual  
**Próxima revisão:** Após correções da Fase 1

