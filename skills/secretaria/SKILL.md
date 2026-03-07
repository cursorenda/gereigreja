---
name: "gerenciando-secretaria"
description: "Gerencia cadastro de pessoas (Membros, Visitantes, Congregados, Novos Convertidos, Obreiros), famílias e histórico. Use para cadastro, edição, visualização ou relatórios de secretaria."
---

# Skill: Gerenciamento de Secretaria

## ⚠️ Importante: Terminologia Pessoa vs Membro

**Modelo de Dados:**
- **`Pessoa`** é o modelo REAL (tabela no banco de dados)
- **`Membro`** é apenas um PROXY de `Pessoa` para compatibilidade com código legado
- O campo `verbose_name` do proxy é `"Membro (compat)"` - indicando compatibilidade

**Tipos de Pessoa:**
O sistema gerencia diversos tipos via `TipoPessoa`:
- Membro
- Visitante  
- Congregado
- Novo Convertido
- Obreiro

**Nomenclatura Correta:**
- ✅ Use "Pessoa" como termo genérico/abrangente
- ✅ Use "Membro" apenas quando se referir especificamente ao tipo "Membro"
- ✅ URLs já usam `/pessoas/` (migração em andamento)
- ⚠️ Código legado ainda usa `Membro.objects` (funciona porque é proxy)

**Campo de Data de Nascimento:**
- ✅ O campo real é `nascimento` (não `data_nascimento`)
- ⚠️ Atenção ao usar em ordenações e filtros

---

# Quando Usar Esta Skill

Use esta skill quando:
- Cadastrar ou editar pessoas (Membros, Visitantes, Congregados, Novos Convertidos, Obreiros)
- Visualizar dados de pessoas (consulta readonly)
- Gerenciar famílias e relacionamentos
- Controlar status de pessoas (Ativo, Inativo, Desligado, Em Disciplina)
- Controlar tipo de pessoa (Membro, Visitante, Congregado, Novo Convertido, Obreiro)
- Gerar relatórios de secretaria
- Imprimir listas filtradas
- Registrar histórico de mudanças de status e tipo

## Estrutura de Dados Atual

### Pessoa (Modelo Base)

**⚠️ Terminologia Importante:**
- **`Pessoa`** é o modelo real (tabela no banco de dados)
- **`Membro`** é apenas um proxy de `Pessoa` para compatibilidade com código legado
- O sistema gerencia diversos tipos: Membros, Visitantes, Congregados, Novos Convertidos, Obreiros
- Use sempre `Pessoa` como termo genérico

```python
class Pessoa(models.Model):
    # Dados Pessoais
    nome = models.CharField(max_length=200)
    apelido = models.CharField(max_length=100, blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    rg = models.CharField(max_length=20, blank=True, null=True)
    nascimento = models.DateField()  # Note: campo é 'nascimento', não 'data_nascimento'
    genero = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Feminino')])
    estado_civil = models.CharField(max_length=20, blank=True, null=True)
    
    # Contato
    telefone = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Endereço
    endereco = models.CharField(max_length=300, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)
    
    # Igreja e Status
    igreja = models.ForeignKey(Igreja, on_delete=models.PROTECT)
    tipo_pessoa = models.ForeignKey(TipoPessoa, on_delete=models.PROTECT)
    status_pessoa = models.ForeignKey(StatusPessoa, on_delete=models.PROTECT)
    data_batismo = models.DateField(blank=True, null=True)
    data_congregacao = models.DateField(blank=True, null=True)
    
    # Tags e Relacionamentos
    tags = models.ManyToManyField(Tag, blank=True, related_name='pessoas')
    familia = models.ForeignKey(Familia, null=True, blank=True)
    
    # Outros
    foto = models.ImageField(upload_to='membros/', blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    chave = models.AutoField(primary_key=True)
```

### StatusHistorico
```python
class StatusHistorico(models.Model):
    membro = models.ForeignKey(Pessoa, on_delete=models.CASCADE)  # FK aponta para Pessoa
    status_pessoa_anterior = models.ForeignKey(StatusPessoa, related_name='historico_anterior')
    status_pessoa_novo = models.ForeignKey(StatusPessoa, related_name='historico_novo')
    tipo_pessoa_anterior = models.ForeignKey(TipoPessoa, related_name='tipo_historico_anterior', null=True)
    tipo_pessoa_novo = models.ForeignKey(TipoPessoa, related_name='tipo_historico_novo', null=True)
    data_transicao = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True, null=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
```

**⚠️ Importante: Nomes Corretos dos Campos**
- Use `data_transicao` (não `data_mudanca`)
- Use `status_pessoa_anterior` e `status_pessoa_novo` (não `status_anterior`, `status_novo`)
- Use `observacao` no singular (não `observacoes`)

## Funcionalidades Principais

### 1. Visualizar Pessoa (Readonly)
**Nova em v1.3.1** - Consulta rápida sem risco de edições acidentais

```python
# View: detalhe_membro()  # Nome da função mantido por compatibilidade
# Rota: /secretaria/pessoas/<int:membro_id>/visualizar/
# Template: secretaria/detalhe_membro.html
# Nota: Usa modelo Pessoa (Membro é apenas proxy)

@login_required
def detalhe_membro(request, membro_id):
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    # Membro funciona porque é proxy de Pessoa
    membro = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)
    
    tags = membro.tags.all()
    cargos_ativos = MembroCargo.objects.filter(membro=membro, data_fim__isnull=True)
    historico_status = StatusHistorico.objects.filter(membro=membro).order_by('-data_transicao')[:5]
    
    return render(request, 'secretaria/detalhe_membro.html', context)
```

**Botão na lista:**
```django
<a href="{% url 'secretaria:detalhe_membro' membro_id=membro.chave %}" 
   class="btn btn-vibrant-visualizar btn-icon">
    <i class="fas fa-eye"></i> Visualizar
</a>
```

### 2. Imprimir Lista com Filtros
**Nova em v1.3.1** - Relatório personalizado mantendo filtros aplicados

```python
# View: imprimir_lista_membros()
# Rota: /secretaria/pessoas/imprimir/
# Template: secretaria/imprimir_lista_membros.html

@login_required
def imprimir_lista_membros(request):
    # Aplica TODOS os filtros da lista principal
    # Retorna QuerySet completo (sem paginação)
    # Mostra filtros aplicados no cabeçalho
    # Template otimizado para impressão A4
```

**Botão de ação:**
```django
<a href="{% url 'secretaria:imprimir_lista_membros' %}?{{ request.GET.urlencode }}" 
   class="btn btn-vibrant-imprimir" target="_blank">
    <i class="fas fa-print"></i> Imprimir Lista
</a>
```

**Preserva filtros:**
- Nome/Apelido
- Tipo de Pessoa
- Status
- Gênero
- Tags
- Igreja

## Regras de Negócio

1. **Multi-Tenant**: Sempre filtrar por `igreja__in=allowed_churches`
2. **Permissões**: Validar acesso com `get_allowed_churches_for_membros()`
3. **CPF Único**: Validar e não permitir duplicados (quando fornecido)
4. **Histórico de Status**: Registrar todas as mudanças com `StatusHistorico`
5. **Campos Obrigatórios**: nome, data_nascimento, genero, igreja, tipo_pessoa, status_pessoa
6. **Select Related**: Sempre usar `.select_related('igreja', 'tipo_pessoa', 'status_pessoa')` em queries
7. **Soft Delete**: Não deletar membros, apenas mudar status para "Desligado"

## Classes CSS Semânticas (v1.3.1)

Use classes baseadas em **função** (não em cor):

```html
<!-- Visualizar (readonly) -->
<button class="btn btn-vibrant-visualizar">
    <i class="fas fa-eye"></i> Visualizar
</button>

<!-- Editar -->
<button class="btn btn-vibrant-editar">
    <i class="fas fa-edit"></i> Editar
</button>

<!-- Imprimir/Exportar -->
<button class="btn btn-vibrant-imprimir">
    <i class="fas fa-print"></i> Imprimir
</button>

<!-- Adicionar/Criar -->
<button class="btn btn-vibrant-adicionar">
    <i class="fas fa-plus"></i> Adicionar
</button>

<!-- Salvar/Confirmar -->
<button class="btn btn-vibrant-salvar">
    <i class="fas fa-save"></i> Salvar
</button>

<!-- Cancelar/Voltar -->
<button class="btn btn-vibrant-cancelar">
    <i class="fas fa-times"></i> Cancelar
</button>

<!-- Excluir/Deletar -->
<button class="btn btn-vibrant-excluir">
    <i class="fas fa-trash"></i> Excluir
</button>
```

**Benefícios:**
- Nome indica função do botão
- Facilita migração de estilos inline
- Mesma função = mesmo estilo em todo sistema
- Manutenção centralizada

## Exemplos de Uso

### Cadastrar Pessoa com Histórico
```python
from secretaria.models import Pessoa, StatusHistorico, StatusPessoa, TipoPessoa
# Nota: Membro também funciona (é proxy de Pessoa), mas prefira Pessoa

# Criar pessoa (pode ser Membro, Visitante, Congregado, etc)
pessoa = Pessoa.objects.create(
    nome='João Silva',
    cpf='123.456.789-00',
    nascimento='1990-05-15',  # Campo é 'nascimento', não 'data_nascimento'
    genero='M',
    celular='(11) 98765-4321',
    email='joao@email.com',
    igreja=igreja_obj,
    tipo_pessoa=TipoPessoa.objects.get(nome='Visitante'),  # Tipo define se é Membro, Visitante, etc
    status_pessoa=StatusPessoa.objects.get(nome='Ativo')
)

# Registrar histórico inicial (não tem status anterior)
StatusHistorico.objects.create(
    membro=pessoa,  # Campo 'membro' aceita objeto Pessoa
    status_pessoa_novo=pessoa.status_pessoa,
    tipo_pessoa_novo=pessoa.tipo_pessoa,
    observacao='Cadastro inicial como Visitante',
    registrado_por=request.user
)
```

### Mudar Status com Histórico
```python
def mudar_status_pessoa(pessoa, novo_status, observacao, usuario):
    """Altera status de uma pessoa (Membro, Visitante, etc) e registra no histórico"""
    # Salvar status anterior
    status_anterior = pessoa.status_pessoa
    tipo_anterior = pessoa.tipo_pessoa
    
    # Registrar histórico ANTES de atualizar
    StatusHistorico.objects.create(
        membro=pessoa,  # Campo 'membro' aceita Pessoa
        status_pessoa_anterior=status_anterior,
        status_pessoa_novo=novo_status,
        tipo_pessoa_anterior=tipo_anterior,
        tipo_pessoa_novo=pessoa.tipo_pessoa,  # Tipo pode ou não mudar junto
        data_transicao=timezone.now(),
        observacao=observacao,
        registrado_por=usuario
    )
    
    # Atualizar pessoa
    pessoa.status_pessoa = novo_status
    pessoa.save()
    
    return pessoa
```

### Listar Pessoas com Filtros
```python
def lista_membros(request):  # Nome mantido por compatibilidade
    """Lista todas as pessoas (Membros, Visitantes, Congregados, etc) com filtros"""
    allowed_churches = get_allowed_churches_for_membros(request.user)
    
    # Base queryset com filtro multi-tenant
    # Usa Membro (proxy) por compatibilidade, mas trabalha com tabela Pessoa
    membros = Membro.objects.filter(igreja__in=allowed_churches)
    
    # Aplicar filtros opcionais
    nome = request.GET.get('nome_apelido')
    if nome:
        membros = membros.filter(
            Q(nome__icontains=nome) | Q(apelido__icontains=nome)
        )
    
    tipo_id = request.GET.get('tipo')
    if tipo_id:
        membros = membros.filter(tipo_pessoa_id=tipo_id)
    
    status_id = request.GET.get('status')
    if status_id:
        membros = membros.filter(status_pessoa_id=status_id)
    
    genero = request.GET.get('genero')
    if genero:
        membros = membros.filter(genero=genero)
    
    tag_ids = request.GET.getlist('tags')
    if tag_ids:
        membros = membros.filter(tags__in=tag_ids).distinct()
    
    # IMPORTANTE: select_related ANTES de paginar
    membros = membros.select_related(
        'igreja', 'tipo_pessoa', 'status_pessoa'
    ).order_by('nome')
    
    # Paginar por último
    paginator = Paginator(membros, 25)
    page = request.GET.get('page', 1)
    membros_page = paginator.page(page)
    
    return render(request, 'secretaria/lista_membros.html', {
        'membros': membros_page
    })
```

### Buscar Histórico de Status
```python
# Últimas 5 transições de uma pessoa
historico = StatusHistorico.objects.filter(
    membro=pessoa  # Campo 'membro' aceita objetos Pessoa
).select_related(
    'status_pessoa_anterior',
    'status_pessoa_novo',
    'registrado_por'
).order_by('-data_transicao')[:5]

# Exibir no template
{% for hist in historico_status %}
    {{ hist.data_transicao|date:"d/m/Y H:i" }}
    {{ hist.status_pessoa_anterior.nome }} → {{ hist.status_pessoa_novo.nome }}
    Registrado por: {{ hist.registrado_por.get_full_name }}
{% endfor %}
```

### Gerar Relatório Filtrado
```python
@login_required
def imprimir_lista_membros(request):
    # Aplica mesma lógica de filtros da lista principal
    membros = aplicar_filtros(request)  # Sua função de filtros
    
    # SEM paginação para impressão
    membros = membros.select_related(
        'igreja', 'tipo_pessoa', 'status_pessoa'
    ).order_by('nome')
    
    # Capturar filtros aplicados para exibir no relatório
    filtros_aplicados = []
    if request.GET.get('nome_apelido'):
        filtros_aplicados.append(f"Nome: {request.GET['nome_apelido']}")
    if request.GET.get('tipo'):
        tipo = TipoPessoa.objects.get(pk=request.GET['tipo'])
        filtros_aplicados.append(f"Tipo: {tipo.nome}")
    # ... outros filtros
    
    return render(request, 'secretaria/imprimir_lista_membros.html', {
        'membros': membros,
        'total_membros': membros.count(),
        'filtros_aplicados': filtros_aplicados,
        'data_impressao': timezone.now()
    })
```


## Rotas Principais

### Lista e Gestão de Pessoas
**Nota:** URLs usam `/pessoas/` (nomenclatura correta). Funções usam `*_membro` por compatibilidade.

- `GET /secretaria/pessoas/` - Lista de pessoas (Membros, Visitantes, etc) com filtros
- `GET /secretaria/pessoas/<id>/visualizar/` - Visualização readonly (v1.3.1)
- `GET /secretaria/pessoas/<id>/editar/` - Edição de pessoa
- `GET /secretaria/pessoas/imprimir/` - Impressão com filtros (v1.3.1)
- `GET /secretaria/pessoas/<id>/ficha-impressao/` - Ficha individual para impressão
- `POST /secretaria/pessoas/<id>/alternar-status/` - Mudar status (AJAX)

### Cadastro Multi-Etapas
**Nota:** Cadastra qualquer tipo de pessoa (não apenas Membros)

- `GET /secretaria/pessoas/pre-cadastro/` - Etapa 1: Dados básicos (nome, nascimento, tipo, status)
- `GET /secretaria/pessoas/cadastro-detalhado/<id>/` - Etapa 2: Contato e endereço
- `GET /secretaria/pessoas/cadastro-complementar/<id>/` - Etapa 3: Histórico, tags e observações

### Acompanhamento de Visitas
**Nota:** Registra visitas feitas a pessoas (especialmente Visitantes e Novos Convertidos)

- `GET /secretaria/acompanhamentos-visita/` - Lista de acompanhamentos de visitas
- `POST /secretaria/acompanhamento-visita/<id>/editar/` - Editar registro de acompanhamento

## Views Importantes

### get_allowed_churches_for_membros()
```python
from secretaria.utils import get_allowed_churches_for_membros

# Em todas as views que trabalham com pessoas
allowed_churches = get_allowed_churches_for_membros(request.user)
pessoas = Pessoa.objects.filter(igreja__in=allowed_churches)
# Ou usar Membro (proxy) por compatibilidade:
# membros = Membro.objects.filter(igreja__in=allowed_churches)
```

**Retorna igrejas baseado no cargo do usuário:**
- Admin Ministerio → Todas as igrejas do ministério
- Pastor Regional/Admin Org → Igrejas configuradas + subordinadas
- Secretário Local → Igreja onde trabalha
- Pessoas comuns → Igreja onde é cadastrado

### has_membro_edit_permission()
```python
from secretaria.utils import has_membro_edit_permission

# Verificar se pode editar pessoas (cadastros)
if has_membro_edit_permission(request.user):
    # Mostrar botões de edição
    # Retorna True para: Admin Ministerio, Pastor Regional, Admin Org, Secretários
```

## Templates Principais

### lista_membros.html
**Nota:** Template lista todas as pessoas (Membros, Visitantes, Congregados, etc)

Lista paginada com filtros por:
- Nome/Apelido
- Tipo de Pessoa (Membro, Visitante, Congregado, Novo Convertido, Obreiro)
- Status (Ativo, Inativo, Desligado, Em Disciplina)
- Gênero
- Tags
- Igreja (modo consolidado)

**Botões de ação:**
- Visualizar (cyan) - v1.3.1
- Editar (blue)
- Imprimir (green)

### detalhe_membro.html (v1.3.1)
Visualização readonly de qualquer tipo de pessoa (Membro, Visitante, etc).

Seções:
- Foto
- Dados Pessoais
- Contato
- Endereço
- Informações da Igreja (tipo, status, batismo, etc)
- Tags
- Cargos Ativos
- Histórico de Status (mudanças de Visitante→Membro, Ativo→Inativo, etc)
- Observações

### imprimir_lista_membros.html (v1.3.1)
Template otimizado para impressão:
- Cabeçalho institucional
- Filtros aplicados
- Total de registros
- Tabela completa (sem paginação)
- CSS `@media print`

## Boas Práticas

1. **Multi-Tenant**: Sempre filtrar por igrejas permitidas
   ```python
   allowed_churches = get_allowed_churches_for_membros(request.user)
   # Prefira Pessoa (modelo real), mas Membro funciona (proxy)
   queryset = Pessoa.objects.filter(igreja__in=allowed_churches)
   ```

2. **Select Related**: Evitar N+1 queries
   ```python
   pessoas.select_related('igreja', 'tipo_pessoa', 'status_pessoa')
   # tipo_pessoa define se é Membro, Visitante, Congregado, etc
   # status_pessoa define se é Ativo, Inativo, Desligado, etc
   ```

3. **Ordem de Operações**: Filtros → select_related → order_by → Paginação
   ```python
   # 1. Filtros
   pessoas = pessoas.filter(status_pessoa__nome='Ativo')
   pessoas = pessoas.filter(tipo_pessoa__nome='Membro')  # Filtrar apenas Membros se necessário
   # 2. Select Related
   pessoas = pessoas.select_related('igreja', 'tipo_pessoa', 'status_pessoa')
   # 3. Ordenação
   pessoas = pessoas.order_by('nome')
   # 4. Paginação (por último!)
   paginator = Paginator(pessoas, 25)
   ```

4. **Histórico de Status**: Sempre registrar mudanças
   ```python
   StatusHistorico.objects.create(
       membro=pessoa,  # Campo 'membro' aceita objetos Pessoa
       status_pessoa_anterior=status_antigo,
       status_pessoa_novo=status_novo,
       tipo_pessoa_anterior=tipo_antigo,  # Ex: Visitante
       tipo_pessoa_novo=tipo_novo,  # Ex: Membro (quando convertido)
       observacao=motivo,
       registrado_por=request.user
   )
   ```

5. **Nomes de Campos Corretos**:
   - ✅ Modelo é `Pessoa` (não `Membro` - este é apenas proxy)
   - ✅ Campo de data de nascimento é `nascimento` (não `data_nascimento`)
   - ✅ StatusHistorico: `data_transicao` (não `data_mudanca`)
   - ✅ StatusHistorico: `status_pessoa_anterior` (não `status_anterior`)
   - ✅ StatusHistorico: `status_pessoa_novo` (não `status_novo`)
   - ✅ StatusHistorico: `observacao` no singular (não `observacoes`)

6. **Classes CSS Semânticas**: Usar função, não cor
   ```html
   <!-- ✅ Correto -->
   <button class="btn btn-vibrant-salvar">Salvar</button>
   
   <!-- ❌ Evitar -->
   <button class="btn btn-vibrant-green">Salvar</button>
   ```

7. **Soft Delete**: Não deletar, mudar status
   ```python
   # ❌ Não fazer
   pessoa.delete()
   
   # ✅ Fazer
   status_desligado = StatusPessoa.objects.get(nome='Desligado')
   mudar_status_pessoa(pessoa, status_desligado, 'Motivo do desligamento', request.user)
   ```

8. **Validação de Permissões**: Em todas as views
   ```python
   @login_required
   def minha_view(request):
       allowed_churches = get_allowed_churches_for_membros(request.user)
       if not allowed_churches.exists():
           return HttpResponseForbidden('Sem permissão')
   ```

9. **Template de Impressão**: Sempre otimizar para A4
   ```css
   @media print {
       .no-print { display: none !important; }
       @page { size: A4; margin: 15mm; }
   }
   ```

10. **Preservar Filtros**: Em navegação e impressão
    ```django
    <a href="{% url 'secretaria:imprimir_lista_membros' %}?{{ request.GET.urlencode }}">
        Imprimir
    </a>
    ```

## Novidades v1.3.1 (06/03/2026)

### ✨ Recursos Adicionados
- **Visualização Readonly**: Botão "Visualizar" para consulta sem edição de qualquer pessoa
- **Impressão com Filtros**: Relatórios personalizados mantendo todos os filtros aplicados
- **Classes CSS Semânticas**: 7 novas classes baseadas em função (não cor)
- **Colunas Ordenáveis**: Headers clicáveis com alternância ASC/DESC e indicadores visuais
- **Correção StatusHistorico**: Campos corrigidos para nomes reais do banco de dados
- **Correção Campo Nascimento**: Ordenação usa `nascimento` (não `data_nascimento`)

### 📝 Melhorias de Documentação
- **Clarificação Terminológica**: Documentação agora distingue claramente entre:
  * `Pessoa` = modelo real (tabela no banco)
  * `Membro` = proxy de compatibilidade
  * "Membro" como tipo = uma das opções de TipoPessoa
- Sistema gerencia 5+ tipos: Membros, Visitantes, Congregados, Novos Convertidos, Obreiros
- "Pessoa" é o termo genérico correto para se referir a qualquer cadastro

### 🔗 Documentação Relacionada
- [CHANGELOG.md](../../CHANGELOG.md) - Histórico completo de mudanças
- [RELEASE_NOTES_v1.3.1.md](../../docs/release-notes/RELEASE_NOTES_v1.3.1.md) - Detalhes da versão
- [botoes.css](../../static/css/botoes.css) - Classes CSS com comentários
