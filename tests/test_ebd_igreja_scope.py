from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from configuracao.models import AssinaturaMinisterio, Igreja, Ministerio, PerfilUsuario, Plano
from escola_biblica.models import Aluno, AnoLetivo, Avaliacao, CadastroAluno, Classe, Frequencia, Licao, OfertaClasse, TransferenciaAluno, Turma
from secretaria.models import Cargo, Membro, MembroCargo, StatusPessoa, TipoPessoa


class EBDIgrejaScopeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grupo_secretaria_ebd = Group.objects.create(name='Secretaria EBD')

        cls.admin_user = User.objects.create_user(
            username='admin_ministerio',
            password='senha123',
            email='admin@teste.com',
        )

        cls.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio EBD Teste',
            administrador_principal=cls.admin_user,
            ativo=True,
        )

        cls.plano = Plano.objects.create(
            nome='pioneiro',
            preco_mensal=50.00,
            limite_membros=100,
            limite_igrejas=5,
        )
        AssinaturaMinisterio.objects.create(
            ministerio=cls.ministerio,
            plano=cls.plano,
            status='ativa',
            data_inicio=timezone.now() - timedelta(days=15),
            data_fim=timezone.now() + timedelta(days=15),
        )

        cls.igreja_central = Igreja.objects.create(
            nome_igreja='Igreja Central',
            ministerio=cls.ministerio,
        )
        cls.igreja_setor = Igreja.objects.create(
            nome_igreja='Igreja Setor Norte',
            ministerio=cls.ministerio,
        )

        cls.tipo_membro = TipoPessoa.objects.create(nome='Membro')
        cls.status_ativo = StatusPessoa.objects.create(nome='Ativo')
        cls.cargo_professor = Cargo.objects.create(nome='Professor EBD', is_ebd=True)

        cls.usuario_secretaria = User.objects.create_user(
            username='secretaria_ebd',
            password='senha123',
            email='secretaria@teste.com',
        )
        cls.usuario_secretaria.groups.add(cls.grupo_secretaria_ebd)
        cls.perfil_secretaria = PerfilUsuario.objects.create(
            user=cls.usuario_secretaria,
            ministerio=cls.ministerio,
        )
        cls.perfil_secretaria.igrejas_permitidas.add(cls.igreja_central, cls.igreja_setor)

        cls.ano_letivo = AnoLetivo.objects.create(ano=date.today().year, ativo=True)
        cls.classe = Classe.objects.create(
            nome='Adultos Escopo',
            igreja=cls.igreja_central,
            departamento='ADULTO',
            faixa_etaria='Adultos',
        )

        cls.professor_central_user = User.objects.create_user(username='prof_central', password='senha123')
        cls.professor_setor_user = User.objects.create_user(username='prof_setor', password='senha123')

        cls.professor_central = Membro.objects.create(
            nome='Professor Central',
            igreja=cls.igreja_central,
            tipo_pessoa=cls.tipo_membro,
            status_pessoa=cls.status_ativo,
            usuario=cls.professor_central_user,
        )
        cls.professor_setor = Membro.objects.create(
            nome='Professor Setor',
            igreja=cls.igreja_setor,
            tipo_pessoa=cls.tipo_membro,
            status_pessoa=cls.status_ativo,
            usuario=cls.professor_setor_user,
        )
        MembroCargo.objects.create(
            membro=cls.professor_central,
            cargo=cls.cargo_professor,
            data_inicio=date.today() - timedelta(days=30),
            data_fim=None,
        )
        MembroCargo.objects.create(
            membro=cls.professor_setor,
            cargo=cls.cargo_professor,
            data_inicio=date.today() - timedelta(days=30),
            data_fim=None,
        )

        cls.turma_central = Turma.objects.create(
            nome='Turma Central',
            classe=cls.classe,
            ano_letivo=cls.ano_letivo,
        )
        cls.turma_central.membros.add(cls.professor_central)

        cls.turma_setor = Turma.objects.create(
            nome='Turma Setor',
            classe=cls.classe,
            ano_letivo=cls.ano_letivo,
        )
        cls.turma_setor.membros.add(cls.professor_setor)

        cls.aluno_central = Aluno.objects.create(nome='Aluno Central', turma=cls.turma_central, ativo=True)
        cls.aluno_setor = Aluno.objects.create(nome='Aluno Setor', turma=cls.turma_setor, ativo=True)

    def setUp(self):
        self.client.login(username='secretaria_ebd', password='senha123')
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja_central.pk
        session.save()

    def test_turma_list_filtra_pela_igreja_ativa(self):
        response = self.client.get(reverse('escola_biblica:turma_list'))

        self.assertEqual(response.status_code, 200)
        turmas = list(response.context['turmas'])
        self.assertEqual([turma.pk for turma in turmas], [self.turma_central.pk])

    def test_relatorio_frequencia_filtra_alunos_pela_igreja_ativa(self):
        response = self.client.get(reverse('escola_biblica:relatorio_frequencia'))

        self.assertEqual(response.status_code, 200)
        alunos = list(response.context['alunos'])
        self.assertEqual([aluno.pk for aluno in alunos], [self.aluno_central.pk])

    def test_aluno_create_form_limita_turmas_ao_escopo(self):
        response = self.client.get(reverse('escola_biblica:aluno_create'))

        self.assertEqual(response.status_code, 200)
        turmas_disponiveis = list(response.context['form'].fields['turma'].queryset)
        self.assertEqual([turma.pk for turma in turmas_disponiveis], [self.turma_central.pk])

    def test_turma_edit_fora_do_escopo_retorna_404(self):
        response = self.client.get(reverse('escola_biblica:turma_edit', kwargs={'pk': self.turma_setor.pk}))

        self.assertEqual(response.status_code, 404)

    def test_mesmo_nome_classe_em_igrejas_diferentes(self):
        classe_setor = Classe.objects.create(
            nome='Adultos Escopo',
            igreja=self.igreja_setor,
            departamento='ADULTO',
            faixa_etaria='Adultos',
        )
        self.assertIsNotNone(classe_setor.pk)

    def test_ofertas_mesma_data_em_turmas_diferentes(self):
        OfertaClasse.objects.create(
            turma=self.turma_central,
            classe=self.turma_central.classe,
            data=date(2026, 2, 1),
            valor=10,
        )
        oferta_setor = OfertaClasse.objects.create(
            turma=self.turma_setor,
            classe=self.turma_setor.classe,
            data=date(2026, 2, 1),
            valor=20,
        )
        self.assertIsNotNone(oferta_setor.pk)

    def test_aluno_reutiliza_cadastro_mestre_ao_criar_nova_matricula(self):
        turma_extra = Turma.objects.create(
            nome='Turma Central B',
            classe=self.classe,
            igreja=self.igreja_central,
            ano_letivo=self.ano_letivo,
        )

        aluno_original = Aluno.objects.create(
            nome='Aluno Mestre',
            data_nascimento=date(2010, 5, 1),
            turma=self.turma_central,
            ativo=True,
        )
        aluno_novo = Aluno.objects.create(
            nome='Aluno Mestre',
            data_nascimento=date(2010, 5, 1),
            turma=turma_extra,
            ativo=True,
        )

        self.assertEqual(aluno_original.cadastro_id, aluno_novo.cadastro_id)
        self.assertEqual(CadastroAluno.objects.filter(nome='Aluno Mestre').count(), 1)

    def test_aluno_list_colapsa_matriculas_do_mesmo_cadastro(self):
        turma_extra = Turma.objects.create(
            nome='Turma Central C',
            classe=self.classe,
            igreja=self.igreja_central,
            ano_letivo=self.ano_letivo,
        )
        Aluno.objects.create(
            nome='Aluno Consolidado',
            data_nascimento=date(2011, 4, 2),
            turma=self.turma_central,
            ativo=True,
        )
        Aluno.objects.create(
            nome='Aluno Consolidado',
            data_nascimento=date(2011, 4, 2),
            turma=turma_extra,
            ativo=True,
        )

        response = self.client.get(reverse('escola_biblica:aluno_list'))

        self.assertEqual(response.status_code, 200)
        nomes = [aluno.nome for aluno in response.context['alunos']]
        self.assertEqual(nomes.count('Aluno Consolidado'), 1)

    def test_aluno_criado_na_ebd_vincula_pessoa_existente_da_secretaria(self):
        pessoa = Membro.objects.create(
            nome='Aluno Integrado',
            nascimento=date(2012, 6, 15),
            igreja=self.igreja_central,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
            email='aluno.integrado@teste.com',
        )

        aluno = Aluno.objects.create(
            nome='Aluno Integrado',
            data_nascimento=date(2012, 6, 15),
            turma=self.turma_central,
            ativo=True,
        )

        self.assertEqual(aluno.cadastro.pessoa_id, pessoa.pk)
        self.assertEqual(aluno.cadastro.nome, pessoa.nome)

    def test_aluno_com_cadastro_vinculado_sincroniza_nome_com_pessoa(self):
        pessoa = Membro.objects.create(
            nome='Aluno Master Secretaria',
            nascimento=date(2011, 3, 20),
            igreja=self.igreja_central,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )
        cadastro = CadastroAluno.objects.create(
            pessoa=pessoa,
            igreja=self.igreja_central,
            nome='Nome Desatualizado',
            data_nascimento=date(2011, 3, 20),
            ativo=True,
        )

        aluno = Aluno.objects.create(
            cadastro=cadastro,
            nome='Nome Desatualizado',
            data_nascimento=date(2011, 3, 20),
            turma=self.turma_central,
            ativo=True,
        )

        aluno.refresh_from_db()
        cadastro.refresh_from_db()

        self.assertEqual(cadastro.nome, pessoa.nome)
        self.assertEqual(aluno.nome, pessoa.nome)
        self.assertEqual(aluno.cadastro.pessoa_id, pessoa.pk)

    def test_transferencia_cria_nova_matricula_e_preserva_origem(self):
        turma_destino = Turma.objects.create(
            nome='Turma Central Destino',
            classe=self.classe,
            igreja=self.igreja_central,
            ano_letivo=self.ano_letivo,
        )

        response = self.client.post(
            reverse('escola_biblica:transferir_aluno', kwargs={'aluno_id': self.aluno_central.pk}),
            {
                'turma_destino': turma_destino.pk,
                'motivo': 'Reorganização de classe',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.aluno_central.refresh_from_db()
        self.assertFalse(self.aluno_central.ativo)
        self.assertEqual(self.aluno_central.turma_id, self.turma_central.pk)

        matricula_destino = Aluno.objects.exclude(pk=self.aluno_central.pk).get(
            cadastro_id=self.aluno_central.cadastro_id,
            turma=turma_destino,
        )
        self.assertTrue(matricula_destino.ativo)

        transferencia = TransferenciaAluno.objects.get(aluno=self.aluno_central)
        self.assertEqual(transferencia.turma_origem_id, self.turma_central.pk)
        self.assertEqual(transferencia.turma_destino_id, turma_destino.pk)
        self.assertEqual(transferencia.motivo, 'Reorganização de classe')

    def test_perfil_da_matricula_ativa_exibe_historico_da_transferencia_do_cadastro(self):
        turma_destino = Turma.objects.create(
            nome='Turma Central Histórico',
            classe=self.classe,
            igreja=self.igreja_central,
            ano_letivo=self.ano_letivo,
        )

        self.client.post(
            reverse('escola_biblica:transferir_aluno', kwargs={'aluno_id': self.aluno_central.pk}),
            {
                'turma_destino': turma_destino.pk,
                'motivo': 'Mudança de sala',
            },
        )
        matricula_destino = Aluno.objects.exclude(pk=self.aluno_central.pk).get(
            cadastro_id=self.aluno_central.cadastro_id,
            turma=turma_destino,
        )

        response = self.client.get(reverse('escola_biblica:aluno_detail', kwargs={'pk': matricula_destino.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['transferencias'].count(), 1)
        self.assertEqual(len(response.context['matriculas_relacionadas']), 1)
        self.assertContains(response, 'Mudança de sala')

    def test_perfil_aluno_exibe_link_para_hub_do_usuario_vinculado(self):
        usuario_aluno = User.objects.create_user(
            username='aluno_hub',
            password='senha123',
            email='aluno_hub@teste.com',
        )
        PerfilUsuario.objects.create(user=usuario_aluno, ministerio=self.ministerio)
        membro_aluno = Membro.objects.create(
            nome='Aluno Hub',
            igreja=self.igreja_central,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
            usuario=usuario_aluno,
        )
        cadastro = CadastroAluno.objects.create(
            pessoa=membro_aluno,
            igreja=self.igreja_central,
            nome=membro_aluno.nome,
            ativo=True,
        )
        aluno = Aluno.objects.create(
            cadastro=cadastro,
            nome=membro_aluno.nome,
            turma=self.turma_central,
            ativo=True,
        )

        response = self.client.get(reverse('escola_biblica:aluno_detail', kwargs={'pk': aluno.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('configuracao:perfil_usuario', args=[usuario_aluno.pk]))

    def test_historico_consolidado_anual_exibe_resumo_por_ano(self):
        turma_destino = Turma.objects.create(
            nome='Turma Central Histórico Anual',
            classe=self.classe,
            igreja=self.igreja_central,
            ano_letivo=self.ano_letivo,
        )

        self.client.post(
            reverse('escola_biblica:transferir_aluno', kwargs={'aluno_id': self.aluno_central.pk}),
            {
                'turma_destino': turma_destino.pk,
                'motivo': 'Mudança para histórico anual',
            },
        )
        matricula_destino = Aluno.objects.exclude(pk=self.aluno_central.pk).get(
            cadastro_id=self.aluno_central.cadastro_id,
            turma=turma_destino,
        )

        Frequencia.objects.create(aluno=self.aluno_central, data=date.today() - timedelta(days=30), presente=True)
        Frequencia.objects.create(aluno=matricula_destino, data=date.today(), presente=False)

        licao = Licao.objects.create(turma=turma_destino, data=date.today(), tema='Lição Histórico')
        Avaliacao.objects.create(aluno=matricula_destino, licao=licao, nota=8, participacao=True)

        response = self.client.get(reverse('escola_biblica:aluno_historico_consolidado', kwargs={'pk': matricula_destino.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Histórico Consolidado do Aluno')
        self.assertContains(response, str(date.today().year))
        self.assertEqual(response.context['total_matriculas'], 2)
        self.assertEqual(response.context['total_transferencias'], 1)
        self.assertEqual(response.context['total_frequencias'], 2)
        self.assertEqual(response.context['total_avaliacoes'], 1)

    def test_historico_consolidado_redireciona_quando_id_nao_existe_no_escopo(self):
        response = self.client.get(
            reverse('escola_biblica:aluno_historico_consolidado', kwargs={'pk': 999999}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'escola_biblica/aluno_list.html')
        self.assertContains(response, 'Aluno não encontrado no escopo atual')

    def test_relatorio_frequencia_consolida_cadastro_com_matriculas_transferidas(self):
        turma_destino = Turma.objects.create(
            nome='Turma Central Frequência',
            classe=self.classe,
            igreja=self.igreja_central,
            ano_letivo=self.ano_letivo,
        )

        self.client.post(
            reverse('escola_biblica:transferir_aluno', kwargs={'aluno_id': self.aluno_central.pk}),
            {
                'turma_destino': turma_destino.pk,
                'motivo': 'Mudança para relatório',
            },
        )
        matricula_destino = Aluno.objects.exclude(pk=self.aluno_central.pk).get(
            cadastro_id=self.aluno_central.cadastro_id,
            turma=turma_destino,
        )

        Frequencia.objects.create(aluno=self.aluno_central, data=date.today() - timedelta(days=7), presente=True)
        Frequencia.objects.create(aluno=matricula_destino, data=date.today(), presente=False)

        response = self.client.get(reverse('escola_biblica:relatorio_frequencia'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['alunos']), 1)
        aluno_relatorio = response.context['alunos'][0]
        self.assertEqual(aluno_relatorio.cadastro_id, self.aluno_central.cadastro_id)
        self.assertEqual(aluno_relatorio.turma_id, turma_destino.pk)
        self.assertEqual(aluno_relatorio.presencas, 1)
        self.assertEqual(aluno_relatorio.total_freq, 2)
        self.assertEqual(aluno_relatorio.freq_percent, 50.0)

    def test_relatorio_alunos_consolida_avaliacoes_de_cadastro_transferido(self):
        turma_destino = Turma.objects.create(
            nome='Turma Central Avaliação',
            classe=self.classe,
            igreja=self.igreja_central,
            ano_letivo=self.ano_letivo,
        )

        self.client.post(
            reverse('escola_biblica:transferir_aluno', kwargs={'aluno_id': self.aluno_central.pk}),
            {
                'turma_destino': turma_destino.pk,
                'motivo': 'Mudança para relatório de alunos',
            },
        )
        matricula_destino = Aluno.objects.exclude(pk=self.aluno_central.pk).get(
            cadastro_id=self.aluno_central.cadastro_id,
            turma=turma_destino,
        )

        licao_origem = Licao.objects.create(turma=self.turma_central, data=date.today() - timedelta(days=14), tema='Lição Origem')
        licao_destino = Licao.objects.create(turma=turma_destino, data=date.today(), tema='Lição Destino')
        Avaliacao.objects.create(aluno=self.aluno_central, licao=licao_origem, nota=7, participacao=True)
        Avaliacao.objects.create(aluno=matricula_destino, licao=licao_destino, nota=9, participacao=False)

        response = self.client.get(reverse('escola_biblica:relatorio_alunos'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['alunos']), 1)
        aluno_relatorio = response.context['alunos'][0]
        self.assertEqual(aluno_relatorio.cadastro_id, self.aluno_central.cadastro_id)
        self.assertEqual(aluno_relatorio.turma_id, turma_destino.pk)
        self.assertEqual(aluno_relatorio.media_nota, 8.0)
        self.assertEqual(aluno_relatorio.participacao, 1)

    def test_avaliacao_create_lista_apenas_matricula_ativa_do_cadastro(self):
        turma_destino = Turma.objects.create(
            nome='Turma Central Form Avaliação',
            classe=self.classe,
            igreja=self.igreja_central,
            ano_letivo=self.ano_letivo,
        )
        self.client.post(
            reverse('escola_biblica:transferir_aluno', kwargs={'aluno_id': self.aluno_central.pk}),
            {
                'turma_destino': turma_destino.pk,
                'motivo': 'Mudança para testar form',
            },
        )
        matricula_destino = Aluno.objects.exclude(pk=self.aluno_central.pk).get(
            cadastro_id=self.aluno_central.cadastro_id,
            turma=turma_destino,
        )

        response = self.client.get(reverse('escola_biblica:avaliacao_create'))

        self.assertEqual(response.status_code, 200)
        alunos_form = list(response.context['form'].fields['aluno'].queryset)
        self.assertIn(matricula_destino, alunos_form)
        self.assertNotIn(self.aluno_central, alunos_form)

    def test_aluno_list_exibe_status_de_vinculo_com_secretaria(self):
        pessoa = Membro.objects.create(
            nome='Aluno Com Badge',
            nascimento=date(2010, 8, 10),
            igreja=self.igreja_central,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )
        Aluno.objects.create(
            nome='Aluno Com Badge',
            data_nascimento=date(2010, 8, 10),
            turma=self.turma_central,
            ativo=True,
        )

        response = self.client.get(reverse('escola_biblica:aluno_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vinculado à Secretaria')
        self.assertContains(response, pessoa.nome)

    def test_vinculacao_manual_de_aluno_com_pessoa(self):
        aluno = Aluno.objects.create(
            nome='Aluno Manual',
            data_nascimento=date(2013, 7, 1),
            turma=self.turma_central,
            ativo=True,
        )
        pessoa = Membro.objects.create(
            nome='Pessoa Manual Secretaria',
            nascimento=date(2014, 1, 2),
            igreja=self.igreja_central,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )

        response = self.client.post(
            reverse('escola_biblica:aluno_vinculo_secretaria', kwargs={'pk': aluno.pk}),
            {'pessoa_id': pessoa.pk},
            follow=True,
        )

        aluno.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(aluno.cadastro.pessoa_id, pessoa.pk)
        self.assertContains(response, 'Aluno vinculado com sucesso')

    def test_aluno_list_filtra_por_status_de_vinculo(self):
        Membro.objects.create(
            nome='Aluno Filtro Vinculado',
            nascimento=date(2012, 2, 2),
            igreja=self.igreja_central,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )
        Aluno.objects.create(
            nome='Aluno Filtro Vinculado',
            data_nascimento=date(2012, 2, 2),
            turma=self.turma_central,
            ativo=True,
        )
        Aluno.objects.create(
            nome='Aluno Filtro Sem Vinculo',
            data_nascimento=date(2014, 9, 9),
            turma=self.turma_central,
            ativo=True,
        )

        response = self.client.get(reverse('escola_biblica:aluno_list'), {'vinculo': 'sem_vinculo'})

        self.assertEqual(response.status_code, 200)
        nomes = [aluno.nome for aluno in response.context['alunos']]
        self.assertIn('Aluno Filtro Sem Vinculo', nomes)
        self.assertNotIn('Aluno Filtro Vinculado', nomes)

    def test_aluno_list_tenta_vinculacao_automatica_em_lote(self):
        aluno = Aluno.objects.create(
            nome='Aluno Lote',
            data_nascimento=date(2015, 1, 5),
            turma=self.turma_central,
            ativo=True,
        )
        pessoa = Membro.objects.create(
            nome='Aluno Lote',
            nascimento=date(2015, 1, 5),
            igreja=self.igreja_central,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )

        response = self.client.post(
            f"{reverse('escola_biblica:aluno_list')}?vinculo=sem_vinculo",
            {'acao': 'tentar_vinculo_lote'},
            follow=True,
        )

        aluno.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(aluno.cadastro.pessoa_id, pessoa.pk)
        self.assertContains(response, 'vinculados automaticamente à Secretaria')
        self.assertContains(response, 'Vinculados: Aluno Lote')

    def test_vinculacao_manual_em_massa(self):
        aluno = Aluno.objects.create(
            nome='Aluno Massa',
            data_nascimento=date(2016, 6, 6),
            turma=self.turma_central,
            ativo=True,
        )
        pessoa = Membro.objects.create(
            nome='Pessoa Massa',
            nascimento=date(2016, 6, 6),
            igreja=self.igreja_central,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )

        response_get = self.client.get(
            f"{reverse('escola_biblica:aluno_vinculo_secretaria_lote')}?vinculo=sem_vinculo"
        )
        self.assertEqual(response_get.status_code, 200)
        self.assertContains(response_get, 'Vinculação Manual em Massa')
        self.assertContains(response_get, 'Aluno Massa')

        response_post = self.client.post(
            f"{reverse('escola_biblica:aluno_vinculo_secretaria_lote')}?vinculo=sem_vinculo",
            {f'pessoa_cadastro_{aluno.cadastro_id}': pessoa.pk},
            follow=True,
        )

        aluno.refresh_from_db()
        self.assertEqual(response_post.status_code, 200)
        self.assertEqual(aluno.cadastro.pessoa_id, pessoa.pk)
        self.assertContains(response_post, 'Vínculos aplicados:')
        self.assertContains(response_post, 'Pessoa Massa')