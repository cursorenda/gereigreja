from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from contas.constants import MEMBRO_COMUM
from configuracao.models import CidadeCatalogo, CidadeTraducao, Pais, SubdivisaoAdministrativa
from configuracao.services_localidades import buscar_cidades_catalogo


class LocalidadesCatalogoTests(TestCase):
    def setUp(self):
        self.pais = Pais.objects.create(
            codigo_iso2='BR',
            codigo_iso3='BRA',
            nome_oficial='Brasil',
            nome_curto='Brasil',
            idioma_padrao='pt-BR',
            ativo=True,
        )
        self.sub = SubdivisaoAdministrativa.objects.create(
            pais=self.pais,
            codigo='SP',
            nome='Sao Paulo',
            nivel=SubdivisaoAdministrativa.NIVEL_ESTADO,
            ativo=True,
        )
        self.cidade = CidadeCatalogo.objects.create(
            pais=self.pais,
            subdivisao=self.sub,
            nome='Sao Paulo',
            ativo=True,
        )
        CidadeTraducao.objects.create(cidade=self.cidade, idioma='pt-BR', nome='Sao Paulo')

    def test_busca_cidades_por_termo_sem_acento(self):
        resultados = list(buscar_cidades_catalogo(termo='sao paulo', pais_iso2='BR', idioma='pt-BR', limite=10))
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0].pk, self.cidade.pk)

    def test_api_retorna_resultados(self):
        usuario = get_user_model().objects.create_user(username='usuario-localidades')
        grupo_membro_comum, _ = Group.objects.get_or_create(name=MEMBRO_COMUM)
        usuario.groups.add(grupo_membro_comum)
        self.client.force_login(usuario)
        url = reverse('configuracao:api_buscar_cidades')
        resp = self.client.get(url, {'q': 'sao', 'country': 'BR', 'lang': 'pt-BR'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['pais_iso2'], 'BR')
