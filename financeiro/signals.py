from django.db.models.signals import post_save, pre_delete, pre_save # Adicionar pre_save aqui
from django.dispatch import receiver
from .models import Despesas, Receitas, ContaBancaria # Supondo que ContaBancaria está em models.py
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

def _atualizar_saldo_conta(conta_bancaria_id, valor_decimal, operacao, tipo_transacao):
    """
    Função auxiliar para atualizar o saldo de forma atômica e segura.
    operacao: 'adicionar' ou 'subtrair'
    tipo_transacao: 'despesa' ou 'receita' (para logging)
    """
    if conta_bancaria_id and valor_decimal is not None:
        try:
            with transaction.atomic():
                conta = ContaBancaria.objects.select_for_update().get(pk=conta_bancaria_id)
                saldo_anterior = conta.saldo_atual
                if operacao == 'adicionar':
                    conta.saldo_atual += valor_decimal
                elif operacao == 'subtrair':
                    conta.saldo_atual -= valor_decimal
                conta.save(update_fields=['saldo_atual'])
                logger.info(
                    f"Saldo da conta ID {conta.pk} ({conta.nome_identificacao}) atualizado de {saldo_anterior} "
                    f"para {conta.saldo_atual} devido a {tipo_transacao} de valor {valor_decimal} (op: {operacao})."
                )
        except ContaBancaria.DoesNotExist:
            logger.error(f"ContaBancaria ID {conta_bancaria_id} não encontrada ao tentar atualizar saldo para {tipo_transacao}.")
        except Exception as e:
            logger.exception(f"Erro ao atualizar saldo da ContaBancaria ID {conta_bancaria_id} para {tipo_transacao}: {e}")

@receiver(post_save, sender=Despesas)
def despesa_criada_ou_editada(sender, instance, created, **kwargs):
    if created:
        # Despesa nova: subtrai o valor da conta
        _atualizar_saldo_conta(instance.conta_bancaria_id, instance.valor, 'subtrair', 'nova despesa')
    else:
        # Despesa editada:
        # O pre_save abaixo já reverteu o valor antigo.
        # Agora aplicamos o novo valor da despesa editada.
        _atualizar_saldo_conta(instance.conta_bancaria_id, instance.valor, 'subtrair', 'edição de despesa (aplicar novo)')

@receiver(pre_save, sender=Despesas)
def despesa_antes_de_editar(sender, instance, **kwargs):
    if instance.pk: # Se a instância já existe (é uma edição)
        try:
            old_instance = Despesas.objects.get(pk=instance.pk)
            # Se a conta ou o valor mudou, precisamos reverter o efeito antigo
            if old_instance.conta_bancaria_id != instance.conta_bancaria_id or old_instance.valor != instance.valor:
                if old_instance.conta_bancaria_id:
                    # Reverte a despesa antiga (adiciona o valor de volta)
                    _atualizar_saldo_conta(old_instance.conta_bancaria_id, old_instance.valor, 'adicionar', 'edição de despesa (reverter antigo)')
        except Despesas.DoesNotExist:
            pass # Não faz nada se a instância antiga não existir

@receiver(pre_delete, sender=Despesas)
def despesa_excluida(sender, instance, **kwargs):
    # Despesa excluída: adiciona o valor de volta à conta
    _atualizar_saldo_conta(instance.conta_bancaria_id, instance.valor, 'adicionar', 'exclusão de despesa')

# --- Sinais para Receitas (lógica similar, mas invertida) ---
@receiver(post_save, sender=Receitas)
def receita_criada_ou_editada(sender, instance, created, **kwargs):
    if created:
        _atualizar_saldo_conta(instance.conta_bancaria_id, instance.valor, 'adicionar', 'nova receita')
    else:
        _atualizar_saldo_conta(instance.conta_bancaria_id, instance.valor, 'adicionar', 'edição de receita (aplicar novo)')

@receiver(pre_save, sender=Receitas)
def receita_antes_de_editar(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Receitas.objects.get(pk=instance.pk)
            if old_instance.conta_bancaria_id != instance.conta_bancaria_id or old_instance.valor != instance.valor:
                if old_instance.conta_bancaria_id:
                    _atualizar_saldo_conta(old_instance.conta_bancaria_id, old_instance.valor, 'subtrair', 'edição de receita (reverter antigo)')
        except Receitas.DoesNotExist:
            pass

@receiver(pre_delete, sender=Receitas)
def receita_excluida(sender, instance, **kwargs):
    _atualizar_saldo_conta(instance.conta_bancaria_id, instance.valor, 'subtrair', 'exclusão de receita')
