
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=None)
def criar_conta_bancaria_padrao_igreja(sender, instance, created, **kwargs):
    # Importa models apenas quando o signal for executado
    from configuracao.models import Igreja
    from financeiro.models import ContaBancaria
    if sender is Igreja and created:
        ContaBancaria.objects.create(
            igreja=instance,
            nome_identificacao="Caixa Principal",
            tipo="caixa_fisico",
            saldo_inicial=0,
            saldo_atual=0,
            is_principal=True
        )
