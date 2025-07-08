from django.db import models
from django.conf import settings
from configuracao.models import Organizacao

class Ticket(models.Model):
    """
    Modelo para um ticket de suporte aberto por um usuário.
    """
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('em_andamento', 'Em Andamento'),
        ('respondido', 'Respondido'),
        ('fechado', 'Fechado'),
    ]
    AREA_CHOICES = [
        ('duvida_geral', 'Dúvida Geral'),
        ('suporte_tecnico', 'Suporte Técnico'),
        ('financeiro_sistema', 'Financeiro/Assinatura'),
        ('sugestao_melhoria', 'Sugestão de Melhoria'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets_suporte', verbose_name="Usuário")
    organizacao = models.ForeignKey(Organizacao, on_delete=models.CASCADE, related_name='tickets_suporte', verbose_name="Organização")
    area = models.CharField(max_length=50, choices=AREA_CHOICES, default='duvida_geral', verbose_name="Área de Suporte")
    assunto = models.CharField(max_length=255, verbose_name="Assunto")
    mensagem = models.TextField(verbose_name="Mensagem")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto', verbose_name="Status")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    def __str__(self):
        return f"Ticket #{self.pk} - {self.assunto} ({self.user.username})"

    class Meta:
        verbose_name = "Ticket de Suporte"
        verbose_name_plural = "Tickets de Suporte"
        ordering = ['-data_criacao']

class RespostaTicket(models.Model):
    """
    Modelo para uma resposta a um ticket de suporte.
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='respostas', verbose_name="Ticket")
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Autor da Resposta")
    mensagem = models.TextField(verbose_name="Mensagem da Resposta")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")

    def __str__(self):
        autor_nome = self.autor.get_full_name() or self.autor.username if self.autor else "Sistema"
        return f"Resposta de {autor_nome} para o Ticket #{self.ticket.pk}"

    class Meta:
        verbose_name = "Resposta de Ticket"
        verbose_name_plural = "Respostas de Tickets"
        ordering = ['data_criacao']        