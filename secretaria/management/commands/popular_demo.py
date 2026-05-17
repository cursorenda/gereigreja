from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from configuracao.models import Ministerio, Igreja
from secretaria.models import Pessoa, TipoPessoa, StatusPessoa
from financeiro.models import Despesas, Receitas
from django.utils import timezone
from contas.constants import (
    ADMIN_MINISTERIO,
    LIDERANCA_SECRETARIA,
    LIDERANCA_FINANCEIRA,
    PASTOR_REGIONAL,
    PASTOR_LOCAL,
    SECRETARIO_LOCAL,
    TESOUREIRO,
    SUPERINTENDENTE_EBD,
    PROFESSOR_EBD,
    EQUIPE_RECEPCAO,
    EQUIPE_EVENTOS,
    EQUIPE_MIDIA,
    MEMBRO_COMUM,
)

class Command(BaseCommand):
    help = 'Popula o banco com dados de demonstração (modo demo)'

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_user, _ = User.objects.get_or_create(username="admin_demo", defaults={"email": "admin@demo.com", "is_staff": True})
        if not admin_user.has_usable_password():
            admin_user.set_password("demo123")
            admin_user.save()

        ministerio, _ = Ministerio.objects.get_or_create(
            nome_fantasia="DEMONSTRAÇÃO",
            defaults={
                "cnpj": "00.000.000/0001-00",
                "cidade": "Cidade Demo",
                "estado": "SP",
                "administrador_principal": admin_user,
            }
        )
        # Garante que o ministério demo está ativo
        if not ministerio.ativo:
            ministerio.ativo = True
            ministerio.save()
        # Cria assinatura gratuita para o ministério demo (necessário para acesso)
        from configuracao.models import AssinaturaMinisterio
        assinatura_demo, _ = AssinaturaMinisterio.objects.get_or_create(
            ministerio=ministerio,
            defaults={
                "data_inicio": timezone.now(),
                "data_fim": timezone.now() + timezone.timedelta(days=3650),  # 10 anos
                "status": "gratuita",
            }
        )
        if assinatura_demo.status != "gratuita":
            assinatura_demo.status = "gratuita"
            assinatura_demo.data_fim = timezone.now() + timezone.timedelta(days=3650)
            assinatura_demo.save()

        # 1 Sede
        sede_obj, _ = Igreja.objects.get_or_create(
            ministerio=ministerio,
            nome_igreja="Igreja Sede DEMO",
            tipo_igreja="sede",
            cidade="Cidade Demo",
            estado="SP"
        )

        regionais = []
        for r in range(1, 4):
            regional_obj, _ = Igreja.objects.get_or_create(
                ministerio=ministerio,
                nome_igreja=f"Regional {r} DEMO",
                tipo_igreja="regional",
                igreja_superior=sede_obj,
                cidade=f"Cidade Regional {r}",
                estado="SP"
            )
            regionais.append(regional_obj)

        congregacoes = []
        for idx, regional in enumerate(regionais, start=1):
            for c in range(1, 4):
                congregacao_obj, _ = Igreja.objects.get_or_create(
                    ministerio=ministerio,
                    nome_igreja=f"Congregação {idx}-{c} DEMO",
                    tipo_igreja="congregacao",
                    igreja_superior=regional,
                    cidade=f"Cidade Congregação {idx}-{c}",
                    estado="SP"
                )
                congregacoes.append(congregacao_obj)

        # Garante que todas as listas contenham apenas objetos Igreja (não tuplas)
        regionais = [r if not isinstance(r, tuple) else r[0] for r in regionais]
        congregacoes = [c if not isinstance(c, tuple) else c[0] for c in congregacoes]
        todas_igrejas = [sede_obj] + regionais + congregacoes

        # Garante que existam os tipos e status obrigatórios
        # Os imports de modelos já estão no topo do arquivo, não repita aqui
        tipo_membro, _ = TipoPessoa.objects.get_or_create(nome="Membro", defaults={"descricao": "Membro padrão demo"})
        status_ativo, _ = StatusPessoa.objects.get_or_create(nome="Ativo", defaults={"descricao": "Status ativo demo"})

        # Cria membros em cada igreja
        for igreja in todas_igrejas:
            for i in range(1, 11):
                Pessoa.objects.get_or_create(
                    nome=f"Membro {igreja.nome_igreja} {i}",
                    igreja=igreja,
                    cpf=f"{igreja.pk:03d}.{i:03d}.000-00",
                    email=f"{igreja.pk}_{i}@demo.com",
                    status_pessoa=status_ativo,
                    tipo_pessoa=tipo_membro,
                )


        # Criação de grupos e usuários demo para cada perfil

        # Perfis e grupos conforme as constantes do sistema
        # Apenas demo_admin tem is_staff=True (acesso ao admin Django para suporte).
        # Todos os outros perfis demo têm is_staff=False para não expor o /admin/.
        perfis = [
            {"nome": ADMIN_MINISTERIO, "username": "demo_admin", "email": "admin@demo.com", "is_staff": True, "is_superuser": False},
            {"nome": PASTOR_REGIONAL, "username": "demo_pastor_regional", "email": "pastor.regional@demo.com", "is_staff": False, "is_superuser": False},
            {"nome": PASTOR_LOCAL, "username": "demo_pastor_local", "email": "pastor.local@demo.com", "is_staff": False, "is_superuser": False},
            {"nome": LIDERANCA_SECRETARIA, "username": "demo_lideranca_secretaria", "email": "secretaria.ministerial@demo.com", "is_staff": False, "is_superuser": False},
            {"nome": LIDERANCA_FINANCEIRA, "username": "demo_lideranca_financeira", "email": "financeiro.ministerial@demo.com", "is_staff": False, "is_superuser": False},
            {"nome": SECRETARIO_LOCAL, "username": "demo_secretario_local", "email": "secretario.local@demo.com", "is_staff": False, "is_superuser": False},
            {"nome": TESOUREIRO, "username": "demo_tesoureiro", "email": "tesoureiro@demo.com", "is_staff": False, "is_superuser": False},
            {"nome": SUPERINTENDENTE_EBD, "username": "demo_superintendente_ebd", "email": "superintendente.ebd@demo.com", "is_staff": False, "is_superuser": False},
            {"nome": PROFESSOR_EBD, "username": "demo_professor_ebd", "email": "professor.ebd@demo.com", "is_staff": False, "is_superuser": False},
            {"nome": EQUIPE_RECEPCAO, "username": "demo_recepcao", "email": "recepcao@demo.com", "is_staff": False, "is_superuser": False},
            {"nome": EQUIPE_EVENTOS, "username": "demo_eventos", "email": "eventos@demo.com", "is_staff": False, "is_superuser": False},
            {"nome": EQUIPE_MIDIA, "username": "demo_midia", "email": "midia@demo.com", "is_staff": False, "is_superuser": False},
        ]
        for perfil in perfis:
            group, _ = Group.objects.get_or_create(name=perfil["nome"])
            user, created = User.objects.get_or_create(
                username=perfil["username"],
                defaults={
                    "email": perfil["email"],
                    "is_staff": perfil["is_staff"],
                    "is_superuser": perfil["is_superuser"],
                }
            )
            if created or not user.has_usable_password():
                user.set_password("demo123")
            # Sempre força is_staff e is_superuser corretos, mesmo para usuários já existentes
            user.is_staff = perfil["is_staff"]
            user.is_superuser = False
            user.save()
            user.groups.add(group)
            # Cria ou atualiza PerfilUsuario vinculado ao ministério demo
            from configuracao.models import PerfilUsuario
            perfil_obj, _ = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={"ministerio": ministerio}
            )
            if perfil_obj.ministerio != ministerio:
                perfil_obj.ministerio = ministerio
                perfil_obj.save()
            # Vincula todas as igrejas do ministério demo ao perfil
            perfil_obj.igrejas_permitidas.set(todas_igrejas)

        # Usuário demo do tipo membro comum (não staff, não superuser)
        membro_group, _ = Group.objects.get_or_create(name=MEMBRO_COMUM)
        user_membro, created = User.objects.get_or_create(
            username="demo_membro",
            defaults={
                "email": "membro@demo.com",
                "is_staff": False,
                "is_superuser": False,
            }
        )
        if created or not user_membro.has_usable_password():
            user_membro.set_password("demo123")
            user_membro.save()
        user_membro.groups.add(membro_group)
        # Cria PerfilUsuario para membro demo
        from configuracao.models import PerfilUsuario
        perfil_membro, _ = PerfilUsuario.objects.get_or_create(
            user=user_membro,
            defaults={"ministerio": ministerio}
        )
        if perfil_membro.ministerio != ministerio:
            perfil_membro.ministerio = ministerio
            perfil_membro.save()
        perfil_membro.igrejas_permitidas.set(todas_igrejas)

        # Adiciona o perfil pastor genérico como alias do Pastor Local para compatibilidade com demos antigas
        alias_pastor, _ = User.objects.get_or_create(
            username="demo_pastor",
            defaults={
                "email": "pastor@demo.com",
                "is_staff": False,
                "is_superuser": False,
            }
        )
        if created or not alias_pastor.has_usable_password():
            alias_pastor.set_password("demo123")
        alias_pastor.is_staff = False
        alias_pastor.is_superuser = False
        alias_pastor.save()
        grupo_pastor_local, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        alias_pastor.groups.add(grupo_pastor_local)
        perfil_alias_pastor, _ = PerfilUsuario.objects.get_or_create(user=alias_pastor, defaults={"ministerio": ministerio})
        if perfil_alias_pastor.ministerio != ministerio:
            perfil_alias_pastor.ministerio = ministerio
            perfil_alias_pastor.save()
        perfil_alias_pastor.igrejas_permitidas.set(todas_igrejas)

        # Vincula o usuário demo_membro a um dos membros criados
        membro_pessoa = Pessoa.objects.filter(email__icontains="@demo.com").first()
        if membro_pessoa:
            membro_pessoa.usuario = user_membro
            membro_pessoa.save()


        from financeiro.models import ContaBancaria, CategoriaDespesa

        # Cria categorias de despesa demo para o ministério
        categoria_despesa_demo, _ = CategoriaDespesa.objects.get_or_create(
            ministerio=ministerio,
            nome="Operacional DEMO",
            defaults={"padrao_global": True}
        )

        # Cria contas bancárias demo para cada igreja
        contas_por_igreja = {}
        for igreja in todas_igrejas:
            conta, _ = ContaBancaria.objects.get_or_create(
                igreja=igreja,
                nome_identificacao="Caixa DEMO",
                defaults={
                    "tipo": "caixa_fisico",
                    "saldo_inicial": 1000,
                    "is_principal": True,
                }
            )
            contas_por_igreja[igreja.pk] = conta

        # Cria receitas e despesas associadas a contas/categorias demo
        for igreja in todas_igrejas:
            conta = contas_por_igreja.get(igreja.pk)
            for i in range(1, 4):
                Receitas.objects.get_or_create(
                    igreja=igreja,
                    valor=100 * i,
                    observacao=f"Receita Demo {i} - {igreja.nome_igreja}",
                    data=timezone.now(),
                    conta_bancaria=conta,
                    categoria=[c[0] for c in Receitas.CATEGORIA_CHOICES][i % len(Receitas.CATEGORIA_CHOICES)]
                )
                Despesas.objects.get_or_create(
                    igreja=igreja,
                    valor=50 * i,
                    observacao=f"Despesa Demo {i} - {igreja.nome_igreja}",
                    data=timezone.now(),
                    conta_bancaria=conta,
                    categoria=categoria_despesa_demo,
                )

        # --- DADOS DEMO DE EVENTOS ---
        from eventos.models import Evento, ParticipacaoEvento
        import random

        tipo_culto = "culto"
        tipo_reuniao = "reuniao"
        tipo_festa = "festa"
        sede = sede_obj
        tipos = list(TipoPessoa.objects.all())
        status = list(StatusPessoa.objects.all())
        data_base = timezone.now()
        eventos_demo = [
            {
                "titulo": "Culto de Celebração DEMO",
                "tipo": tipo_culto,
                "dias": 1,
                "descricao": "Culto especial de demonstração.",
            },
            {
                "titulo": "Reunião de Líderes DEMO",
                "tipo": tipo_reuniao,
                "dias": 1,
                "descricao": "Reunião de líderes para planejamento demo.",
            },
            {
                "titulo": "Festa da Família DEMO",
                "tipo": tipo_festa,
                "dias": 2,
                "descricao": "Festa de integração das famílias demo.",
            },
        ]
        eventos_criados = []
        for idx, evento_info in enumerate(eventos_demo):
            evento, _ = Evento.objects.get_or_create(
                igreja=sede,
                titulo=evento_info["titulo"],
                tipo=evento_info["tipo"],
                quantidade_dias=evento_info["dias"],
                descricao=evento_info["descricao"],
                data_inicio=data_base + timezone.timedelta(days=idx),
                data_fim=(data_base + timezone.timedelta(days=idx+evento_info["dias"])) if evento_info["dias"] > 1 else None,
                responsavel=admin_user,
            )
            eventos_criados.append(evento)
            # Participações demo: 10 membros aleatórios
            membros_demo = list(Pessoa.objects.filter(igreja=sede)[:10])
            for membro in membros_demo:
                ParticipacaoEvento.objects.get_or_create(
                    evento=evento,
                    membro=membro,
                    papel="PARTICIPANTE",
                    status="CONFIRMADO",
                    tipo_inclusao="AUTOMATICA",
                )

        # --- DADOS DEMO DE NOTIFICAÇÕES ---

        from notificacoes.models import Notificacao, NotificacaoEnviada
        usuarios_demo = User.objects.filter(username__startswith="demo_")
        ministerio_demo = ministerio
        tipos_notificacao = ["info", "aviso", "financeiro", "membro", "alerta", "sucesso"]
        for user in usuarios_demo:
            for i in range(2):
                Notificacao.objects.get_or_create(
                    user=user,
                    ministerio=ministerio_demo,
                    message=f"Mensagem demo {i+1} para {user.username}",
                    notification_type=random.choice(tipos_notificacao),
                    is_read=(i % 2 == 0),
                )

        # Notificações enviadas demo
        for i in range(3):
            NotificacaoEnviada.objects.get_or_create(
                tipo=random.choice(["evento", "aniversario", "outro"]),
                titulo=f"Notificação Enviada Demo {i+1}",
                mensagem=f"Esta é uma mensagem de notificação enviada demo {i+1}.",
                destinatario=f"destinatario{i+1}@demo.com",
            )

        self.stdout.write(self.style.SUCCESS('Estrutura demo criada: 1 sede, 3 regionais, 9 congregações, membros, lançamentos, eventos e notificações!'))