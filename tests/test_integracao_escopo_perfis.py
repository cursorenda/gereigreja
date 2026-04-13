from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from configuracao.models import Igreja, Ministerio, PerfilUsuario
from contas.constants import (
    ADMIN_MINISTERIO,
    LIDERANCA_SECRETARIA,
    PASTOR_LOCAL,
    PASTOR_REGIONAL,
)
from escola_biblica.models import Aluno, AnoLetivo, CadastroAluno, Classe, Frequencia, Turma
from financeiro.models import CategoriaDespesa, ContaBancaria, Despesas, Receitas
from secretaria.models import Membro, StatusPessoa, TipoPessoa


class EscopoPerfisIntegracaoTest(TestCase):
    def setUp(self):
        User = get_user_model()

        self.admin = User.objects.create_user(
            username="admin_integracao_perfis",
            email="admin_perfis@example.com",
            password="senha123",
        )

        self.ministerio = Ministerio.objects.create(
            nome_fantasia="Ministerio Integracao Perfis",
            administrador_principal=self.admin,
            ativo=True,
            cnpj="12345678000177",
        )

        self.sede = Igreja.objects.create(
            nome_igreja="Sede Perfis",
            ministerio=self.ministerio,
            tipo_igreja="sede",
        )
        self.regional = Igreja.objects.create(
            nome_igreja="Regional Perfis",
            ministerio=self.ministerio,
            tipo_igreja="regional",
            igreja_superior=self.sede,
        )
        self.congregacao = Igreja.objects.create(
            nome_igreja="Congregacao Perfis",
            ministerio=self.ministerio,
            tipo_igreja="congregacao",
            igreja_superior=self.regional,
        )
        self.ponto_local = Igreja.objects.create(
            nome_igreja="Ponto Local Perfis",
            ministerio=self.ministerio,
            tipo_igreja="independente",
            igreja_superior=self.congregacao,
        )

        self.grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        self.grupo_regional, _ = Group.objects.get_or_create(name=PASTOR_REGIONAL)
        self.grupo_local, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        self.grupo_lider_secretaria, _ = Group.objects.get_or_create(name=LIDERANCA_SECRETARIA)

        self.usuario_ministerial = User.objects.create_user(
            username="usuario_ministerial_perfis",
            email="ministerial_perfis@example.com",
            password="senha123",
        )
        self.usuario_ministerial.groups.add(self.grupo_admin)
        PerfilUsuario.objects.create(
            user=self.usuario_ministerial,
            ministerio=self.ministerio,
        )

        self.usuario_regional = User.objects.create_user(
            username="usuario_regional_perfis",
            email="regional_perfis@example.com",
            password="senha123",
        )
        self.usuario_regional.groups.add(self.grupo_regional)
        perfil_regional = PerfilUsuario.objects.create(
            user=self.usuario_regional,
            ministerio=self.ministerio,
        )
        perfil_regional.igrejas_permitidas.set([self.regional])

        self.usuario_local = User.objects.create_user(
            username="usuario_local_perfis",
            email="local_perfis@example.com",
            password="senha123",
        )
        self.usuario_local.groups.add(self.grupo_local)
        perfil_local = PerfilUsuario.objects.create(
            user=self.usuario_local,
            ministerio=self.ministerio,
        )
        perfil_local.igrejas_permitidas.set([self.congregacao])

        self.usuario_lider_secretaria = User.objects.create_user(
            username="usuario_lider_secretaria_perfis",
            email="lider_secretaria_perfis@example.com",
            password="senha123",
        )
        self.usuario_lider_secretaria.groups.add(self.grupo_lider_secretaria)
        perfil_lider_secretaria = PerfilUsuario.objects.create(
            user=self.usuario_lider_secretaria,
            ministerio=self.ministerio,
        )
        perfil_lider_secretaria.igrejas_permitidas.set([self.sede])

        self.tipo_membro = TipoPessoa.objects.create(nome="Membro Perfis")
        self.status_ativo = StatusPessoa.objects.create(nome="Ativo Perfis")

        self.membro_sede = Membro.objects.create(
            nome="Membro Sede Perfis",
            igreja=self.sede,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )
        self.membro_regional = Membro.objects.create(
            nome="Membro Regional Perfis",
            igreja=self.regional,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )
        self.membro_congregacao = Membro.objects.create(
            nome="Membro Congregacao Perfis",
            igreja=self.congregacao,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )
        self.membro_ponto_local = Membro.objects.create(
            nome="Membro Ponto Local Perfis",
            igreja=self.ponto_local,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )

        self.conta_sede = ContaBancaria.objects.create(
            igreja=self.sede,
            nome_identificacao="Conta Sede Perfis",
            tipo="caixa_fisico",
            saldo_inicial=0,
        )
        self.conta_regional = ContaBancaria.objects.create(
            igreja=self.regional,
            nome_identificacao="Conta Regional Perfis",
            tipo="caixa_fisico",
            saldo_inicial=0,
        )
        self.conta_congregacao = ContaBancaria.objects.create(
            igreja=self.congregacao,
            nome_identificacao="Conta Congregacao Perfis",
            tipo="caixa_fisico",
            saldo_inicial=0,
        )
        self.conta_ponto_local = ContaBancaria.objects.create(
            igreja=self.ponto_local,
            nome_identificacao="Conta Ponto Local Perfis",
            tipo="caixa_fisico",
            saldo_inicial=0,
        )

        self.categoria_despesa = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome="Operacional Perfis",
        )

        Receitas.objects.create(
            igreja=self.sede,
            categoria="oferta",
            data="2026-04-01",
            valor=Decimal("100.00"),
            membro=self.membro_sede,
            conta_bancaria=self.conta_sede,
            fechado=False,
        )
        self.receita_regional = Receitas.objects.create(
            igreja=self.regional,
            categoria="oferta",
            data="2026-04-02",
            valor=Decimal("200.00"),
            membro=self.membro_regional,
            conta_bancaria=self.conta_regional,
            fechado=False,
        )
        self.receita_congregacao = Receitas.objects.create(
            igreja=self.congregacao,
            categoria="oferta",
            data="2026-04-03",
            valor=Decimal("300.00"),
            membro=self.membro_congregacao,
            conta_bancaria=self.conta_congregacao,
            fechado=False,
        )
        Receitas.objects.create(
            igreja=self.ponto_local,
            categoria="oferta",
            data="2026-04-04",
            valor=Decimal("400.00"),
            membro=self.membro_ponto_local,
            conta_bancaria=self.conta_ponto_local,
            fechado=False,
        )

        self.despesa_regional = Despesas.objects.create(
            igreja=self.regional,
            categoria=self.categoria_despesa,
            data="2026-04-02",
            descricao="Despesa Regional Setup",
            valor=Decimal("50.00"),
            conta_bancaria=self.conta_regional,
            fechado=False,
        )
        self.despesa_congregacao = Despesas.objects.create(
            igreja=self.congregacao,
            categoria=self.categoria_despesa,
            data="2026-04-03",
            descricao="Despesa Congregacao Setup",
            valor=Decimal("60.00"),
            conta_bancaria=self.conta_congregacao,
            fechado=False,
        )

    def test_lista_receitas_escopo_ministerial_retorna_todas_as_igrejas_do_ministerio(self):
        self.client.force_login(self.usuario_ministerial)

        response = self.client.get(reverse("financeiro:lista_receitas"))

        self.assertEqual(response.status_code, 200)
        receitas_ids_igreja = set(response.context["receitas"].values_list("igreja_id", flat=True))
        self.assertEqual(
            receitas_ids_igreja,
            {self.sede.pk, self.regional.pk, self.congregacao.pk, self.ponto_local.pk},
        )

    def test_lista_receitas_escopo_regional_retorna_base_e_subordinadas(self):
        self.client.force_login(self.usuario_regional)

        response = self.client.get(reverse("financeiro:lista_receitas"))

        self.assertEqual(response.status_code, 200)
        receitas_ids_igreja = set(response.context["receitas"].values_list("igreja_id", flat=True))
        self.assertEqual(
            receitas_ids_igreja,
            {self.regional.pk, self.congregacao.pk, self.ponto_local.pk},
        )
        self.assertNotIn(self.sede.pk, receitas_ids_igreja)

    def test_lista_receitas_escopo_local_retorna_base_e_descendentes_sem_ancestrais(self):
        self.client.force_login(self.usuario_local)

        response = self.client.get(reverse("financeiro:lista_receitas"))

        self.assertEqual(response.status_code, 200)
        receitas_ids_igreja = set(response.context["receitas"].values_list("igreja_id", flat=True))
        self.assertEqual(receitas_ids_igreja, {self.congregacao.pk, self.ponto_local.pk})
        self.assertNotIn(self.sede.pk, receitas_ids_igreja)
        self.assertNotIn(self.regional.pk, receitas_ids_igreja)

    def test_lista_contas_bancarias_escopo_regional_retorna_apenas_hierarquia_permitida(self):
        self.client.force_login(self.usuario_regional)

        response = self.client.get(reverse("financeiro:lista_contas_bancarias"))

        self.assertEqual(response.status_code, 200)
        contas_ids_igreja = set(response.context["contas_bancarias"].values_list("igreja_id", flat=True))
        self.assertEqual(
            contas_ids_igreja,
            {self.regional.pk, self.congregacao.pk, self.ponto_local.pk},
        )
        self.assertNotIn(self.sede.pk, contas_ids_igreja)

    def test_cadastrar_receita_escopo_regional_permite_igreja_subordinada(self):
        self.client.force_login(self.usuario_regional)

        payload = {
            "igreja": str(self.congregacao.pk),
            "membro": str(self.membro_congregacao.pk),
            "data": "2026-04-10",
            "categoria": "oferta",
            "valor": "123.45",
            "forma_pgto": "PIX",
            "conta_bancaria": str(self.conta_congregacao.pk),
            "observacao": "receita_regional_subordinada",
        }

        response = self.client.post(reverse("financeiro:cadastrar_receita"), data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Receitas.objects.filter(
                igreja=self.congregacao,
                observacao="receita_regional_subordinada",
                valor=Decimal("123.45"),
            ).exists()
        )

    def test_cadastrar_receita_escopo_local_permite_igreja_descendente(self):
        self.client.force_login(self.usuario_local)

        payload = {
            "igreja": str(self.ponto_local.pk),
            "membro": str(self.membro_ponto_local.pk),
            "data": "2026-04-11",
            "categoria": "oferta",
            "valor": "80.00",
            "forma_pgto": "DIN",
            "conta_bancaria": str(self.conta_ponto_local.pk),
            "observacao": "receita_local_descendente",
        }

        response = self.client.post(reverse("financeiro:cadastrar_receita"), data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Receitas.objects.filter(
                igreja=self.ponto_local,
                observacao="receita_local_descendente",
                valor=Decimal("80.00"),
            ).exists()
        )

    def test_cadastrar_receita_escopo_local_bloqueia_igreja_ancestral_fora_do_escopo(self):
        self.client.force_login(self.usuario_local)

        payload = {
            "igreja": str(self.regional.pk),
            "membro": str(self.membro_regional.pk),
            "data": "2026-04-12",
            "categoria": "oferta",
            "valor": "90.00",
            "forma_pgto": "PIX",
            "conta_bancaria": str(self.conta_regional.pk),
            "observacao": "receita_local_ancestral_bloqueada",
        }

        response = self.client.post(reverse("financeiro:cadastrar_receita"), data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Receitas.objects.filter(
                observacao="receita_local_ancestral_bloqueada",
            ).exists()
        )

    def test_cadastrar_despesa_escopo_regional_permite_igreja_subordinada(self):
        self.client.force_login(self.usuario_regional)

        payload = {
            "igreja": str(self.congregacao.pk),
            "categoria": str(self.categoria_despesa.pk),
            "data": "2026-04-13",
            "descricao": "Despesa Regional Subordinada",
            "valor": "55.40",
            "conta_bancaria": str(self.conta_congregacao.pk),
            "observacao": "despesa_regional_subordinada",
        }

        response = self.client.post(reverse("financeiro:cadastrar_despesa"), data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Despesas.objects.filter(
                igreja=self.congregacao,
                observacao="despesa_regional_subordinada",
                valor=Decimal("55.40"),
            ).exists()
        )

    def test_cadastrar_despesa_escopo_local_permite_igreja_descendente(self):
        self.client.force_login(self.usuario_local)

        payload = {
            "igreja": str(self.ponto_local.pk),
            "categoria": str(self.categoria_despesa.pk),
            "data": "2026-04-14",
            "descricao": "Despesa Local Descendente",
            "valor": "33.00",
            "conta_bancaria": str(self.conta_ponto_local.pk),
            "observacao": "despesa_local_descendente",
        }

        response = self.client.post(reverse("financeiro:cadastrar_despesa"), data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Despesas.objects.filter(
                igreja=self.ponto_local,
                observacao="despesa_local_descendente",
                valor=Decimal("33.00"),
            ).exists()
        )

    def test_cadastrar_despesa_escopo_local_bloqueia_igreja_ancestral_fora_do_escopo(self):
        self.client.force_login(self.usuario_local)

        payload = {
            "igreja": str(self.regional.pk),
            "categoria": str(self.categoria_despesa.pk),
            "data": "2026-04-15",
            "descricao": "Despesa Local Bloqueada",
            "valor": "77.00",
            "conta_bancaria": str(self.conta_regional.pk),
            "observacao": "despesa_local_ancestral_bloqueada",
        }

        response = self.client.post(reverse("financeiro:cadastrar_despesa"), data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Despesas.objects.filter(
                observacao="despesa_local_ancestral_bloqueada",
            ).exists()
        )

    # ------------------------------------------------------------------
    # Edição com escopo cruzado
    # ------------------------------------------------------------------

    def test_editar_receita_escopo_local_bloqueia_objeto_de_outra_igreja(self):
        self.client.force_login(self.usuario_local)

        response = self.client.get(
            reverse("financeiro:editar_receita", args=[self.receita_regional.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_editar_receita_escopo_regional_permite_objeto_subordinado(self):
        self.client.force_login(self.usuario_regional)

        payload = {
            "igreja": str(self.receita_congregacao.igreja.pk),
            "membro": str(self.membro_congregacao.pk),
            "data": "2026-04-20",
            "categoria": "dizimo",
            "valor": "150.00",
            "forma_pgto": "PIX",
            "conta_bancaria": str(self.conta_congregacao.pk),
            "observacao": "receita_editada_por_regional",
        }

        response = self.client.post(
            reverse("financeiro:editar_receita", args=[self.receita_congregacao.pk]),
            data=payload,
        )

        self.assertEqual(response.status_code, 302)
        self.receita_congregacao.refresh_from_db()
        self.assertEqual(self.receita_congregacao.observacao, "receita_editada_por_regional")

    def test_editar_despesa_escopo_local_bloqueia_objeto_de_outra_igreja(self):
        self.client.force_login(self.usuario_local)

        response = self.client.get(
            reverse("financeiro:editar_despesa", args=[self.despesa_regional.pk])
        )

        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------
    # Exclusão com escopo cruzado
    # ------------------------------------------------------------------

    def test_excluir_receita_escopo_local_bloqueia_objeto_de_outra_igreja(self):
        self.client.force_login(self.usuario_local)

        response = self.client.post(
            reverse("financeiro:excluir_receita", args=[self.receita_regional.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Receitas.objects.filter(pk=self.receita_regional.pk).exists())

    def test_excluir_receita_escopo_regional_permite_objeto_subordinado(self):
        self.client.force_login(self.usuario_regional)
        pk = self.receita_congregacao.pk

        response = self.client.post(
            reverse("financeiro:excluir_receita", args=[pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Receitas.objects.filter(pk=pk).exists())

    def test_excluir_despesa_escopo_local_bloqueia_objeto_de_outra_igreja(self):
        self.client.force_login(self.usuario_local)

        response = self.client.post(
            reverse("financeiro:excluir_despesa", args=[self.despesa_regional.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Despesas.objects.filter(pk=self.despesa_regional.pk).exists())

    # ------------------------------------------------------------------
    # Painéis de liderança - filtro hierárquico
    # ------------------------------------------------------------------

    def test_painel_lideranca_financeiro_global_sede_filtro_regional_mostra_rede_regional(self):
        self.client.force_login(self.usuario_ministerial)
        session = self.client.session
        session["igreja_ativa_id"] = self.sede.pk
        session.save()

        response = self.client.get(
            reverse("financeiro:painel_lideranca_financeiro"),
            {"igreja_filtro": str(self.regional.pk), "periodo_filtro": "geral"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Rede: Regional Perfis", response.context["titulo_dashboard"])
        self.assertEqual(response.context["allowed_churches_count"], 3)

    def test_painel_lideranca_financeiro_global_sede_filtro_folha_mostra_apenas_igreja(self):
        self.client.force_login(self.usuario_ministerial)
        session = self.client.session
        session["igreja_ativa_id"] = self.sede.pk
        session.save()

        response = self.client.get(
            reverse("financeiro:painel_lideranca_financeiro"),
            {"igreja_filtro": str(self.ponto_local.pk), "periodo_filtro": "geral"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Igreja: Ponto Local Perfis", response.context["titulo_dashboard"])
        self.assertEqual(response.context["allowed_churches_count"], 1)

    def test_painel_lideranca_secretaria_global_sede_filtro_regional_mostra_rede_regional(self):
        self.client.force_login(self.usuario_lider_secretaria)
        session = self.client.session
        session["igreja_ativa_id"] = self.sede.pk
        session.save()

        response = self.client.get(
            reverse("secretaria:painel_lideranca_secretaria"),
            {"igreja_filtro": str(self.regional.pk)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Rede: Regional Perfis", response.context["titulo_dashboard"])
        self.assertEqual(response.context["allowed_churches_count"], 3)

    def test_meu_perfil_exibe_aba_aluno_ebd_com_links_consolidados(self):
        self.membro_congregacao.usuario = self.usuario_local
        self.membro_congregacao.save(update_fields=["usuario"])

        ano_letivo = AnoLetivo.objects.create(ano=2026, ativo=True)
        classe = Classe.objects.create(
            igreja=self.congregacao,
            nome="Classe Perfil Unificado",
            departamento="ADULTO",
        )
        turma = Turma.objects.create(
            nome="Turma Perfil Unificado",
            igreja=self.congregacao,
            classe=classe,
            ano_letivo=ano_letivo,
        )
        cadastro = CadastroAluno.objects.create(
            igreja=self.congregacao,
            pessoa=self.membro_congregacao,
            nome=self.membro_congregacao.nome,
            data_nascimento=self.membro_congregacao.nascimento,
        )
        matricula = Aluno.objects.create(
            cadastro=cadastro,
            turma=turma,
            nome=self.membro_congregacao.nome,
            data_nascimento=self.membro_congregacao.nascimento,
            ativo=True,
        )
        Frequencia.objects.create(
            aluno=matricula,
            data=date(2026, 4, 12),
            presente=True,
        )

        self.client.force_login(self.usuario_local)

        response = self.client.get(reverse("configuracao:meu_perfil"), {"aba": "ebd-aluno"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hub do Perfil")
        self.assertContains(response, "Visão do Aluno EBD")
        self.assertContains(
            response,
            reverse("escola_biblica:aluno_detail", args=[matricula.pk]),
        )
        self.assertContains(
            response,
            reverse("escola_biblica:aluno_historico_consolidado", args=[matricula.pk]),
        )
        self.assertContains(response, "Turma Perfil Unificado")
        self.assertEqual(response.context["cadastro_ebd"], cadastro)
        self.assertEqual(response.context["matricula_referencia_ebd"], matricula)

    def test_perfil_usuario_exibe_hub_com_aba_ebd_do_usuario_alvo(self):
        self.membro_congregacao.usuario = self.usuario_local
        self.membro_congregacao.save(update_fields=["usuario"])

        ano_letivo = AnoLetivo.objects.create(ano=2027, ativo=True)
        classe = Classe.objects.create(
            igreja=self.congregacao,
            nome="Classe Perfil Terceiro",
            departamento="ADULTO",
        )
        turma = Turma.objects.create(
            nome="Turma Perfil Terceiro",
            igreja=self.congregacao,
            classe=classe,
            ano_letivo=ano_letivo,
        )
        cadastro = CadastroAluno.objects.create(
            igreja=self.congregacao,
            pessoa=self.membro_congregacao,
            nome=self.membro_congregacao.nome,
            data_nascimento=self.membro_congregacao.nascimento,
        )
        matricula = Aluno.objects.create(
            cadastro=cadastro,
            turma=turma,
            nome=self.membro_congregacao.nome,
            data_nascimento=self.membro_congregacao.nascimento,
            ativo=True,
        )

        self.client.force_login(self.usuario_ministerial)

        response = self.client.get(
            reverse("configuracao:perfil_usuario", args=[self.usuario_local.pk]),
            {"aba": "ebd-aluno"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Perfil de {self.usuario_local.username}")
        self.assertContains(response, "Visão do Aluno EBD")
        self.assertContains(
            response,
            reverse("escola_biblica:aluno_detail", args=[matricula.pk]),
        )
        self.assertContains(response, "Turma Perfil Terceiro")
        self.assertEqual(response.context["usuario"], self.usuario_local)
        self.assertEqual(response.context["cadastro_ebd"], cadastro)
        self.assertEqual(response.context["matricula_referencia_ebd"], matricula)

    def test_meu_perfil_exibe_aba_secretaria_com_dados_do_membro_vinculado(self):
        self.membro_congregacao.usuario = self.usuario_local
        self.membro_congregacao.telefone = "1111-1111"
        self.membro_congregacao.celular = "99999-1111"
        self.membro_congregacao.email = "membro_congregacao@example.com"
        self.membro_congregacao.save(update_fields=["usuario", "telefone", "celular", "email"])

        self.client.force_login(self.usuario_local)

        response = self.client.get(reverse("configuracao:meu_perfil"), {"aba": "secretaria"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cadastro da Secretaria")
        self.assertContains(response, self.congregacao.nome_igreja)
        self.assertContains(response, "membro_congregacao@example.com")
        self.assertContains(
            response,
            reverse("secretaria:detalhe_membro", args=[self.membro_congregacao.pk]),
        )
        self.assertEqual(response.context["membro_secretaria_obj"], self.membro_congregacao)

    def test_meu_perfil_resumo_exibe_hierarquia_pessoa_usuario_cadastroebd(self):
        """Testa que o Resumo exibe a hierarquia visual Pessoa → Usuário → Cadastro(s) EBD"""
        self.membro_congregacao.usuario = self.usuario_local
        self.membro_congregacao.save(update_fields=["usuario"])

        ano_letivo = AnoLetivo.objects.create(ano=2026, ativo=True)
        classe = Classe.objects.create(
            igreja=self.congregacao,
            nome="Classe Hierarquia",
            departamento="ADULTO",
        )
        turma = Turma.objects.create(
            nome="Turma Hierarquia",
            igreja=self.congregacao,
            classe=classe,
            ano_letivo=ano_letivo,
        )
        cadastro = CadastroAluno.objects.create(
            igreja=self.congregacao,
            pessoa=self.membro_congregacao,
            nome=self.membro_congregacao.nome,
            data_nascimento=self.membro_congregacao.nascimento,
        )
        matricula = Aluno.objects.create(
            cadastro=cadastro,
            turma=turma,
            nome=self.membro_congregacao.nome,
            data_nascimento=self.membro_congregacao.nascimento,
            ativo=True,
        )

        self.client.force_login(self.usuario_local)

        response = self.client.get(reverse("configuracao:meu_perfil"))

        self.assertEqual(response.status_code, 200)
        # Valida que está na aba Resumo padrão
        self.assertEqual(response.context["aba_ativa"], "resumo")
        # Valida estrutura hierárquica: Pessoa (Membro)
        self.assertContains(response, "Hierarquia de Vínculo no Sistema")
        self.assertContains(response, "PESSOA")
        self.assertContains(response, self.membro_congregacao.nome)
        # Valida estrutura: Usuário
        self.assertContains(response, "USUÁRIO")
        self.assertContains(response, self.usuario_local.username)
        # Valida estrutura: Cadastro(s) EBD
        self.assertContains(response, "CADASTRO(S) EBD")
        self.assertContains(response, "Total: 1 cadastro(s)")
        self.assertContains(response, "Turma ativa:")
        self.assertContains(response, "Turma Hierarquia")