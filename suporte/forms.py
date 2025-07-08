from django import forms
from .models import Ticket, RespostaTicket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['area', 'assunto', 'mensagem']
        widgets = {
            'area': forms.Select(attrs={'class': 'form-select'}),
            'assunto': forms.TextInput(attrs={'class': 'form-control'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }
        labels = {
            'area': 'Sobre qual área você precisa de ajuda?',
            'assunto': 'Qual o assunto principal?',
            'mensagem': 'Descreva sua dúvida ou problema com o máximo de detalhes possível.',
        }

class RespostaTicketForm(forms.ModelForm):
    """
    Formulário para o usuário adicionar uma nova resposta a um ticket existente.
    """
    class Meta:
        model = RespostaTicket
        fields = ['mensagem']
        widgets = {
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Digite sua resposta aqui...'}),
        }
        labels = {
            'mensagem': 'Sua Resposta',
        }
