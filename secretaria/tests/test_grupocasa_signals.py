from django.test import TestCase
from secretaria.models import Membro, GrupoCasa, TipoPessoa, StatusPessoa
from configuracao.models import Igreja

class GrupoCasaSignalsTest(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from configuracao.models import Ministerio
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='admin')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministério Teste',
            administrador_principal=self.admin
        )
        self.igreja = Igreja.objects.create(nome_igreja='Igreja Teste', ministerio=self.ministerio)
        self.tipo = TipoPessoa.objects.create(nome='Membro')
        self.status = StatusPessoa.objects.create(nome='Ativo')

    def test_associate_on_create_when_group_exists(self):
        g = GrupoCasa.objects.create(igreja=self.igreja, rua='Rua A', numero='10', complemento='', cep='12345')
        m = Membro.objects.create(nome='Joao', igreja=self.igreja, tipo_pessoa=self.tipo, status_pessoa=self.status, rua='Rua A', numero_casa='10', complemento='', cep='12345')
        m.refresh_from_db()
        self.assertIsNotNone(m.grupo_casa)
        self.assertEqual(m.grupo_casa.id, g.id)

    def test_associate_on_update_address(self):
        g = GrupoCasa.objects.create(igreja=self.igreja, rua='Rua B', numero='5', complemento='', cep='00000')
        m = Membro.objects.create(nome='Maria', igreja=self.igreja, tipo_pessoa=self.tipo, status_pessoa=self.status, rua='Outra', numero_casa='1', cep='99999')
        # update address to match group
        m.rua = 'Rua B'
        m.numero_casa = '5'
        m.cep = '00000'
        m.save()
        m.refresh_from_db()
        self.assertIsNotNone(m.grupo_casa)
        self.assertEqual(m.grupo_casa.id, g.id
)
    
    def test_create_group_when_two_members_share_address(self):
        # two members with same address should trigger automatic group creation
        m1 = Membro.objects.create(nome='Aline', igreja=self.igreja, tipo_pessoa=self.tipo, status_pessoa=self.status, rua='Rua Criar', numero_casa='10', complemento='', cep='55555')
        m2 = Membro.objects.create(nome='Bruno', igreja=self.igreja, tipo_pessoa=self.tipo, status_pessoa=self.status, rua='Rua Criar', numero_casa='10', complemento='', cep='55555')
        # reload from DB
        m1.refresh_from_db()
        m2.refresh_from_db()
        self.assertIsNotNone(m1.grupo_casa)
        self.assertIsNotNone(m2.grupo_casa)
        self.assertEqual(m1.grupo_casa_id, m2.grupo_casa_id)
        # verify GrupoCasa exists with rua/numero
        gc = GrupoCasa.objects.get(pk=m1.grupo_casa_id)
        self.assertEqual(gc.rua, 'Rua Criar')
        self.assertEqual(gc.numero, '10')
