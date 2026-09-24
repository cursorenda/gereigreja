"""Prepara um cenário funcional exclusivamente para o SQLite local do projeto."""

from getpass import getpass
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from contas.constants import (
    ADMIN_MINISTERIO,
    MEMBRO_COMUM,
    PASTOR_LOCAL,
    SECRETARIO_LOCAL,
    TESOUREIRO,
)
from configuracao.models import (
    Departamento,
    DepartamentoMinisterial,
    DepartamentoVinculo,
    Igreja,
    Ministerio,
    PerfilUsuario,
)
from configuracao.services_departamentos import DepartamentoVinculoService
from secretaria.models import Pessoa, StatusPessoa, TipoPessoa


SETTINGS_LOCAL = 'core.settings_local'
SETTINGS_TEST = 'core.settings_test'
LOCAL_DATABASE_NAME = Path(settings.BASE_DIR) / 'db.sqlite3'

MINISTERIO_NOME = '[LOCAL TEST] Ministério Local de Testes'
SEDE_NOME = '[LOCAL TEST] Igreja Sede'
REGIONAL_NOME = '[LOCAL TEST] Regional'
CONGREGACAO_NOME = '[LOCAL TEST] Congregação'
DEPARTAMENTO_CODIGO = 'ASSISTENCIA_LOCAL_TEST'
DEPARTAMENTO_NOME = '[LOCAL TEST] Assistência Social'

USUARIOS = (
    ('admin_ministerio_local', 'Admin Ministério Local', ADMIN_MINISTERIO, 'sede'),
    ('pastor_local_teste', 'Pastor Local de Teste', PASTOR_LOCAL, 'congregacao'),
    ('secretario_local_teste', 'Secretário Local de Teste', SECRETARIO_LOCAL, 'sede'),
    ('tesoureiro_local_teste', 'Tesoureiro Local de Teste', TESOUREIRO, 'sede'),
    ('membro_local_teste', 'Membro Local de Teste', MEMBRO_COMUM, 'congregacao'),
    ('multi_funcao_local', 'Multi Função Local', TESOUREIRO, 'congregacao'),
)


def validar_ambiente_local(*, permitir_settings_test=False):
    """Falha fechada antes de qualquer escrita fora do SQLite local esperado."""
    settings_module = getattr(settings, 'SETTINGS_MODULE', None)
    database = settings.DATABASES.get('default', {})
    engine = database.get('ENGINE')
    database_name = database.get('NAME')

    if settings_module == SETTINGS_TEST and permitir_settings_test:
        nome_teste = str(database_name)
        if engine != 'django.db.backends.sqlite3' or not (
            nome_teste == ':memory:' or nome_teste.startswith('file:memorydb_')
        ):
            raise CommandError('Ambiente de teste local inválido para o seed.')
        return

    if settings_module != SETTINGS_LOCAL:
        raise CommandError('Este comando só pode ser executado com --settings=core.settings_local.')

    if engine != 'django.db.backends.sqlite3':
        raise CommandError('Este comando exige SQLite local; engines remotas são bloqueadas.')

    if Path(database_name).resolve() != LOCAL_DATABASE_NAME.resolve():
        raise CommandError('O SQLite informado não corresponde ao db.sqlite3 local esperado.')


def _solicitar_senha_local():
    senha = getpass('Senha local para os usuários sintéticos: ')
    confirmacao = getpass('Confirme a senha local: ')
    if not senha:
        raise CommandError('A senha local não pode ser vazia.')
    if senha != confirmacao:
        raise CommandError('As senhas informadas não conferem.')
    return senha


def _obter_ou_criar_usuario(username, nome, password):
    User = get_user_model()
    usuario, criado = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@local.test',
            'first_name': nome,
            'is_staff': False,
            'is_superuser': False,
        },
    )
    if criado:
        if password is None:
            raise CommandError('Uma senha local é obrigatória para criar usuários do seed.')
        usuario.set_password(password)
        usuario.save(update_fields=['password'])
    return usuario, criado


def preparar_ambiente_local(*, password=None, reset_passwords=False, permitir_settings_test=False):
    """Cria o cenário idempotente; ``permitir_settings_test`` é exclusivo dos testes."""
    validar_ambiente_local(permitir_settings_test=permitir_settings_test)

    with transaction.atomic():
        usuarios = {}
        usuarios_criados = {}
        for username, nome, _, _ in USUARIOS:
            usuario, criado = _obter_ou_criar_usuario(username, nome, password)
            usuarios[username] = usuario
            usuarios_criados[username] = criado

        admin_ministerio = usuarios['admin_ministerio_local']
        ministerio, _ = Ministerio.objects.get_or_create(
            nome_fantasia=MINISTERIO_NOME,
            defaults={
                'administrador_principal': admin_ministerio,
                'ativo': True,
                'is_demo': False,
                'cidade': 'Local',
                'estado': 'MG',
            },
        )
        ministerio.administrador_principal = admin_ministerio
        ministerio.ativo = True
        ministerio.is_demo = False
        ministerio.save(update_fields=['administrador_principal', 'ativo', 'is_demo', 'data_atualizacao'])

        sede, _ = Igreja.objects.get_or_create(
            ministerio=ministerio,
            nome_igreja=SEDE_NOME,
            defaults={'tipo_igreja': 'sede', 'cidade': 'Local', 'estado': 'MG'},
        )
        regional, _ = Igreja.objects.get_or_create(
            ministerio=ministerio,
            nome_igreja=REGIONAL_NOME,
            defaults={
                'tipo_igreja': 'regional',
                'igreja_superior': sede,
                'cidade': 'Local',
                'estado': 'MG',
            },
        )
        congregacao, _ = Igreja.objects.get_or_create(
            ministerio=ministerio,
            nome_igreja=CONGREGACAO_NOME,
            defaults={
                'tipo_igreja': 'congregacao',
                'igreja_superior': regional,
                'cidade': 'Local',
                'estado': 'MG',
            },
        )
        for igreja, tipo, superior in (
            (sede, 'sede', None),
            (regional, 'regional', sede),
            (congregacao, 'congregacao', regional),
        ):
            igreja.tipo_igreja = tipo
            igreja.igreja_superior = superior
            igreja.save(update_fields=['tipo_igreja', 'igreja_superior', 'data_atualizacao'])

        tipo_pessoa, _ = TipoPessoa.objects.get_or_create(
            nome='[LOCAL TEST] Membro',
            defaults={'descricao': 'Tipo sintético exclusivo do ambiente local.'},
        )
        status_pessoa, _ = StatusPessoa.objects.get_or_create(
            nome='[LOCAL TEST] Ativo',
            defaults={'descricao': 'Status sintético exclusivo do ambiente local.'},
        )

        igrejas_por_escopo = {'sede': sede, 'congregacao': congregacao}
        pessoas = {}
        for username, nome, grupo_nome, escopo in USUARIOS:
            usuario = usuarios[username]
            if reset_passwords:
                if password is None:
                    raise CommandError('Uma senha local é obrigatória para redefinir usuários do seed.')
                usuario.set_password(password)
                usuario.save(update_fields=['password'])
            usuario.groups.add(Group.objects.get_or_create(name=grupo_nome)[0])
            if usuario.is_superuser or usuario.is_staff:
                usuario.is_superuser = False
                usuario.is_staff = False
                usuario.save(update_fields=['is_superuser', 'is_staff'])

            perfil, _ = PerfilUsuario.objects.get_or_create(
                user=usuario,
                defaults={'ministerio': ministerio},
            )
            if perfil.ministerio_id != ministerio.id:
                perfil.ministerio = ministerio
                perfil.save(update_fields=['ministerio'])
            perfil.igrejas_permitidas.set([igrejas_por_escopo[escopo]])

            pessoa, _ = Pessoa.objects.update_or_create(
                usuario=usuario,
                defaults={
                    'igreja': igrejas_por_escopo[escopo],
                    'nome': nome,
                    'email': f'{username}@local.test',
                    'tipo_pessoa': tipo_pessoa,
                    'status_pessoa': status_pessoa,
                },
            )
            pessoas[username] = pessoa

        definicao, _ = DepartamentoMinisterial.objects.get_or_create(
            ministerio=ministerio,
            codigo=DEPARTAMENTO_CODIGO,
            defaults={'nome': DEPARTAMENTO_NOME, 'ativo': True, 'ordem': 100},
        )
        departamento, _ = Departamento.objects.get_or_create(
            igreja=congregacao,
            codigo_interno=DEPARTAMENTO_CODIGO,
            defaults={
                'departamento_ministerial': definicao,
                'nome_exibicao': DEPARTAMENTO_NOME,
                'tipo_departamento': Departamento.TIPO_PERSONALIZADO,
                'classificacao': Departamento.CLASSIFICACAO_ORGANIZACIONAL,
                'ativo': True,
            },
        )
        if not DepartamentoVinculo.objects.filter(
            departamento=departamento,
            membro=pessoas['multi_funcao_local'],
            data_fim__isnull=True,
        ).exists():
            DepartamentoVinculoService.adicionar(
                departamento=departamento,
                membro=pessoas['multi_funcao_local'],
                usuario=usuarios['pastor_local_teste'],
            )

    return {
        'ministerio': ministerio,
        'sede': sede,
        'regional': regional,
        'congregacao': congregacao,
        'usuarios_criados': usuarios_criados,
    }


class Command(BaseCommand):
    help = 'Prepara o ambiente funcional exclusivamente no SQLite local do GereIgreja.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-passwords',
            action='store_true',
            help='Solicita nova senha local e redefine apenas os usuários sintéticos do seed.',
        )

    def handle(self, *args, **options):
        validar_ambiente_local()
        User = get_user_model()
        usuarios_existentes = User.objects.filter(username__in=[item[0] for item in USUARIOS]).count()
        reset_passwords = options['reset_passwords']
        password = None
        if reset_passwords or usuarios_existentes < len(USUARIOS):
            password = _solicitar_senha_local()

        preparar_ambiente_local(password=password, reset_passwords=reset_passwords)
        self.stdout.write('Ambiente local preparado.')
        self.stdout.write(f'Ministério:\n{MINISTERIO_NOME}')
        self.stdout.write('Usuários:')
        for username, *_ in USUARIOS:
            self.stdout.write(username)
        self.stdout.write('Servidor:\nhttp://127.0.0.1:8000/')