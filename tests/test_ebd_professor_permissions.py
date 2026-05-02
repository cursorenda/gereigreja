"""
Testes de Permissões para Professores EBD - v1.2.2

Testa o sistema de permissões granulares onde professores podem:
- Acessar chamada de presença de suas turmas
- Ver lista de suas turmas
- Ver alunos de suas turmas
- Ver detalhes de alunos de suas turmas

Mas NÃO podem:
- Acessar turmas de outros professores
- Ver alunos de turmas que não lecionam
- Criar/editar/excluir turmas (exclusivo secretaria)
- Transferir alunos (exclusivo secretaria)
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from datetime import date, timedelta, datetime
from django.utils import timezone
from unittest.mock import patch

from escola_biblica.models import (
    Turma, Aluno, Classe, AnoLetivo, PeriodoEBD, Departamento
)
from secretaria.models import Membro, Cargo, MembroCargo, TipoPessoa, StatusPessoa
from configuracao.models import (
    PerfilUsuario, Ministerio, Igreja, AssinaturaMinisterio, Plano
)
from escola_biblica.views import (
    pode_acessar_chamada_turma, 
    get_turmas_professor, 
    pode_ver_aluno
)


# Decorator helper para bypassar verificação de assinatura em testes
def bypass_assinatura_check(test_class):
    """
    Bypassa o decorator @verificar_assinatura_valida em testes.
    
    Isso permite testar permissões de professores sem se preocupar
    com a infraestrutura de billing/assinatura.
    """
    return patch('core.decorators.verificar_assinatura_valida', 
                 lambda func: func)(test_class)


@bypass_assinatura_check
@override_settings(
    # Remove ActiveChurchMiddleware para simplificar testes
    # Views EBD não dependem obrigatoriamente de request.igreja_ativa
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
)
class ProfessorPermissionsTestCase(TestCase):
    """Testes completos de permissões para professores EBD."""
    
    @classmethod
    def setUpTestData(cls):
        """Configuração inicial de dados para todos os testes."""
        
        # Criação de grupos
        cls.grupo_secretaria = Group.objects.create(name='Secretaria EBD')
        cls.grupo_superintendente = Group.objects.create(name='Superintendente EBD')
        cls.grupo_pastor = Group.objects.create(name='Pastor Local')
        
        # Criação de usuário admin para o ministério
        cls.admin_user = User.objects.create_user(
            username='admin',
            password='senha123',
            email='admin@teste.com'
        )
        
        # Criação de ministério
        cls.ministerio = Ministerio.objects.create(
            nome_fantasia='Igreja Teste',
            administrador_principal=cls.admin_user,
            ativo=True
        )
        
        # Criação de plano e assinatura ativa para o ministério
        cls.plano_basico = Plano.objects.create(
            nome='pioneiro',
            preco_mensal=50.00,
            limite_membros=100,
            limite_igrejas=5
        )
        cls.assinatura = AssinaturaMinisterio.objects.create(
            ministerio=cls.ministerio,
            plano=cls.plano_basico,
            status='ativa',
            data_inicio=timezone.now() - timedelta(days=30),
            data_fim=timezone.now() + timedelta(days=30)
        )
        
        cls.igreja = Igreja.objects.create(
            nome_igreja='Congregação Central',
            ministerio=cls.ministerio
        )
        
        # Criação de tipo e status de pessoa (obrigatórios)
        cls.tipo_membro = TipoPessoa.objects.create(nome='Membro')
        cls.status_ativo = StatusPessoa.objects.create(nome='Ativo')
        
        # Criação de cargo de professor EBD
        cls.cargo_professor = Cargo.objects.create(
            nome='Professor EBD',
            is_ebd=True
        )
        cls.cargo_secretaria_ebd = Cargo.objects.create(
            nome='Secretário EBD',
            is_ebd=True
        )
        
        # Criação de ano letivo e período
        cls.ano_letivo = AnoLetivo.objects.create(ano=date.today().year, ativo=True)
        cls.periodo = PeriodoEBD.objects.create(
            ano_letivo=cls.ano_letivo,
            numero=1,
            tipo='trimestre',
            data_inicio=date.today(),
            data_fim=date.today() + timedelta(days=90)
        )
        
        # Criação de departamento e classe
        cls.departamento = Departamento.objects.create(nome='Adultos')
        cls.classe = Classe.objects.create(
            nome='Adultos I',
            departamento='ADULTO',
            faixa_etaria='Adultos'
        )
        
        # Criação de usuários e perfis
        # 1. Professor da Turma A
        cls.user_professor_a = User.objects.create_user(
            username='professor_a',
            password='senha123',
            email='prof_a@teste.com'
        )
        cls.perfil_professor_a = PerfilUsuario.objects.create(
            user=cls.user_professor_a,
            ministerio=cls.ministerio
        )
        cls.membro_professor_a = Membro.objects.create(
            nome='Professor A',
            email='prof_a@teste.com',
            igreja=cls.igreja,
            tipo_pessoa=cls.tipo_membro,
            status_pessoa=cls.status_ativo,
            usuario=cls.user_professor_a  # Vincula User ao Membro (relacionamento correto)
        )
        # Nota: PerfilUsuario não tem campo 'membro', remover essa linha
        # cls.perfil_professor_a.membro = cls.membro_professor_a
        # cls.perfil_professor_a.save()
        
        # Vincula cargo de professor EBD ao membro A
        cls.cargo_ativo_a = MembroCargo.objects.create(
            membro=cls.membro_professor_a,
            cargo=cls.cargo_professor,
            data_inicio=date.today() - timedelta(days=30),
            data_fim=None  # Cargo ativo
        )
        
        # 2. Professor da Turma B
        cls.user_professor_b = User.objects.create_user(
            username='professor_b',
            password='senha123',
            email='prof_b@teste.com'
        )
        cls.perfil_professor_b = PerfilUsuario.objects.create(
            user=cls.user_professor_b,
            ministerio=cls.ministerio
        )
        cls.membro_professor_b = Membro.objects.create(
            nome='Professor B',
            email='prof_b@teste.com',
            igreja=cls.igreja,
            tipo_pessoa=cls.tipo_membro,
            status_pessoa=cls.status_ativo,
            usuario=cls.user_professor_b  # Vincula User ao Membro
        )
        # Nota: PerfilUsuario não tem campo 'membro', remover essa linha
        # cls.perfil_professor_b.membro = cls.membro_professor_b
        # cls.perfil_professor_b.save()
        
        # Vincula cargo de professor EBD ao membro B
        cls.cargo_ativo_b = MembroCargo.objects.create(
            membro=cls.membro_professor_b,
            cargo=cls.cargo_professor,
            data_inicio=date.today() - timedelta(days=30),
            data_fim=None
        )
        
        # 3. Secretário EBD
        cls.user_secretario = User.objects.create_user(
            username='secretario',
            password='senha123',
            email='secretario@teste.com'
        )
        cls.user_secretario.groups.add(cls.grupo_secretaria)
        cls.perfil_secretario = PerfilUsuario.objects.create(
            user=cls.user_secretario,
            ministerio=cls.ministerio
        )
        
        # 4. Usuário comum (sem permissões EBD)
        cls.user_comum = User.objects.create_user(
            username='comum',
            password='senha123',
            email='comum@teste.com'
        )
        cls.perfil_comum = PerfilUsuario.objects.create(
            user=cls.user_comum,
            ministerio=cls.ministerio
        )
        
        # Criação de turmas
        cls.turma_a = Turma.objects.create(
            nome='Turma Adultos A',
            classe=cls.classe,
            ano_letivo=cls.ano_letivo
        )
        cls.turma_a.membros.add(cls.membro_professor_a)  # Professor A leciona turma A
        
        cls.turma_b = Turma.objects.create(
            nome='Turma Adultos B',
            classe=cls.classe,
            ano_letivo=cls.ano_letivo
        )
        cls.turma_b.membros.add(cls.membro_professor_b)  # Professor B leciona turma B
        
        # Criação de alunos
        cls.aluno_turma_a = Aluno.objects.create(
            nome='Aluno da Turma A',
            turma=cls.turma_a,
            ativo=True
        )
        cls.aluno_turma_b = Aluno.objects.create(
            nome='Aluno da Turma B',
            turma=cls.turma_b,
            ativo=True
        )
    
    def setUp(self):
        """Configuração antes de cada teste."""
        self.client = Client()
        
        # Força refresh dos users para garantir que perfil está acessível
        self.user_professor_a.refresh_from_db()
        self.user_professor_b.refresh_from_db()
        self.user_secretario.refresh_from_db()
        self.user_comum.refresh_from_db()
        
        # Configura igreja_ativa_id na sessão para simular middleware
        # Isso é necessário porque várias views filtram por request.igreja_ativa
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja.pk
        session.save()
    
    # ========== TESTES DE FUNÇÕES HELPER ==========
    
    def test_pode_acessar_chamada_turma_professor_propria_turma(self):
        """Professor A pode acessar chamada da própria turma (Turma A)."""
        pode_acessar = pode_acessar_chamada_turma(self.user_professor_a, self.turma_a)
        self.assertTrue(pode_acessar)
    
    def test_nao_pode_acessar_chamada_turma_outro_professor(self):
        """Professor A NÃO pode acessar chamada da turma de outro professor (Turma B)."""
        pode_acessar = pode_acessar_chamada_turma(self.user_professor_a, self.turma_b)
        self.assertFalse(pode_acessar)
    
    def test_secretario_pode_acessar_todas_turmas(self):
        """Secretário EBD pode acessar chamada de qualquer turma."""
        pode_acessar_a = pode_acessar_chamada_turma(self.user_secretario, self.turma_a)
        pode_acessar_b = pode_acessar_chamada_turma(self.user_secretario, self.turma_b)
        self.assertTrue(pode_acessar_a)
        self.assertTrue(pode_acessar_b)
    
    def test_usuario_comum_nao_pode_acessar_chamada(self):
        """Usuário comum NÃO pode acessar chamada de nenhuma turma."""
        pode_acessar = pode_acessar_chamada_turma(self.user_comum, self.turma_a)
        self.assertFalse(pode_acessar)
    
    def test_get_turmas_professor_retorna_apenas_suas_turmas(self):
        """get_turmas_professor retorna apenas turmas do professor específico."""
        turmas_a = get_turmas_professor(self.user_professor_a)
        turmas_b = get_turmas_professor(self.user_professor_b)
        
        self.assertIn(self.turma_a, turmas_a)
        self.assertNotIn(self.turma_b, turmas_a)
        
        self.assertIn(self.turma_b, turmas_b)
        self.assertNotIn(self.turma_a, turmas_b)
    
    def test_get_turmas_professor_usuario_comum_retorna_vazio(self):
        """get_turmas_professor retorna queryset vazio para usuário sem cargo."""
        turmas = get_turmas_professor(self.user_comum)
        self.assertEqual(turmas.count(), 0)
    
    def test_pode_ver_aluno_professor_da_turma(self):
        """Professor pode ver aluno de sua própria turma."""
        pode_ver = pode_ver_aluno(self.user_professor_a, self.aluno_turma_a)
        self.assertTrue(pode_ver)
    
    def test_nao_pode_ver_aluno_outra_turma(self):
        """Professor NÃO pode ver aluno de turma de outro professor."""
        pode_ver = pode_ver_aluno(self.user_professor_a, self.aluno_turma_b)
        self.assertFalse(pode_ver)
    
    def test_secretario_pode_ver_todos_alunos(self):
        """Secretário EBD pode ver alunos de qualquer turma."""
        pode_ver_a = pode_ver_aluno(self.user_secretario, self.aluno_turma_a)
        pode_ver_b = pode_ver_aluno(self.user_secretario, self.aluno_turma_b)
        self.assertTrue(pode_ver_a)
        self.assertTrue(pode_ver_b)
    
    # ========== TESTES DE VIEWS ==========
    
    def test_chamada_presenca_view_professor_propria_turma(self):
        """Professor pode acessar view de chamada de sua turma (200 OK)."""
        self.client.login(username='professor_a', password='senha123')
        url = reverse('escola_biblica:chamada_presenca', kwargs={'turma_id': self.turma_a.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_chamada_presenca_view_professor_turma_alheia(self):
        """Professor recebe 403 ao tentar acessar chamada de turma alheia."""
        self.client.login(username='professor_a', password='senha123')
        url = reverse('escola_biblica:chamada_presenca', kwargs={'turma_id': self.turma_b.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
    
    def test_chamada_presenca_view_secretario_qualquer_turma(self):
        """Secretário pode acessar view de chamada de qualquer turma."""
        self.client.login(username='secretario', password='senha123')
        
        url_a = reverse('escola_biblica:chamada_presenca', kwargs={'turma_id': self.turma_a.id})
        url_b = reverse('escola_biblica:chamada_presenca', kwargs={'turma_id': self.turma_b.id})
        
        response_a = self.client.get(url_a)
        response_b = self.client.get(url_b)
        
        self.assertEqual(response_a.status_code, 200)
        self.assertEqual(response_b.status_code, 200)
    
    def test_turma_list_view_professor_ve_apenas_suas_turmas(self):
        """Professor vê apenas suas turmas na listagem."""
        self.client.login(username='professor_a', password='senha123')
        url = reverse('escola_biblica:turma_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Verifica contexto da resposta
        turmas_listadas = response.context.get('turmas')
        if turmas_listadas:
            turmas_ids = [t.id for t in turmas_listadas]
            self.assertIn(self.turma_a.id, turmas_ids)
            self.assertNotIn(self.turma_b.id, turmas_ids)
    
    def test_turma_list_view_secretario_ve_todas_turmas(self):
        """Secretário vê todas as turmas na listagem."""
        self.client.login(username='secretario', password='senha123')
        url = reverse('escola_biblica:turma_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        turmas_listadas = response.context.get('turmas')
        if turmas_listadas:
            turmas_ids = [t.id for t in turmas_listadas]
            self.assertIn(self.turma_a.id, turmas_ids)
            self.assertIn(self.turma_b.id, turmas_ids)
    
    def test_aluno_list_view_professor_ve_apenas_seus_alunos(self):
        """Professor vê apenas alunos de suas turmas na listagem."""
        self.client.login(username='professor_a', password='senha123')
        url = reverse('escola_biblica:aluno_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        alunos_listados = response.context.get('alunos')
        if alunos_listados:
            alunos_ids = [a.id for a in alunos_listados]
            self.assertIn(self.aluno_turma_a.id, alunos_ids)
            self.assertNotIn(self.aluno_turma_b.id, alunos_ids)
    
    def test_aluno_list_view_secretario_ve_todos_alunos(self):
        """Secretário vê todos os alunos na listagem."""
        self.client.login(username='secretario', password='senha123')
        url = reverse('escola_biblica:aluno_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        alunos_listados = response.context.get('alunos')
        if alunos_listados:
            alunos_ids = [a.id for a in alunos_listados]
            self.assertIn(self.aluno_turma_a.id, alunos_ids)
            self.assertIn(self.aluno_turma_b.id, alunos_ids)
    
    def test_aluno_detail_view_professor_seu_aluno(self):
        """Professor pode ver detalhes de aluno de sua turma."""
        self.client.login(username='professor_a', password='senha123')
        url = reverse('escola_biblica:aluno_detail', kwargs={'pk': self.aluno_turma_a.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_aluno_detail_view_professor_aluno_alheio(self):
        """Professor recebe 403 ao tentar ver detalhes de aluno de turma alheia."""
        self.client.login(username='professor_a', password='senha123')
        url = reverse('escola_biblica:aluno_detail', kwargs={'pk': self.aluno_turma_b.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
    
    # ========== TESTES DE EDGE CASES ==========
    
    def test_professor_sem_cargo_ativo_nao_acessa_turma(self):
        """Professor com cargo inativo NÃO pode acessar turma."""
        # Inativa o cargo do professor A
        self.cargo_ativo_a.data_fim = date.today() - timedelta(days=1)
        self.cargo_ativo_a.save()
        
        pode_acessar = pode_acessar_chamada_turma(self.user_professor_a, self.turma_a)
        self.assertFalse(pode_acessar)
        
        # Reativa para não afetar outros testes
        self.cargo_ativo_a.data_fim = None
        self.cargo_ativo_a.save()
    
    def test_professor_sem_perfil_membro_nao_acessa(self):
        """Professor sem perfil/membro vinculado NÃO pode acessar turma."""
        # Cria usuário sem perfil completo
        user_sem_perfil = User.objects.create_user(
            username='sem_perfil',
            password='senha123'
        )
        pode_acessar = pode_acessar_chamada_turma(user_sem_perfil, self.turma_a)
        self.assertFalse(pode_acessar)
    
    def test_superuser_acessa_todas_turmas(self):
        """Superuser pode acessar qualquer turma (bypass de permissões)."""
        superuser = User.objects.create_superuser(
            username='superadmin',
            password='senha123',
            email='superadmin@teste.com'
        )
        
        pode_acessar_a = pode_acessar_chamada_turma(superuser, self.turma_a)
        pode_acessar_b = pode_acessar_chamada_turma(superuser, self.turma_b)
        
        self.assertTrue(pode_acessar_a)
        self.assertTrue(pode_acessar_b)
    
    def test_usuario_nao_autenticado_redireciona_login(self):
        """Usuário não autenticado é redirecionado para login."""
        url = reverse('escola_biblica:chamada_presenca', kwargs={'turma_id': self.turma_a.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertIn('/login/', response.url)
    
    # ========== TESTES DE INTEGRIDADE ==========
    
    def test_views_protegidas_requerem_autenticacao(self):
        """Todas as views protegidas requerem autenticação."""
        urls_protegidas = [
            reverse('escola_biblica:turma_list'),
            reverse('escola_biblica:aluno_list'),
            reverse('escola_biblica:chamada_presenca', kwargs={'turma_id': self.turma_a.id}),
            reverse('escola_biblica:aluno_detail', kwargs={'pk': self.aluno_turma_a.id}),
        ]
        
        for url in urls_protegidas:
            response = self.client.get(url)
            self.assertIn(response.status_code, [302, 403],
                         f"URL {url} deveria redirecionar ou negar acesso sem autenticação")


@bypass_assinatura_check
@override_settings(
    # Remove ActiveChurchMiddleware para simplificar testes
    # Views EBD não dependem obrigatoriamente de request.igreja_ativa
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
)
class ProfessorCRUDRestrictionsTestCase(TestCase):
    """Testa que professores NÃO podem criar/editar/excluir turmas/alunos."""
    
    @classmethod
    def setUpTestData(cls):
        """Setup básico para testes de restrições."""
        # Reutiliza setup básico do teste anterior
        # (simplificado para focar nas restrições)
        cls.grupo_secretaria = Group.objects.create(name='Secretaria EBD')
        
        # Criação de usuário admin para o ministério
        cls.admin_user = User.objects.create_user(
            username='admin',
            password='senha123',
            email='admin@teste.com'
        )
        
        cls.ministerio = Ministerio.objects.create(
            nome_fantasia='Igreja Teste',
            administrador_principal=cls.admin_user,
            ativo=True
        )
        
        # Criação de plano e assinatura ativa
        cls.plano_basico = Plano.objects.create(
            nome='pioneiro',
            preco_mensal=50.00,
            limite_membros=100,
            limite_igrejas=5
        )
        cls.assinatura = AssinaturaMinisterio.objects.create(
            ministerio=cls.ministerio,
            plano=cls.plano_basico,
            status='ativa',
            data_inicio=timezone.now() - timedelta(days=30),
            data_fim=timezone.now() + timedelta(days=30)
        )
        
        cls.igreja = Igreja.objects.create(
            nome_igreja='Congregação Central',
            ministerio=cls.ministerio
        )
        
        # Tipos e status
        cls.tipo_membro = TipoPessoa.objects.create(nome='Membro')
        cls.status_ativo = StatusPessoa.objects.create(nome='Ativo')
        
        cls.cargo_professor = Cargo.objects.create(
            nome='Professor EBD',
            is_ebd=True
        )
        
        cls.user_professor = User.objects.create_user(
            username='professor',
            password='senha123'
        )
        cls.perfil = PerfilUsuario.objects.create(
            user=cls.user_professor,
            ministerio=cls.ministerio
        )
        cls.membro = Membro.objects.create(
            nome='Professor Teste',
            igreja=cls.igreja,
            tipo_pessoa=cls.tipo_membro,
            status_pessoa=cls.status_ativo,
            usuario=cls.user_professor  # Vincula User ao Membro
        )
        # Nota: PerfilUsuario não tem campo 'membro', remover essa linha
        # cls.perfil.membro = cls.membro
        # cls.perfil.save()
        
        MembroCargo.objects.create(
            membro=cls.membro,
            cargo=cls.cargo_professor,
            data_inicio=date.today(),
            data_fim=None
        )
    
    def setUp(self):
        """Configuração antes de cada teste."""
        self.client = Client()
        
        # Refresh do user para garantir acesso ao perfil
        self.user_professor.refresh_from_db()
        
        # Configura igreja_ativa_id na sessão
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja.pk
        session.save()
    
    def test_professor_nao_pode_criar_turma(self):
        """Professor NÃO pode acessar view de criação de turma (403 esperado)."""
        self.client.login(username='professor', password='senha123')
        url = reverse('escola_biblica:turma_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
    
    def test_professor_nao_pode_editar_turma(self):
        """Professor NÃO pode acessar view de edição de turma (403 esperado)."""
        ano_letivo = AnoLetivo.objects.create(ano=date.today().year, ativo=True)
        classe = Classe.objects.create(nome='Adultos', departamento='ADULTO')
        turma = Turma.objects.create(
            nome='Turma Teste',
            classe=classe,
            ano_letivo=ano_letivo
        )
        
        self.client.login(username='professor', password='senha123')
        url = reverse('escola_biblica:turma_edit', kwargs={'pk': turma.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
    
    def test_professor_nao_pode_excluir_turma(self):
        """Professor NÃO pode acessar view de exclusão de turma (403 esperado)."""
        ano_letivo = AnoLetivo.objects.create(ano=date.today().year, ativo=True)
        classe = Classe.objects.create(nome='Adultos', departamento='ADULTO')
        turma = Turma.objects.create(
            nome='Turma Teste',
            classe=classe,
            ano_letivo=ano_letivo
        )
        
        self.client.login(username='professor', password='senha123')
        url = reverse('escola_biblica:turma_delete', kwargs={'pk': turma.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
    
    def test_professor_nao_pode_criar_aluno(self):
        """Professor NÃO pode acessar view de criação de aluno (403 esperado)."""
        self.client.login(username='professor', password='senha123')
        url = reverse('escola_biblica:aluno_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
