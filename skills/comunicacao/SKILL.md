---
name: "enviando-comunicacao"
description: "Envia e-mails, SMS e notificações para membros. Use para enviar mensagens em massa, notificações ou comunicados."
---

# Quando Usar Esta Skill

Use esta skill quando:
- Enviar e-mails ou SMS para membros
- Criar notificações do sistema
- Enviar comunicados em massa
- Usar templates de mensagem
- Agendar envios automáticos

## Estrutura de Dados

### Mensagem
```python
class Mensagem(models.Model):
    TIPO_CHOICES = [('email', 'E-mail'), ('sms', 'SMS'), ('notificacao', 'Notificação')]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    assunto = models.CharField(max_length=200)
    corpo = models.TextField()
    remetente = models.ForeignKey(User)
    destinatarios = models.ManyToManyField(Pessoa)
    data_envio = models.DateTimeField()
    enviado = models.BooleanField(default=False)
```

### Template de Mensagem
```python
class TemplateMensagem(models.Model):
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20)
    assunto = models.CharField(max_length=200)
    corpo = models.TextField()  # Usa placeholders: {{nome}}, {{data}}
```

## Exemplos de Uso

### Enviar E-mail Individual
```python
from django.core.mail import send_mail

def enviar_email_boas_vindas(pessoa):
    send_mail(
        subject='Bem-vindo ao Gereigreja!',
        message=f'Olá {pessoa.nome}, seja bem-vindo!',
        from_email='contato@igreja.com',
        recipient_list=[pessoa.email],
        fail_silently=False,
    )
```

### Enviar E-mail em Massa
```python
from django.core.mail import send_mass_mail

def enviar_comunicado(titulo, mensagem, destinatarios):
    emails = [
        (
            titulo,
            mensagem,
            'contato@igreja.com',
            [pessoa.email]
        )
        for pessoa in destinatarios if pessoa.email
    ]
    
    send_mass_mail(emails, fail_silently=False)
```

### Usar Template
```python
def enviar_com_template(template_id, pessoa, contexto):
    template = TemplateMensagem.objects.get(id=template_id)
    
    # Substituir placeholders
    assunto = template.assunto.format(**contexto)
    corpo = template.corpo.format(**contexto)
    
    send_mail(
        subject=assunto,
        message=corpo,
        from_email='contato@igreja.com',
        recipient_list=[pessoa.email]
    )
```

### Enviar SMS (via API)
```python
import requests

def enviar_sms(telefone, mensagem):
    response = requests.post(
        'https://api-sms.com/send',
        json={
            'to': telefone,
            'message': mensagem,
            'api_key': settings.SMS_API_KEY
        }
    )
    return response.json()
```

## Templates Comuns

### Boas-Vindas
```
Assunto: Bem-vindo(a) à {{igreja}}!

Olá {{nome}},

É com grande alegria que damos as boas-vindas!

Estamos felizes em tê-lo(a) conosco.

Deus abençoe!
{{igreja}}
```

### Lembrete de Evento
```
Assunto: Lembrete: {{evento}} amanhã!

Olá {{nome}},

Lembramos que amanhã ({{data}}) teremos {{evento}}.

Local: {{local}}
Horário: {{horario}}

Contamos com sua presença!
```

## Configuração de E-mail (Django)

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha'
DEFAULT_FROM_EMAIL = 'noreply@igreja.com'
```

## Boas Práticas

1. **Sempre validar e-mails** antes de enviar
2. **Usar templates** para mensagens recorrentes
3. **Respeitar LGPD** - permitir descadastro
4. **Não enviar spam** - limite de envios por dia
5. **Logs de envio** - registrar todas as mensagens
6. **Tratar erros** - `fail_silently=False` para debug
7. **E-mails HTML** - usar `send_html_mail` quando necessário
