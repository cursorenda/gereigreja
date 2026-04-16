# GUIA TÉCNICO: Implementação da Vincução Pessoa ↔ CadastroAluno

---

## PARTE 1: DIAGRAMA VISUAL DETALHADO

### Arquitetura ATUAL (Fragmentada)

```
┌──────────────────────────────────────────────────────────────────────┐
│                        BANCO DE DADOS ATUAL                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────┐   ┌──────────────────────────────┐ │
│  │  TABELA: secretaria_pessoa  │   │  TABELA: escola_biblica_     │ │
│  │  (54 campos)                │   │  cadastroaluno (10 campos)   │ │
│  ├─────────────────────────────┤   ├──────────────────────────────┤ │
│  │ chave (PK)                  │   │ id (PK)                      │ │
│  │ usuario_id (FK -> User)     │   │ nome ⭐ DUPLICADO             │ │
│  │ igreja_id (FK)              │   │ data_nascimento ⭐ DUPLICADO │ │
│  │ nome ⭐ DUPLICADO             │   │ responsavel ⭐ DUPLICADO      │ │
│  │ apelido                     │   │ telefone_responsavel ⭐ DUPL. │ │
│  │ cpf                         │   │ observacoes                  │ │
│  │ rg                          │   │ ativo                        │ │
│  │ nascimento ⭐ DUPLICADO       │   │ igreja_id (FK)               │ │
│  │ genero                      │   │ created_at                   │ │
│  │ estado_civil                │   │ updated_at                   │ │
│  │ profissao                   │   │ ✅ SEM pessoa_id (FK FALTA)   │ │
│  │ escolaridade                │   └──────────────────────────────┘ │
│  │ email ❌ FALTA EM EBD         │                                  │
│  │ telefone                    │          ❌ NÃO HÁ                 │
│  │ celular                     │          RELAÇÃO DIRETA            │
│  │ cep, rua, número, bairro... │          ❌                        │
│  │ tipo_pessoa_id (FK)         │   ┌──────────────────────────────┐ │
│  │ status_pessoa_id (FK)       │   │  TABELA: escola_biblica_    │ │
│  │ grupo_casa_id (FK)          │   │  aluno (7 campos)           │ │
│  │ tags (M2M)                  │   ├──────────────────────────────┤ │
│  │ foto                        │   │ id (PK)                      │ │
│  │ criado_em, atualizado_em    │   │ cadastro_id (FK)             │ │
│  │ ... + 27 outros campos ...  │   │ nome ⭐ DUPLICADO             │ │
│  └─────────────────────────────┘   │ data_nascimento ⭐ DUPLICADO │ │
│                                      │ turma_id (FK)                │ │
│                                      │ responsavel ⭐ DUPLICADO      │ │
│                                      │ telefone_resp ⭐ DUPLICADO   │ │
│                                      │ ativo (duplica status)       │ │
│                                      │ created_at, updated_at       │ │
│                                      └──────────────────────────────┘ │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘

❌ PROBLEMA: Dados espalhados, desconectados, sem sincronização
```

### Arquitetura FUTURA PROPOSTA (Fase 1)

```
┌──────────────────────────────────────────────────────────────────────┐
│                  BANCO DE DADOS COM VINCULAÇÃO                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────┐                                    │
│  │  TABELA: secretaria_pessoa  │                                    │
│  │  (Master Global de Pessoas) │                                    │
│  ├─────────────────────────────┤                                    │
│  │ chave (PK)                  │───┐                                │
│  │ nome ✅ MASTER               │   │                                │
│  │ nascimento ✅ MASTER         │   │                                │
│  │ email ✅ MASTER              │   │                                │
│  │ telefone, celular ✅ MASTER  │   │                                │
│  │ rua, número, bairro ✅ MAST. │   │                                │
│  │ tipo_pessoa_id (FK)          │   │                                │
│  │ status_pessoa_id (FK)        │   │                                │
│  │ + 40 outros campos           │   │                                │
│  └─────────────────────────────┘   │                                │
│                                     │ NEW FK <<<<<<<<<               │
│                                     │                                │
│  ┌──────────────────────────────┐  │                                │
│  │ TABELA: escola_biblica_      │◄─┘                                │
│  │ cadastroaluno (11 campos)    │                                    │
│  ├──────────────────────────────┤   (pessoa_id FK NEW!)             │
│  │ id (PK)                      │                                    │
│  │ pessoa_id (FK) ✅ NEW!        │ ←── Vincula com Pessoa            │
│  │ nome (sincron. from Pessoa)  │                                    │
│  │ data_nascimento (sinc.)      │                                    │
│  │ responsavel (local EBD)      │                                    │
│  │ telefone_responsavel (local) │                                    │
│  │ observacoes_ebd              │                                    │
│  │ ativo                        │                                    │
│  │ igreja_id (FK)               │                                    │
│  │ created_at, updated_at       │                                    │
│  └──────────────────────────────┘                                    │
│           ↓                                                          │
│  ┌──────────────────────────────┐                                    │
│  │ TABELA: escola_biblica_aluno │                                    │
│  ├──────────────────────────────┤                                    │
│  │ id (PK)                      │                                    │
│  │ cadastro_id (FK) ✅ MANTÉM   │                                    │
│  │ turma_id (FK)                │                                    │
│  │ nome (denormalizado p/ speed)│                                    │
│  │ + 4 outros campos            │                                    │
│  └──────────────────────────────┘                                    │
│           ↓                                                          │
│  ┌──────────────────────────────┐                                    │
│  │ TABELA: escola_biblica_      │                                    │
│  │ frequencia, avaliacao, etc   │                                    │
│  └──────────────────────────────┘                                    │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘

✅ BENEFÍCIO: Pessoa é master, CadastroAluno consome dados via FK
```

### Fluxo de Sincronização (Novo)

```
USO SECTARIA (Criar/Editar Pessoa)
│
└─► Pessoa.save()
    │
    └─► Pessoa.nome = "João Silva"
        Pessoa.nascimento = 01/01/2010
        Pessoa.status_pessoa = "Ativo"
        
        Pessoa.save() triggers
        ├─ StatusHistorico criado
        └─ Qualquer CadastroAluno vinculado fica "marcado para sincronização"


USO EBD (Criar/Editar Aluno)
│
└─► Aluno.save()
    │
    └─► try: find or create CadastroAluno
        │
        ├─ Se encontrar Pessoa correspondente
        │  └─► CadastroAluno.pessoa = Pessoa (auto-link)
        │      CadastroAluno.nome = Pessoa.nome (sync)
        │
        └─► Aluno.cadastro = CadastroAluno
            Aluno.nome = CadastroAluno.nome (copy)


QUERY: "Quem é tal aluno?"
│
└─► CadastroAluno.objects.get(pk=123)
    .pessoa  ◄─ NEW! Acessa Pessoa mestre se vinculado
    .matriculas.all()  ◄─ todas as matrículas por ano
```

---

## PARTE 2: ARQUIVO: Migration 0022

**Arquivo**: `escola_biblica/migrations/0022_cadastroaluno_pessoa.py`

```python
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('secretaria', '#### LATEST_SECRETARIA_MIGRATION ####'),  # Ajustar!
        ('escola_biblica', '0021_cadastroaluno_aluno_cadastro'),
    ]

    operations = [
        # 1. Adicionar FK pessoa (nullable inicialmente)
        migrations.AddField(
            model_name='cadastroaluno',
            name='pessoa',
            field=models.ForeignKey(
                blank=True,
                help_text='Vinculação com pessoa em Secretaria (se aplicável)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='registros_ebd',
                to='secretaria.pessoa',
                verbose_name='Pessoa (Secretaria)'
            ),
        ),
        
        # 2. Criar índice para busca rápida de vinculações
        migrations.AddIndex(
            model_name='cadastroaluno',
            index=models.Index(
                fields=['pessoa'],
                name='escola_bibl_pessoa_idx',
            ),
        ),
        
        # 3. Backfill: Tentar vincular CadastroAluno existentes com Pessoa
        migrations.RunPython(
            code=backfill_cadastro_pessoa,
            reverse_code=migrations.RunPython.noop,
        ),
    ]


def backfill_cadastro_pessoa(apps, schema_editor):
    """
    Tenta vincular CadastroAluno existentes com Pessoa correspondente.
    
    Estratégia de matching (em ordem):
    1. (igreja, nome_exact, data_nascimento_exact)
    2. (igreja, nome_iexact, data_nascimento_exact)
    3. (igreja, nome_iexact, responsavel_iexact, telefone_exact)
    4. Manual (deixar pessoa_id = NULL para vinculação manual depois)
    
    Logs cada match em stdout para auditoria.
    """
    from school_biblica.models import CadastroAluno
    from secretaria.models import Pessoa
    import logging
    from django.db.models import Q
    
    logger = logging.getLogger(__name__)
    
    stats = {
        'total': 0,
        'vinculados': 0,
        'correspondencias_perfeitas': 0,
        'correspondencias_fuzzy': 0,
        'nao_encontrados': 0,
        'erros': 0,
    }
    
    print("\n🔄 Iniciando backfill de vinculação CadastroAluno <- Pessoa...")
    
    for cadastro in CadastroAluno.objects.select_related('igreja').all():
        stats['total'] += 1
        
        if cadastro.pessoa_id:
            logger.debug(f"  {cadastro.nome}: Já vinculado (pessoa_id={cadastro.pessoa_id})")
            stats['vinculados'] += 1
            continue
        
        try:
            nome_norm = (cadastro.nome or '').strip().lower()
            
            # Estratégia 1: Exact match (nome case-sensitive, data)
            if cadastro.data_nascimento:
                pessoa = Pessoa.objects.filter(
                    igreja=cadastro.igreja,
                    nome__iexact=nome_norm,
                    nascimento=cadastro.data_nascimento,
                    registros_ebd__isnull=True,  # Evita multi-vinculação
                ).select_for_update().first()
                
                if pessoa:
                    cadastro.pessoa = pessoa
                    cadastro.save()
                    stats['correspondencias_perfeitas'] += 1
                    print(f"  ✅ {cadastro.nome}: Vinculado (match perfeito: nome + data)")
                    continue
            
            # Estratégia 2: Fuzzy match (responsável + telefone)
            if cadastro.responsavel or cadastro.telefone_responsavel:
                q = Q(igreja=cadastro.igreja, nome__iexact=nome_norm)
                
                if cadastro.responsavel:
                    q &= Q(nome_pai__iexact=cadastro.responsavel) | Q(
                        nome_mae__iexact=cadastro.responsavel
                    )
                
                if cadastro.telefone_responsavel:
                    q &= Q(telefone__exact=cadastro.telefone_responsavel) | Q(
                        celular__exact=cadastro.telefone_responsavel
                    )
                
                pessoa = Pessoa.objects.filter(q).select_for_update().first()
                
                if pessoa:
                    cadastro.pessoa = pessoa
                    cadastro.save()
                    stats['correspondencias_fuzzy'] += 1
                    print(f"  🔗 {cadastro.nome}: Vinculado (match fuzzy: nome + responsável)")
                    continue
            
            # Nenhuma correspondência encontrada
            stats['nao_encontrados'] += 1
            print(f"  ⚠️  {cadastro.nome}: Sem correspondência em Secretaria")
        
        except Exception as e:
            stats['erros'] += 1
            logger.error(f"  ❌ {cadastro.nome}: Erro ao vincular: {e}", exc_info=True)
    
    print(f"\n📊 RESULTADO DO BACKFILL:")
    print(f"  Total processados: {stats['total']}")
    print(f"  ✅ Vinculados (match perfeito): {stats['correspondencias_perfeitas']}")
    print(f"  🔗 Vinculados (match fuzzy): {stats['correspondencias_fuzzy']}")
    print(f"  ⚠️  Não encontrados: {stats['nao_encontrados']}")
    print(f"  ❌ Erros: {stats['erros']}")
    print(f"  📈 Taxa de sucesso: {((stats['correspondencias_perfeitas'] + stats['correspondencias_fuzzy']) / stats['total'] * 100):.1f}%")
```

---

## PARTE 3: MODIFICAÇÕES EM MODELS.PY

**Arquivo**: `escola_biblica/models.py`

```python
# Adicionar imports
from secretaria.models import Pessoa

class CadastroAluno(models.Model):
    """Cadastro mestre do aluno na EBD, independente do ano/turma."""
    
    # NOVOS CAMPOS + RELACIONAMENTOS
    pessoa = models.ForeignKey(
        Pessoa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registros_ebd',
        verbose_name='Pessoa (Secretaria)',
        help_text='Vinculação opcional com registro em Secretaria. Se vinculado, dados são sincronizados.'
    )
    
    # CAMPOS EXISTENTES (mantidos)
    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.PROTECT,
        related_name='cadastros_alunos_ebd',
        verbose_name='Igreja',
    )
    nome = models.CharField(max_length=150)
    data_nascimento = models.DateField(null=True, blank=True)
    responsavel = models.CharField(max_length=150, blank=True)
    telefone_responsavel = models.CharField(max_length=20, blank=True)
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        indexes = [
            models.Index(fields=['igreja', 'nome']),
            models.Index(fields=['ativo']),
            models.Index(fields=['pessoa']),  # NEW: Para queries de vinculação
        ]
        verbose_name = 'Cadastro de Aluno EBD'
        verbose_name_plural = 'Cadastros de Alunos EBD'

    def __str__(self):
        if self.pessoa:
            return f"{self.nome} (vinculado a Secretaria)"
        return self.nome
    
    def get_dados_completos(self):
        """Retorna dados completos: de Pessoa se vinculado, senão do CadastroAluno"""
        if self.pessoa:
            return {
                'nome': self.pessoa.nome,
                'data_nascimento': self.pessoa.nascimento,
                'email': self.pessoa.email,
                'telefone': self.pessoa.celular or self.pessoa.telefone,
                'tipo_pessoa': self.pessoa.tipo_pessoa.nome if self.pessoa.tipo_pessoa else None,
                'status': self.pessoa.status_pessoa.nome if self.pessoa.status_pessoa else None,
                'grupo_casa': self.pessoa.grupo_casa,
            }
        return {
            'nome': self.nome,
            'data_nascimento': self.data_nascimento,
            'email': None,
            'telefone': self.telefone_responsavel,
            'tipo_pessoa': None,
            'status': 'Ativo' if self.ativo else 'Inativo',
            'grupo_casa': None,
        }

    def tentar_vincular_pessoa(self, force=False):
        """
        Tenta encontrar e vincular uma Pessoa correspondente.
        
        Args:
            force: Se True, ignora vinculação existente
            
        Returns:
            Pessoa se encontrada e vinculada, None caso contrário
        """
        if self.pessoa_id and not force:
            return self.pessoa
        
        from django.db.models import Q
        from unidecode import unidecode
        
        def normalize(s):
            """Remove acentos e normaliza para comparação"""
            return unidecode((s or '').strip()).lower()
        
        nome_norm = normalize(self.nome)
        
        # Query base
        qs = Pessoa.objects.filter(
            igreja=self.igreja,
            status_pessoa__nome='Ativo'  # Apenas Pessoas ativas
        )
        
        # Tentativa 1: Nome + nascimento exato
        if self.data_nascimento:
            pessoa = qs.filter(
                nome__iexact=nome_norm,
                nascimento=self.data_nascimento
            ).select_for_update().first()
            
            if pessoa and not pessoa.registros_ebd.filter(
                pessoa_id__isnull=False
            ).exists():
                return pessoa
        
        # Tentativa 2: Nome + responsável + telefone
        if self.responsavel:
            responsavel_norm = normalize(self.responsavel)
            pessoa = qs.filter(
                nome__iexact=nome_norm,
            ).filter(
                Q(nome_pai__iexact=responsavel_norm) |
                Q(nome_mae__iexact=responsavel_norm)
            ).select_for_update().first()
            
            if pessoa:
                return pessoa
        
        return None
    
    def save(self, *args, **kwargs):
        # Tentar auto-vincular se não vinculado
        if not self.pessoa_id:
            pessoa_candidata = self.tentar_vincular_pessoa()
            if pessoa_candidata:
                self.pessoa = pessoa_candidata
        
        # Sincronizar dados de Pessoa se vinculado
        if self.pessoa:
            self.nome = self.pessoa.nome
            self.data_nascimento = self.pessoa.nascimento
            # Note: Mantém responsavel/telefone_responsavel da EBD
            # para casos onde conhecemos dados locais
        
        super().save(*args, **kwargs)
    
    def get_matricula_atual(self):
        return self.matriculas.select_related('turma', 'turma__ano_letivo').order_by(
            '-ativo', '-turma__ano_letivo__ano', '-updated_at', '-id'
        ).first()
```

---

## PARTE 4: MODIFICAÇÕES EM ADMIN.PY

**Arquivo**: `escola_biblica/admin.py`

```python
from django.contrib import admin
from .models import CadastroAluno, Aluno

@admin.register(CadastroAluno)
class CadastroAlunoAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'pessoa_link',  # NEW
        'igreja',
        'ativo',
        'created_at'
    )
    list_filter = (
        'ativo',
        'igreja',
        ('pessoa', admin.RelatedOnlyFieldListFilter),  # NEW: Filtro por vinculação
    )
    search_fields = (
        'nome',
        'pessoa__nome',  # NEW: Buscar por Pessoa
        'responsavel'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'pessoa_info',  # NEW: Info da Pessoa se vinculada
    )
    
    fieldsets = (
        ('Vinculação com Secretaria', {
            'fields': ('pessoa', 'pessoa_info'),
            'description': 'Se vinculado a uma Pessoa, os dados serão sincronizados automaticamente.',
            'classes': ('collapse',)
        }),
        ('Dados do Aluno EBD', {
            'fields': ('nome', 'data_nascimento', 'igreja', 'ativo')
        }),
        ('Responsável (Local EBD)', {
            'fields': ('responsavel', 'telefone_responsavel', 'observacoes')
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def pessoa_link(self, obj):
        """Mostra link para Pessoa se vinculada"""
        if obj.pessoa:
            url = f"/admin/secretaria/pessoa/{obj.pessoa.chave}/change/"
            return format_html(
                '<a href="{}">{}</a> ✅',
                url,
                obj.pessoa.nome
            )
        return "—"
    pessoa_link.short_description = 'Pessoa (Secretaria)'
    
    def pessoa_info(self, obj):
        """Informações detalhadas da Pessoa vincul da"""
        if not obj.pessoa:
            return "Não vinculado a pessoa em Secretaria"
        
        p = obj.pessoa
        info = f"""
        <strong>Nome:</strong> {p.nome}<br>
        <strong>Email:</strong> {p.email or '—'}<br>
        <strong>Telefone:</strong> {p.celular or p.telefone or '—'}<br>
        <strong>Tipo:</strong> {p.tipo_pessoa.nome if p.tipo_pessoa else '—'}<br>
        <strong>Status:</strong> {p.status_pessoa.nome if p.status_pessoa else '—'}<br>
        <strong>Grupo/Casa:</strong> {p.grupo_casa or '—'}<br>
        <strong>Cadastro em Secretaria:</strong> {p.criado_em:%d/%m/%Y}
        """
        return format_html(info)
    pessoa_info.short_description = 'Informações da Pessoa Vinculada'
    
    # NEW: Action para vincular alunos manualmente
    def vincular_pessoa_action(self, request, queryset):
        """Action para tentar vincular selecionados"""
        vinculados = 0
        nao_encontrados = []
        
        for cadastro in queryset:
            pessoa = cadastro.tentar_vincular_pessoa()
            if pessoa:
                cadastro.pessoa = pessoa
                cadastro.save()
                vinculados += 1
            else:
                nao_encontrados.append(cadastro.nome)
        
        self.message_user(
            request,
            f"✅ {vinculados} cadastros vinculados. "
            f"{'⚠️ ' + str(len(nao_encontrados)) + ' não encontrados.' if nao_encontrados else ''}",
            messages.SUCCESS if vinculados > 0 else messages.WARNING
        )
    vincular_pessoa_action.short_description = "🔗 Tentar vincular com Pessoa"
    
    actions = ['vincular_pessoa_action']


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    # ... existing fields ...
    list_display = (
        'nome',
        'cadastro',  # MOSTRAR CADASTRO MASTER
        'cadastro_pessoa',  # NEW: Mostrar Pessoa linkada
        'turma',
        'ativo',
    )
    
    def cadastro_pessoa(self, obj):
        """Mostra Pessoa se CadastroAluno está vinculado"""
        if obj.cadastro and obj.cadastro.pessoa:
            return format_html(
                '<span style="color: green;">✅ {}</span>',
                obj.cadastro.pessoa.nome
            )
        return "—"
    cadastro_pessoa.short_description = 'Pessoa (Secretaria)'
```

---

## PARTE 5: TESTES

**Arquivo**: `escola_biblica/tests/test_cadastro_pessoa_link.py`

```python
from django.test import TestCase
from escola_biblica.models import CadastroAluno
from secretaria.models import Pessoa, StatusPessoa, TipoPessoa, Igreja
from datetime import date
from django.utils import timezone


class CadastroAlunoPessoaLinkTestCase(TestCase):
    """Testes para vinculação CadastroAluno ↔ Pessoa"""
    
    @classmethod
    def setUpTestData(cls):
        cls.status_ativo = StatusPessoa.objects.create(nome='Ativo')
        cls.tipo_membro = TipoPessoa.objects.create(nome='Membro')
        cls.igreja = Igreja.objects.create(nome_igreja="Igreja Teste", sigla="IT")
    
    def test_cadastro_aluno_vincula_pessoa_match_exato(self):
        """Deve vincular se encontrar Pessoa com nome e data exatos"""
        pessoa = Pessoa.objects.create(
            nome="João Silva",
            nascimento=date(2010, 1, 1),
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
            igreja=self.igreja
        )
        
        cadastro = CadastroAluno(
            nome="João Silva",
            data_nascimento=date(2010, 1, 1),
            igreja=self.igreja
        )
        cadastro.save()
        
        # Deve ter auto-vinculado
        self.assertIsNotNone(cadastro.pessoa)
        self.assertEqual(cadastro.pessoa.nome, "João Silva")
    
    def test_cadastro_aluno_nao_vincula_pessoa_diferente(self):
        """Não deve vincular se dados não correspondem"""
        pessoa = Pessoa.objects.create(
            nome="Maria Silva",
            nascimento=date(2010, 1, 1),
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
            igreja=self.igreja
        )
        
        cadastro = CadastroAluno(
            nome="João Silva",  # Nome diferente
            data_nascimento=date(2010, 1, 1),
            igreja=self.igreja
        )
        cadastro.save()
        
        # Não deve ter vinculado
        self.assertIsNone(cadastro.pessoa)
    
    def test_cadastro_aluno_sincroniza_nome_de_pessoa(self):
        """Se vinculado, nome deve sincronizar de Pessoa"""
        pessoa = Pessoa.objects.create(
            nome="João Silva",
            nascimento=date(2010, 1, 1),
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
            igreja=self.igreja
        )
        
        cadastro = CadastroAluno.objects.create(
            nome="João Siva",  # Typo
            data_nascimento=date(2010, 1, 1),
            pessoa=pessoa,
            igreja=self.igreja
        )
        
        # Depois de salvar, deve ter sincronizado
        cadastro.save()
        cadastro.refresh_from_db()
        self.assertEqual(cadastro.nome, "João Silva")
    
    def test_get_dados_completos_de_pessoa(self):
        """get_dados_completos() deve retornar dados de Pessoa se vinculado"""
        pessoa = Pessoa.objects.create(
            nome="João Silva",
            nascimento=date(2010, 1, 1),
            email="joao@example.com",
            celular="11999999999",
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
            igreja=self.igreja
        )
        
        cadastro = CadastroAluno.objects.create(
            nome="João Silva",
            data_nascimento=date(2010, 1, 1),
            pessoa=pessoa,
            igreja=self.igreja
        )
        
        dados = cadastro.get_dados_completos()
        self.assertEqual(dados['email'], "joao@example.com")
        self.assertEqual(dados['telefone'], "11999999999")
        self.assertEqual(dados['tipo_pessoa'], "Membro")
```

---

## PARTE 6: QUERIES DE TESTE

```sql
-- Descobrir alunos vinculados a Pessoa
SELECT 
    ca.id, ca.nome, ca.data_nascimento,
    p.chave, p.nome as pessoa_nome
FROM escola_biblica_cadastroaluno ca
LEFT JOIN secretaria_pessoa p ON ca.pessoa_id = p.chave
WHERE ca.pessoa_id IS NOT NULL
ORDER BY ca.nome;

-- Descobrir alunos NÃO vincul ados
SELECT 
    ca.id, ca.nome, 
    COUNT(a.id) as matriculas_ativas
FROM escola_biblica_cadastroaluno ca
LEFT JOIN escola_biblica_aluno a ON ca.id = a.cadastro_id AND a.ativo = true
WHERE ca.pessoa_id IS NULL
GROUP BY ca.id
ORDER BY matriculas_ativas DESC;

-- Encontrar Pessoa que poderia ser vinculada (mas não foi auto-linkada)
SELECT 
    p.chave, p.nome, p.nascimento,
    ca.id as cadastro_id_possivel
FROM secretaria_pessoa p
LEFT JOIN escola_biblica_cadastroaluno ca 
    ON p.nome = ca.nome 
    AND p.nascimento = ca.data_nascimento
    AND p.igreja_id = ca.igreja_id
WHERE LOWER(p.nome) LIKE '%joão%'
  AND ca.id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM escola_biblica_cadastroaluno ca2 
    WHERE ca2.pessoa_id = p.chave
  );
```

---

## PARTE 7: PLANNING & ROLLOUT

### Sprint Planning

| Item | Estimativa | Responsável |
|------|-----------|-------------|
| Criar migration 0022 | 0.5d | Dev |
| Implementar auto-linking logic | 1d | Dev |
| Atualizar Admin | 0.5d | Dev |
| Escrever testes | 1d | QA/Dev |
| Executar backfill em DEV | 0.5d | Dev |
| Review & ajustesde migrations | 0.5d | Tech Lead |
| **Total Fase 1** | **3.5-4d** | |

### Rollout Checklist

- [ ] Migration 0022 testada em DEV
- [ ] Tests passando (100% cobertura)
- [ ] Backfill executado e validado
- [ ] Admin funcionando
- [ ] Documentação atualizada
- [ ] Code review aprovado
- [ ] Deploy para STAGING
- [ ] Smoke test em STAGING
- [ ] Deploy para PROD (backup antes!)
- [ ] Monitoramento de erros pós-deploy
- [ ] Relatório de sucesso (% vinculado, etc)

---

**Documento**: Guia Técnico de Implementação  
**Data**: 13/04/2026  
**Status**: Pronto para `git commit`
