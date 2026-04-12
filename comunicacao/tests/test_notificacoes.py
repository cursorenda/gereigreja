from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from contas.constants import MEMBRO_COMUM
from comunicacao.models import Notificacao
from configuracao.models import Ministerio, PerfilUsuario


class NotificacoesViewsTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

        self.admin_user = self.User.objects.create_user(
            username='admin_ministerio',
            email='admin@example.com',
            password='12345678',
        )
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Teste',
            administrador_principal=self.admin_user,
            ativo=True,
        )

        self.user = self.User.objects.create_user(
            username='usuario_teste',
            email='user@example.com',
            password='12345678',
        )
        PerfilUsuario.objects.create(user=self.user, ministerio=self.ministerio)

        self.other_user = self.User.objects.create_user(
            username='outro_usuario',
            email='other@example.com',
            password='12345678',
        )
        PerfilUsuario.objects.create(user=self.other_user, ministerio=self.ministerio)

        grupo_membro_comum, _ = Group.objects.get_or_create(name=MEMBRO_COMUM)
        self.user.groups.add(grupo_membro_comum)
        self.other_user.groups.add(grupo_membro_comum)

    def test_marcar_todas_notificacoes_lidas_atualiza_apenas_usuario_logado(self):
        Notificacao.objects.create(
            user=self.user,
            ministerio=self.ministerio,
            message='n1',
            notification_type='info',
            is_read=False,
        )
        Notificacao.objects.create(
            user=self.user,
            ministerio=self.ministerio,
            message='n2',
            notification_type='financeiro',
            is_read=False,
        )
        Notificacao.objects.create(
            user=self.user,
            ministerio=self.ministerio,
            message='n3',
            notification_type='aviso',
            is_read=True,
        )
        Notificacao.objects.create(
            user=self.other_user,
            ministerio=self.ministerio,
            message='outra pessoa',
            notification_type='info',
            is_read=False,
        )

        self.client.force_login(self.user)
        response = self.client.post(reverse('comunicacao:marcar_todas_notificacoes_lidas'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('comunicacao:lista_notificacoes'))

        self.assertEqual(
            Notificacao.objects.filter(user=self.user, ministerio=self.ministerio, is_read=False).count(),
            0,
        )
        self.assertEqual(
            Notificacao.objects.filter(user=self.other_user, ministerio=self.ministerio, is_read=False).count(),
            1,
        )

    def test_marcar_todas_notificacoes_lidas_rejeita_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('comunicacao:marcar_todas_notificacoes_lidas'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('comunicacao:lista_notificacoes'))
