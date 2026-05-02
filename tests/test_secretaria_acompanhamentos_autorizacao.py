"""
Testes de autorização para acompanhamentos de visita.
Verifica que usuários só veem acompanhamentos e membros de igrejas permitidas.
"""
from datetime import date, datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from configuracao.models import Igreja, Ministerio, PerfilUsuario
from contas.constants import MEMBRO_COMUM, PASTOR_LOCAL
from django.utils import timezone
from secretaria.models import AcompanhamentoVisita, Membro, TipoPessoa, StatusPessoa


class AcompanhamentosAutorizacaoTest(TestCase):
    def setUp(self):
        user_model = get_user_model()

        # Criar admin principal
        self.user_admin = user_model.objects.create_user(
            username='admin_acomp_test',
            password='pass123',
        )
        
        # Criar dois pastores locais (um de cada igreja)
        self.user_local_Igreja_A = user_model.objects.create_user(
            username='pastor_local_A',
            password='pass123',
        )
        self.user_local_Igreja_B = user_model.objects.create_user(
            username='pastor_local_B',
            password='pass123',
        )

        # Criar ministério
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Acompanhamentos Teste',
            administrador_principal=self.user_admin,
            ativo=True,
        )

        # Criar duas igrejas
        self.igreja_A = Igreja.objects.create(
            nome_igreja='Igreja A - Acompanhamentos',
            ministerio=self.ministerio,
        )
        self.igreja_B = Igreja.objects.create(
            nome_igreja='Igreja B - Acompanhamentos',
            ministerio=self.ministerio,
        )

        # Associar perfis: pastor local A acessa só Igreja A, B acessa só Igreja B
        self.perfil_local_A = PerfilUsuario.objects.create(
            user=self.user_local_Igreja_A,
            ministerio=self.ministerio,
        )
        self.perfil_local_A.igrejas_permitidas.add(self.igreja_A)

        self.perfil_local_B = PerfilUsuario.objects.create(
            user=self.user_local_Igreja_B,
            ministerio=self.ministerio,
        )
        self.perfil_local_B.igrejas_permitidas.add(self.igreja_B)

        # Associar grupos
        self.grupo_pastor_local, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        self.user_local_Igreja_A.groups.add(self.grupo_pastor_local)
        self.user_local_Igreja_B.groups.add(self.grupo_pastor_local)

        # Criar tipo de pessoa
        self.tipo_pessoa = TipoPessoa.objects.create(
            nome='Visitante',
        )

        # Criar status de pessoa
        self.status_pessoa = StatusPessoa.objects.create(
            nome='Ativo',
        )

        # Criar membros em cada igreja
        self.membro_A = Membro.objects.create(
            nome='Membro Igreja A',
            tipo_pessoa=self.tipo_pessoa,
            status_pessoa=self.status_pessoa,
            igreja=self.igreja_A,
            data_entrada=date(2026, 1, 1),
        )
        self.membro_B = Membro.objects.create(
            nome='Membro Igreja B',
            tipo_pessoa=self.tipo_pessoa,
            status_pessoa=self.status_pessoa,
            igreja=self.igreja_B,
            data_entrada=date(2026, 1, 1),
        )

        # Criar acompanhamentos de visita para cada membro
        self.acompanhamento_A = AcompanhamentoVisita.objects.create(
            membro=self.membro_A,
            responsavel=self.user_local_Igreja_A,
            tipo_contato='visita',
            data=timezone.make_aware(datetime(2026, 4, 1, 10, 0, 0)),
            observacao='Visita membro A',
        )
        self.acompanhamento_B = AcompanhamentoVisita.objects.create(
            membro=self.membro_B,
            responsavel=self.user_local_Igreja_B,
            tipo_contato='visita',
            data=timezone.make_aware(datetime(2026, 4, 1, 10, 0, 0)),
            observacao='Visita membro B',
        )

    def test_lista_acompanhamentos_filtra_por_igrejas_permitidas(self):
        """Pastor Local de Igreja A não vê acompanhamentos de Igreja B."""
        self.client.force_login(self.user_local_Igreja_A)
        
        response = self.client.get(reverse('secretaria:acompanhamentos_visita'))
        
        self.assertEqual(response.status_code, 200)
        acompanhamentos = response.context['acompanhamentos']
        
        # Deve ver apenas acompanhamento de Igreja A
        ids = list(acompanhamentos.values_list('id', flat=True))
        self.assertIn(self.acompanhamento_A.id, ids)
        self.assertNotIn(self.acompanhamento_B.id, ids)

    def test_escolher_pessoa_filtra_por_igrejas_permitidas(self):
        """Pastor Local de Igreja A não vê membros de Igreja B."""
        self.client.force_login(self.user_local_Igreja_A)
        
        response = self.client.get(reverse('secretaria:escolher_pessoa_para_acompanhamento'))
        
        self.assertEqual(response.status_code, 200)
        pessoas = response.context['pessoas']
        
        # Deve ver apenas membro de Igreja A
        nomes = [p.nome for p in pessoas]
        self.assertIn(self.membro_A.nome, nomes)
        self.assertNotIn(self.membro_B.nome, nomes)

    def test_acompanhamentos_visita_bloqueado_sem_permissao(self):
        """Usuário com grupo reconhecido, mas sem permissão, recebe 403 na listagem."""
        user_model = get_user_model()
        user_sem_permissao = user_model.objects.create_user(
            username='membro_comum_sem_acesso_acomp',
            password='pass123',
        )
        perfil = PerfilUsuario.objects.create(
            user=user_sem_permissao,
            ministerio=self.ministerio,
        )
        perfil.igrejas_permitidas.add(self.igreja_A)
        grupo_membro_comum, _ = Group.objects.get_or_create(name=MEMBRO_COMUM)
        user_sem_permissao.groups.add(grupo_membro_comum)

        self.client.force_login(user_sem_permissao)
        response = self.client.get(reverse('secretaria:acompanhamentos_visita'))

        self.assertEqual(response.status_code, 403)

    def test_escolher_pessoa_bloqueado_sem_permissao(self):
        """Usuário com grupo reconhecido, mas sem permissão, recebe 403 ao escolher pessoa."""
        user_model = get_user_model()
        user_sem_permissao = user_model.objects.create_user(
            username='membro_comum_sem_acesso_pessoa',
            password='pass123',
        )
        perfil = PerfilUsuario.objects.create(
            user=user_sem_permissao,
            ministerio=self.ministerio,
        )
        perfil.igrejas_permitidas.add(self.igreja_A)
        grupo_membro_comum, _ = Group.objects.get_or_create(name=MEMBRO_COMUM)
        user_sem_permissao.groups.add(grupo_membro_comum)

        self.client.force_login(user_sem_permissao)
        response = self.client.get(reverse('secretaria:escolher_pessoa_para_acompanhamento'))

        self.assertEqual(response.status_code, 403)
