from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from types import SimpleNamespace
from .models import PerfilUsuario, Ministerio, Igreja, ConfiguracaoSistema
# Cria automaticamente uma igreja ao criar um novo Ministério
from django.db import transaction

@receiver(post_save, sender=Ministerio)
def criar_igreja_para_novo_ministerio(sender, instance, created, **kwargs):
    if created:
        # Evita duplicidade caso o signal rode mais de uma vez
        if not Igreja.objects.filter(ministerio=instance).exists():
            with transaction.atomic():
                Igreja.objects.create(
                    ministerio=instance,
                    nome_igreja=instance.nome_fantasia,
                    tipo_igreja='sede'
                )


@receiver(pre_save, sender=ConfiguracaoSistema)
def registrar_estado_anterior_configuracao_ebd(sender, instance, **kwargs):
    if not instance.pk:
        return

    anterior = ConfiguracaoSistema.objects.filter(pk=instance.pk).only('ebd_periodo', 'ebd_dia_semana', 'ebd_horario').first()
    if anterior is None:
        return

    instance._old_ebd_periodo = anterior.ebd_periodo
    instance._old_ebd_dia_semana = anterior.ebd_dia_semana
    instance._old_ebd_horario = anterior.ebd_horario


@receiver(pre_save, sender=Igreja)
def registrar_estado_anterior_configuracao_ebd_igreja(sender, instance, **kwargs):
    if not instance.pk:
        return

    anterior = Igreja.objects.filter(pk=instance.pk).only('ebd_periodo', 'ebd_dia_semana', 'ebd_horario').first()
    if anterior is None:
        return

    instance._old_ebd_periodo = anterior.ebd_periodo
    instance._old_ebd_dia_semana = anterior.ebd_dia_semana
    instance._old_ebd_horario = anterior.ebd_horario


def _disparar_auto_sync_ebd_configuracao(instance):
    from escola_biblica.views import auto_sync_ebd_periodos_e_licoes
    from escola_biblica.services_agenda import sync_eventos_ebd_por_ministerio
    from configuracao.models import Igreja

    igreja_ativa = instance if isinstance(instance, Igreja) else None

    fake_request = SimpleNamespace(
        user=SimpleNamespace(
            is_authenticated=True,
            is_superuser=True,
            pk=getattr(instance.ministerio, 'pk', None),
            perfil=SimpleNamespace(ministerio=instance.ministerio),
            perfil_usuario=SimpleNamespace(ministerio=instance.ministerio),
        ),
        session={},
        igrejas_permitidas=Igreja.objects.filter(ministerio=instance.ministerio),
        igreja_ativa=igreja_ativa,
    )
    auto_sync_ebd_periodos_e_licoes(fake_request, force=True)
    sync_eventos_ebd_por_ministerio(instance.ministerio)


@receiver(post_save, sender=ConfiguracaoSistema)
def disparar_auto_sync_ebd_apos_configuracao(sender, instance, created, **kwargs):
    antigo_periodo = getattr(instance, '_old_ebd_periodo', None)
    antigo_dia = getattr(instance, '_old_ebd_dia_semana', None)
    antigo_horario = getattr(instance, '_old_ebd_horario', None)
    mudou_ebd = (
        created
        or antigo_periodo != instance.ebd_periodo
        or antigo_dia != instance.ebd_dia_semana
        or antigo_horario != instance.ebd_horario
    )

    if not mudou_ebd:
        return

    transaction.on_commit(lambda: _disparar_auto_sync_ebd_configuracao(instance))


@receiver(post_save, sender=Igreja)
def disparar_auto_sync_ebd_apos_configuracao_igreja(sender, instance, created, **kwargs):
    antigo_periodo = getattr(instance, '_old_ebd_periodo', None)
    antigo_dia = getattr(instance, '_old_ebd_dia_semana', None)
    antigo_horario = getattr(instance, '_old_ebd_horario', None)
    mudou_ebd = (
        created
        or antigo_periodo != instance.ebd_periodo
        or antigo_dia != instance.ebd_dia_semana
        or antigo_horario != instance.ebd_horario
    )

    if not mudou_ebd or instance.ministerio is None:
        return

    transaction.on_commit(lambda: _disparar_auto_sync_ebd_configuracao(instance))

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_perfilusuario_for_new_user(sender, instance, created, **kwargs):
    """
    Cria automaticamente um PerfilUsuario para cada novo usuário.
    Se já existir, não faz nada.
    """
    if created:
        # Tenta obter o ministério padrão (opcional, pode ser None)
        ministerio = getattr(instance, 'ministerio', None)
        if ministerio is not None:
            PerfilUsuario.objects.get_or_create(user=instance, defaults={'ministerio': ministerio})

# Função utilitária para garantir/atualizar perfil ao aceitar convite
# (pode ser chamada no fluxo de aceite do convite)
def garantir_perfilusuario(user, ministerio):
    perfil, created = PerfilUsuario.objects.get_or_create(user=user, defaults={'ministerio': ministerio})
    if not created and perfil.ministerio != ministerio:
        perfil.ministerio = ministerio
        perfil.save()
    return perfil
