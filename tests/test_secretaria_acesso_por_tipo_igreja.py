import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from configuracao.models import Igreja, Ministerio
from contas.constants import ADMIN_MINISTERIO, MEMBRO_COMUM, PASTOR_LOCAL, SECRETARIO_LOCAL
from contas.page_permissions import pode_acessar_secretaria


@pytest.mark.django_db
def test_admin_na_sede_exige_escopo_explicito():
    from configuracao.models import PerfilUsuario

    User = get_user_model()
    admin = User.objects.create_user(username='admin_sede', password='senha123')
    Group.objects.get_or_create(name=ADMIN_MINISTERIO)
    admin.groups.add(Group.objects.get(name=ADMIN_MINISTERIO))

    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Sede',
        administrador_principal=admin,
        ativo=True,
        cnpj='11111111000111',
    )
    igreja = Igreja.objects.create(nome_igreja='Igreja Sede', ministerio=ministerio, tipo_igreja='sede')

    assert not pode_acessar_secretaria(admin, igreja=igreja)

    perfil = PerfilUsuario.objects.create(user=admin, ministerio=ministerio)
    perfil.igrejas_permitidas.add(igreja)

    assert pode_acessar_secretaria(admin, igreja=igreja)


@pytest.mark.django_db
def test_admin_na_independente_exige_escopo_explicito():
    from configuracao.models import PerfilUsuario

    User = get_user_model()
    admin = User.objects.create_user(username='admin_independente', password='senha123')
    Group.objects.get_or_create(name=ADMIN_MINISTERIO)
    admin.groups.add(Group.objects.get(name=ADMIN_MINISTERIO))

    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Independente',
        administrador_principal=admin,
        ativo=True,
        cnpj='22222222000122',
    )
    igreja = Igreja.objects.create(nome_igreja='Igreja Independente', ministerio=ministerio, tipo_igreja='independente')

    assert not pode_acessar_secretaria(admin, igreja=igreja)

    perfil = PerfilUsuario.objects.create(user=admin, ministerio=ministerio)
    perfil.igrejas_permitidas.add(igreja)

    assert pode_acessar_secretaria(admin, igreja=igreja)


@pytest.mark.django_db
def test_admin_nao_acessa_secretaria_na_regional():
    User = get_user_model()
    admin = User.objects.create_user(username='admin_regional', password='senha123')
    Group.objects.get_or_create(name=ADMIN_MINISTERIO)
    admin.groups.add(Group.objects.get(name=ADMIN_MINISTERIO))

    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Regional',
        administrador_principal=admin,
        ativo=True,
        cnpj='33333333000133',
    )
    igreja = Igreja.objects.create(nome_igreja='Igreja Regional', ministerio=ministerio, tipo_igreja='regional')

    assert not pode_acessar_secretaria(admin, igreja=igreja)


@pytest.mark.django_db
def test_admin_nao_acessa_secretaria_na_congregacao():
    User = get_user_model()
    admin = User.objects.create_user(username='admin_congregacao', password='senha123')
    Group.objects.get_or_create(name=ADMIN_MINISTERIO)
    admin.groups.add(Group.objects.get(name=ADMIN_MINISTERIO))

    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Congregacao',
        administrador_principal=admin,
        ativo=True,
        cnpj='44444444000144',
    )
    igreja = Igreja.objects.create(nome_igreja='Igreja Congregacao', ministerio=ministerio, tipo_igreja='congregacao')

    assert not pode_acessar_secretaria(admin, igreja=igreja)


@pytest.mark.django_db
def test_secretario_local_exige_escopo_explicito():
    from configuracao.models import PerfilUsuario

    User = get_user_model()
    secretario = User.objects.create_user(username='secretario_local', password='senha123')
    dono_ministerio = User.objects.create_user(username='dono_ministerio_secretario', password='senha123')
    Group.objects.get_or_create(name=SECRETARIO_LOCAL)
    secretario.groups.add(Group.objects.get(name=SECRETARIO_LOCAL))

    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Secretario',
        administrador_principal=dono_ministerio,
        ativo=True,
        cnpj='55555555000155',
    )
    igreja = Igreja.objects.create(nome_igreja='Igreja Secretario Permitida', ministerio=ministerio, tipo_igreja='regional')
    outra_igreja = Igreja.objects.create(nome_igreja='Igreja Secretario Nao Permitida', ministerio=ministerio, tipo_igreja='congregacao')

    assert not pode_acessar_secretaria(secretario)
    assert not pode_acessar_secretaria(secretario, igreja=igreja)

    perfil = PerfilUsuario.objects.create(user=secretario, ministerio=ministerio)
    perfil.igrejas_permitidas.add(igreja)

    assert pode_acessar_secretaria(secretario)
    assert pode_acessar_secretaria(secretario, igreja=igreja)
    assert not pode_acessar_secretaria(secretario, igreja=outra_igreja)


@pytest.mark.django_db
def test_secretario_local_e_admin_ministerio_somam_permissoes_sem_expandir_escopo_local():
    from configuracao.models import PerfilUsuario

    User = get_user_model()
    secretario_admin = User.objects.create_user(username='secretario_admin_dual', password='senha123')
    Group.objects.get_or_create(name=SECRETARIO_LOCAL)
    secretario_admin.groups.add(Group.objects.get(name=SECRETARIO_LOCAL))

    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Secretario Admin Dual',
        administrador_principal=secretario_admin,
        ativo=True,
        cnpj='57575757000157',
    )
    congregacao = Igreja.objects.create(
        nome_igreja='Congregacao Dual',
        ministerio=ministerio,
        tipo_igreja='congregacao',
    )
    sede = Igreja.objects.create(
        nome_igreja='Sede Dual',
        ministerio=ministerio,
        tipo_igreja='sede',
    )
    independente = Igreja.objects.create(
        nome_igreja='Independente Dual',
        ministerio=ministerio,
        tipo_igreja='independente',
    )
    regional = Igreja.objects.create(
        nome_igreja='Regional Dual',
        ministerio=ministerio,
        tipo_igreja='regional',
    )
    perfil = PerfilUsuario.objects.create(user=secretario_admin, ministerio=ministerio)

    assert not pode_acessar_secretaria(secretario_admin, igreja=congregacao)
    assert pode_acessar_secretaria(secretario_admin, igreja=sede)
    assert pode_acessar_secretaria(secretario_admin, igreja=independente)
    assert not pode_acessar_secretaria(secretario_admin, igreja=regional)

    perfil.igrejas_permitidas.add(congregacao)

    assert pode_acessar_secretaria(secretario_admin, igreja=congregacao)


@pytest.mark.django_db
def test_usuario_comum_nunca_acessa_secretaria():
    User = get_user_model()
    dono_ministerio = User.objects.create_user(username='dono_ministerio_comum', password='senha123')
    comum = User.objects.create_user(username='usuario_comum_secretaria', password='senha123')
    Group.objects.get_or_create(name=MEMBRO_COMUM)
    comum.groups.add(Group.objects.get(name=MEMBRO_COMUM))

    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Comum',
        administrador_principal=dono_ministerio,
        ativo=True,
        cnpj='66666666000166',
    )
    igreja = Igreja.objects.create(nome_igreja='Igreja Sede Comum', ministerio=ministerio, tipo_igreja='sede')

    assert not pode_acessar_secretaria(comum)
    assert not pode_acessar_secretaria(comum, igreja=igreja)


@pytest.mark.django_db
def test_pastor_local_sem_igreja_ativa_com_igreja_explicita_pode_acessar_secretaria():
    from configuracao.models import PerfilUsuario

    User = get_user_model()
    pastor = User.objects.create_user(username='pastor_local_sem_ativa', password='senha123')
    Group.objects.get_or_create(name=PASTOR_LOCAL)
    pastor.groups.add(Group.objects.get(name=PASTOR_LOCAL))

    dono = User.objects.create_user(username='dono_pastor_local_sem_ativa', password='senha123')
    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Pastor Local Sem Ativa',
        administrador_principal=dono,
        ativo=True,
        cnpj='77777777000177',
    )
    igreja = Igreja.objects.create(
        nome_igreja='Igreja Autorizada Sem Ativa',
        ministerio=ministerio,
        tipo_igreja='congregacao',
    )
    perfil = PerfilUsuario.objects.create(user=pastor, ministerio=ministerio)
    perfil.igrejas_permitidas.set([igreja])

    assert pode_acessar_secretaria(pastor)


@pytest.mark.django_db
def test_pastor_local_com_igreja_ativa_autorizada_pode_acessar_secretaria():
    from configuracao.models import PerfilUsuario

    User = get_user_model()
    pastor = User.objects.create_user(username='pastor_local_ativa_autorizada', password='senha123')
    Group.objects.get_or_create(name=PASTOR_LOCAL)
    pastor.groups.add(Group.objects.get(name=PASTOR_LOCAL))

    dono = User.objects.create_user(username='dono_pastor_local_ativa_autorizada', password='senha123')
    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Pastor Local Ativa',
        administrador_principal=dono,
        ativo=True,
        cnpj='88888888000188',
    )
    igreja = Igreja.objects.create(
        nome_igreja='Igreja Ativa Autorizada',
        ministerio=ministerio,
        tipo_igreja='congregacao',
    )
    perfil = PerfilUsuario.objects.create(user=pastor, ministerio=ministerio)
    perfil.igrejas_permitidas.set([igreja])

    assert pode_acessar_secretaria(pastor, igreja=igreja)


@pytest.mark.django_db
def test_pastor_local_com_igreja_fora_do_conjunto_autorizado_nao_acessa_secretaria():
    from configuracao.models import PerfilUsuario

    User = get_user_model()
    pastor = User.objects.create_user(username='pastor_local_fora_escopo', password='senha123')
    Group.objects.get_or_create(name=PASTOR_LOCAL)
    pastor.groups.add(Group.objects.get(name=PASTOR_LOCAL))

    dono = User.objects.create_user(username='dono_pastor_local_fora_escopo', password='senha123')
    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Pastor Local Fora Escopo',
        administrador_principal=dono,
        ativo=True,
        cnpj='99999999000199',
    )
    igreja_ok = Igreja.objects.create(nome_igreja='Igreja Ok', ministerio=ministerio, tipo_igreja='congregacao')
    igreja_fora = Igreja.objects.create(nome_igreja='Igreja Fora', ministerio=ministerio, tipo_igreja='congregacao')
    perfil = PerfilUsuario.objects.create(user=pastor, ministerio=ministerio)
    perfil.igrejas_permitidas.set([igreja_ok])

    assert not pode_acessar_secretaria(pastor, igreja=igreja_fora)


@pytest.mark.django_db
def test_pastor_local_com_igreja_de_outro_ministerio_nao_acessa_secretaria():
    from configuracao.models import PerfilUsuario

    User = get_user_model()
    pastor = User.objects.create_user(username='pastor_local_outro_min', password='senha123')
    Group.objects.get_or_create(name=PASTOR_LOCAL)
    pastor.groups.add(Group.objects.get(name=PASTOR_LOCAL))

    dono = User.objects.create_user(username='dono_pastor_local_outro_min', password='senha123')
    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Pastor Local Outro Min',
        administrador_principal=dono,
        ativo=True,
        cnpj='12121212000112',
    )
    outro_dono = User.objects.create_user(username='dono_outro_ministerio', password='senha123')
    outro_ministerio = Ministerio.objects.create(
        nome_fantasia='Outro Ministerio Pastor Local',
        administrador_principal=outro_dono,
        ativo=True,
        cnpj='34343434000134',
    )
    igreja_ok = Igreja.objects.create(
        nome_igreja='Igreja Ok Outro Min',
        ministerio=ministerio,
        tipo_igreja='congregacao',
    )
    igreja_outro_min = Igreja.objects.create(
        nome_igreja='Igreja Outro Min',
        ministerio=outro_ministerio,
        tipo_igreja='congregacao',
    )
    perfil = PerfilUsuario.objects.create(user=pastor, ministerio=ministerio)
    perfil.igrejas_permitidas.set([igreja_ok])

    assert not pode_acessar_secretaria(pastor, igreja=igreja_outro_min)


@pytest.mark.django_db
def test_pastor_local_com_igreja_regional_autorizada_nao_herda_subordinadas_na_secretaria():
    from configuracao.models import PerfilUsuario

    User = get_user_model()
    pastor = User.objects.create_user(username='pastor_local_regional_autorizada', password='senha123')
    Group.objects.get_or_create(name=PASTOR_LOCAL)
    pastor.groups.add(Group.objects.get(name=PASTOR_LOCAL))

    dono = User.objects.create_user(username='dono_pastor_local_regional_autorizada', password='senha123')
    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Pastor Local Regional',
        administrador_principal=dono,
        ativo=True,
        cnpj='56565656000156',
    )
    igreja_regional = Igreja.objects.create(
        nome_igreja='Regional Autorizada',
        ministerio=ministerio,
        tipo_igreja='regional',
    )
    igreja_sub = Igreja.objects.create(
        nome_igreja='Congregacao Subordinada',
        ministerio=ministerio,
        tipo_igreja='congregacao',
        igreja_superior=igreja_regional,
    )
    perfil = PerfilUsuario.objects.create(user=pastor, ministerio=ministerio)
    perfil.igrejas_permitidas.set([igreja_regional])

    assert pode_acessar_secretaria(pastor, igreja=igreja_regional)
    assert not pode_acessar_secretaria(pastor, igreja=igreja_sub)


@pytest.mark.django_db
def test_pastor_local_sem_igreja_explicita_nao_acessa_secretaria():
    from configuracao.models import PerfilUsuario

    User = get_user_model()
    pastor = User.objects.create_user(username='pastor_local_sem_igreja_explicita', password='senha123')
    Group.objects.get_or_create(name=PASTOR_LOCAL)
    pastor.groups.add(Group.objects.get(name=PASTOR_LOCAL))

    dono = User.objects.create_user(username='dono_pastor_local_sem_igreja_explicita', password='senha123')
    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Pastor Local Sem Igreja',
        administrador_principal=dono,
        ativo=True,
        cnpj='78787878000178',
    )
    PerfilUsuario.objects.create(user=pastor, ministerio=ministerio)

    assert not pode_acessar_secretaria(pastor)
