from configuracao.models import ConfiguracaoSistema, Ministerio
from django.core.management.base import BaseCommand
from django.utils import timezone
from agenda.models import AgendaEvento
from secretaria.models import Membro

from django.core.mail import send_mail
from django.conf import settings
from comunicacao.models import NotificacaoEnviada

class Command(BaseCommand):
    help = 'Envia notificações automáticas do sistema (eventos, aniversários, etc)'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando envio de notificações automáticas...')
        self.notificar_eventos_proximos()
        self.notificar_aniversariantes()
        # Adicione aqui outras funções de notificação
        self.stdout.write(self.style.SUCCESS('Notificações enviadas com sucesso.'))

    def notificar_eventos_proximos(self):
        agora = timezone.now()
        daqui_1_dia = agora + timezone.timedelta(days=1)
        eventos = AgendaEvento.objects.filter(data_inicio__gte=agora, data_inicio__lte=daqui_1_dia)
        for evento in eventos:
            ministerio = None
            if evento.responsavel and hasattr(evento.responsavel, 'perfil'):
                ministerio = getattr(evento.responsavel.perfil, 'ministerio', None)
            if not ministerio:
                continue  # Não envia se não conseguir identificar o ministério
            try:
                config = ConfiguracaoSistema.objects.get(ministerio=ministerio)
            except ConfiguracaoSistema.DoesNotExist:
                continue  # Não envia se não houver configuração
            if not config.notificar_eventos:
                continue  # Notificações de eventos desativadas
            if evento.responsavel and evento.responsavel.email:
                subject = f'Lembrete: Evento "{evento.titulo}" amanhã'
                message = f'O evento "{evento.titulo}" ocorrerá em breve. Data/hora: {evento.data_inicio.astimezone(timezone.get_current_timezone()).strftime("%d/%m/%Y %H:%M")}'
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[evento.responsavel.email],
                    fail_silently=True,
                )
                NotificacaoEnviada.objects.create(
                    tipo='evento',
                    titulo=evento.titulo,
                    mensagem=message,
                    destinatario=evento.responsavel.email,
                    usuario=evento.responsavel if hasattr(evento, 'responsavel') else None
                )

    def notificar_aniversariantes(self):
        hoje = timezone.localdate()
        aniversariantes = Membro.objects.filter(nascimento__month=hoje.month, nascimento__day=hoje.day)
        for membro in aniversariantes:
            ministerio = None
            if hasattr(membro, 'igreja') and membro.igreja and hasattr(membro.igreja, 'ministerio'):
                ministerio = membro.igreja.ministerio
            if not ministerio:
                continue  # Não envia se não conseguir identificar o ministério
            try:
                config = ConfiguracaoSistema.objects.get(ministerio=ministerio)
            except ConfiguracaoSistema.DoesNotExist:
                continue  # Não envia se não houver configuração
            if not config.notificar_aniversarios:
                continue  # Notificações de aniversários desativadas
            if membro.email:
                subject = 'Feliz aniversário!'
                message = f'Parabéns, {membro.nome}! Que Deus te abençoe neste novo ciclo.'
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[membro.email],
                    fail_silently=True,
                )
                NotificacaoEnviada.objects.create(
                    tipo='aniversario',
                    titulo='Feliz aniversário!',
                    mensagem=message,
                    destinatario=membro.email,
                    usuario=membro.usuario if hasattr(membro, 'usuario') else None
                )
