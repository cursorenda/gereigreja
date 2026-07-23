# c:\Gereigreja\comunicacao\signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Aviso
from notificacoes.models import Notificacao
from configuracao.models import PerfilUsuario # Para pegar todos os usuários do ministério
from django.urls import reverse # Para gerar a URL da notificação

@receiver(post_save, sender=Aviso)
def create_aviso_notification(sender, instance, created, **kwargs):
    if created and instance.publicado:
        # Notificar todos os usuários do ministério
        ministerio = instance.ministerio
        users_in_org = [p.user for p in PerfilUsuario.objects.filter(ministerio=ministerio, user__is_active=True)]

        notification_url = reverse('comunicacao:detalhe_aviso', kwargs={'pk': instance.pk})

        for user in users_in_org:
            # Evitar notificar o próprio autor do aviso se ele não precisar ser notificado
            if user == instance.autor:
                continue # Ou crie uma notificação diferente para o autor

            Notificacao.objects.create(
                user=user,
                ministerio=ministerio,
                message=f"Um novo aviso foi publicado: '{instance.titulo}'",
                notification_type='aviso',
                url=notification_url,
                content_object=instance # Vincula a notificação ao objeto Aviso
            )


@receiver(post_save, sender='secretaria.Pessoa')
def enviar_whatsapp_novo_membro(sender, instance, created, **kwargs):
    if not created or not instance.igreja_id:
        return

    config = WhatsAppConfiguracao.objects.filter(
        igreja=instance.igreja,
        ministerio=instance.igreja.ministerio,
        ativo=True,
        auto_novos_membros=True,
    ).first()
    if not config or not instance.celular:
        return

    tipo_nome = (instance.tipo_pessoa.nome or '').lower() if instance.tipo_pessoa else ''
    if 'membro' not in tipo_nome:
        return

    mensagem = (
        f"Ola, {instance.nome}! Seja muito bem-vindo(a) a {instance.igreja.nome_igreja}. "
        "Estamos felizes por caminhar com voce."
    )
    try:
        send_whatsapp_text(
            config,
            instance.celular,
            mensagem,
            tipo='novo_membro',
            ministerio=instance.igreja.ministerio,
            igreja=instance.igreja,
            membro=instance,
        )
    except WhatsAppSendError:
        return


@receiver(post_save, sender='financeiro.Receitas')
def enviar_whatsapp_agradecimento_dizimo(sender, instance, created, **kwargs):
    # O agradecimento de dízimo passou a ser agendado no fechamento de caixa.
    return
