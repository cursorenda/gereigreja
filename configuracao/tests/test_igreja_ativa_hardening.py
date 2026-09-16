from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL, SECRETARIO_LOCAL
from configuracao.models import Igreja, Ministerio, PerfilUsuario
from core.middleware import ActiveChurchMiddleware
from core.utils import get_igrejas_selecionaveis
from financeiro.templatetags.financeiro_tags import get_churches_tree_ordered


class IgrejaAtivaHardeningTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user('admin-contexto')
        self.pastor = User.objects.create_user('pastor-contexto')
        self.secretario = User.objects.create_user('secretario-contexto')
        self.sem_escopo = User.objects.create_user('sem-escopo-contexto')
        self.outro_admin = User.objects.create_user('outro-admin-contexto')

        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Contexto',
            administrador_principal=self.admin,
            ativo=True,
        )
        self.outro_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministerio Contexto',
            administrador_principal=self.outro_admin,
            ativo=True,
        )
        self.sede = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Sede Contexto',
            tipo_igreja='sede',
        )
        self.local = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Local Contexto',
            tipo_igreja='regional',
            igreja_superior=self.sede,
        )
        self.subordinada = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Subordinada Contexto',
            igreja_superior=self.local,
        )
        self.cross_ministerio = Igreja.objects.create(
            ministerio=self.outro_ministerio,
            nome_igreja='Cross Ministerio',
        )

        admin_group, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        pastor_group, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        secretario_group, _ = Group.objects.get_or_create(name=SECRETARIO_LOCAL)
        self.admin.groups.add(admin_group)
        self.pastor.groups.add(pastor_group)
        self.secretario.groups.add(secretario_group)

        self.admin_perfil = PerfilUsuario.objects.create(user=self.admin, ministerio=self.ministerio)
        self.pastor_perfil = PerfilUsuario.objects.create(user=self.pastor, ministerio=self.ministerio)
        self.secretario_perfil = PerfilUsuario.objects.create(user=self.secretario, ministerio=self.ministerio)
        self.sem_escopo_perfil = PerfilUsuario.objects.create(user=self.sem_escopo, ministerio=self.ministerio)
        self.pastor_perfil.igrejas_permitidas.add(self.local)
        self.secretario_perfil.igrejas_permitidas.add(self.sede)
        self.url = reverse('configuracao:set_active_church')

    def _request(self, user, igreja_id=None):
        request = RequestFactory().get('/')
        request.user = user
        SessionMiddleware(lambda req: HttpResponse()).process_request(request)
        request.session.save()
        if igreja_id is not None:
            request.session['igreja_ativa_id'] = igreja_id
        return request

    def _run_middleware(self, request):
        ActiveChurchMiddleware(lambda req: HttpResponse())(request)
        return request

    def test_pastor_nao_recebe_subordinadas_implicitamente(self):
        self.assertQuerySetEqual(
            get_igrejas_selecionaveis(self.pastor).order_by('pk'),
            [self.local],
        )

    def test_secretario_respeita_somente_escopo_explicito(self):
        self.assertQuerySetEqual(get_igrejas_selecionaveis(self.secretario), [self.sede])

    def test_admin_ministerio_ve_todas_do_proprio_ministerio(self):
        self.assertSetEqual(
            set(get_igrejas_selecionaveis(self.admin)),
            set(Igreja.objects.filter(ministerio=self.ministerio)),
        )

    def test_usuario_sem_igreja_explicita_recebe_queryset_vazio(self):
        self.assertFalse(get_igrejas_selecionaveis(self.sem_escopo).exists())

    def test_middleware_seletor_e_helper_usam_o_mesmo_escopo(self):
        request = self._run_middleware(self._request(self.pastor))
        seletor = get_churches_tree_ordered({'request': request})
        self.assertSetEqual(set(request.igrejas_permitidas), set(get_igrejas_selecionaveis(self.pastor)))
        self.assertSetEqual(set(seletor), set(get_igrejas_selecionaveis(self.pastor)))

    def test_sessao_valida_permanece(self):
        request = self._run_middleware(self._request(self.admin, self.local.pk))
        self.assertEqual(request.igreja_ativa, self.local)
        self.assertEqual(request.session['igreja_ativa_id'], self.local.pk)

    def test_sessao_obsoleta_e_removida_apos_perda_de_acesso(self):
        self.pastor_perfil.igrejas_permitidas.add(self.sede)
        request = self._request(self.pastor, self.local.pk)
        self.pastor_perfil.igrejas_permitidas.remove(self.local)
        self._run_middleware(request)
        self.assertNotEqual(request.session.get('igreja_ativa_id'), self.local.pk)
        self.assertNotEqual(getattr(request.igreja_ativa, 'pk', None), self.local.pk)

    def test_sessao_e_removida_quando_escopo_fica_vazio(self):
        request = self._request(self.pastor, self.local.pk)
        self.pastor_perfil.igrejas_permitidas.clear()
        self._run_middleware(request)
        self.assertNotIn('igreja_ativa_id', request.session)
        self.assertIsNone(request.igreja_ativa)

    def test_post_valido_altera_contexto(self):
        self.pastor_perfil.igrejas_permitidas.add(self.sede)
        self.client.force_login(self.pastor)
        response = self.client.post(self.url, {'igreja_id_selector': self.sede.pk})
        self.assertRedirects(response, reverse('secretaria:dashboard'), fetch_redirect_response=False)
        self.assertEqual(self.client.session['igreja_ativa_id'], self.sede.pk)

    def test_get_nao_altera_estado(self):
        self.client.force_login(self.pastor)
        session = self.client.session
        session['igreja_ativa_id'] = self.local.pk
        session.save()
        response = self.client.get(self.url, {'igreja_id_selector': self.sede.pk})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.client.session['igreja_ativa_id'], self.local.pk)

    def test_id_inexistente_fora_do_escopo_e_cross_ministerio_nao_alteram(self):
        self.pastor_perfil.igrejas_permitidas.add(self.sede)
        self.client.force_login(self.pastor)
        for igreja_id in (999999, self.subordinada.pk, self.cross_ministerio.pk):
            session = self.client.session
            session['igreja_ativa_id'] = self.local.pk
            session.save()
            self.client.post(self.url, {'igreja_id_selector': igreja_id})
            self.assertEqual(self.client.session['igreja_ativa_id'], self.local.pk)

    def test_limpeza_explicita_remove_contexto(self):
        self.pastor_perfil.igrejas_permitidas.add(self.sede)
        self.client.force_login(self.pastor)
        session = self.client.session
        session['igreja_ativa_id'] = self.local.pk
        session.save()
        self.client.post(self.url, {'igreja_id_selector': 'todas'})
        self.assertNotIn('igreja_ativa_id', self.client.session)

    def test_next_interno_funciona_e_externo_e_rejeitado(self):
        self.pastor_perfil.igrejas_permitidas.add(self.sede)
        self.client.force_login(self.pastor)
        next_interno = reverse('configuracao:gestao_departamentos')
        response = self.client.post(
            self.url,
            {'igreja_id_selector': self.sede.pk, 'next': next_interno},
        )
        self.assertEqual(response.url, next_interno)
        for unsafe in ('https://example.invalid/phishing', '//example.invalid/phishing'):
            response = self.client.post(
                self.url,
                {'igreja_id_selector': self.sede.pk, 'next': unsafe},
            )
            self.assertEqual(response.url, reverse('secretaria:dashboard'))

    def test_csrf_e_exigido(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.pastor)
        response = client.post(self.url, {'igreja_id_selector': self.local.pk})
        self.assertEqual(response.status_code, 403)


    def test_logging_estruturado_registra_sucesso_limpeza_e_negacao(self):
        self.pastor_perfil.igrejas_permitidas.add(self.sede)
        self.client.force_login(self.pastor)
        with patch('configuracao.views.logger') as logger:
            self.client.post(self.url, {'igreja_id_selector': self.sede.pk})
            success_extra = logger.info.call_args.kwargs['extra']
            self.assertEqual(success_extra['result'], 'success')
            self.assertEqual(success_extra['user_id'], self.pastor.pk)
            self.assertEqual(success_extra['ministerio_id'], self.ministerio.pk)
            self.assertEqual(success_extra['new_church_id'], self.sede.pk)

            self.client.post(self.url, {'igreja_id_selector': 'todas'})
            self.assertEqual(logger.info.call_args.kwargs['extra']['result'], 'cleared')

            self.client.post(self.url, {'igreja_id_selector': self.cross_ministerio.pk})
            denied_extra = logger.warning.call_args.kwargs['extra']
            self.assertEqual(denied_extra['result'], 'denied')
            self.assertEqual(denied_extra['requested_church_id'], self.cross_ministerio.pk)
