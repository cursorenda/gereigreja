from decimal import Decimal

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from configuracao.models import Igreja, Ministerio
from financeiro.models import (
    CategoriaDespesa,
    Despesas,
    FechamentoCaixa,
    LogTransacaoFinanceira,
    Receitas,
    TransferenciaCaixa,
)
from financeiro.services import DepartamentoFinanceiroService

@receiver(post_save, sender=Ministerio)
def criar_categorias_padrao_ministerio(sender, instance, created, **kwargs):
    if created:
        # Copia categorias padrão global
        for cat in CategoriaDespesa.objects.filter(padrao_global=True):
            CategoriaDespesa.objects.get_or_create(ministerio=instance, nome=cat.nome)
        # Copia fornecedores padrão global
        from financeiro.models import Fornecedor, ContaBancaria
        for forn in Fornecedor.objects.filter(padrao_global=True):
            Fornecedor.objects.get_or_create(
                ministerio=instance,
                nome=forn.nome,
                cnpj_cpf=forn.cnpj_cpf,
                telefone=forn.telefone,
                email=forn.email,
                endereco=forn.endereco,
                observacoes=forn.observacoes,
                ativo=forn.ativo
            )
    # (Removido) Não criar contas bancárias padrão global aqui, pois não há igreja ainda.


@receiver(post_save, sender=Igreja)
def criar_departamentos_padrao_igreja(sender, instance, created, **kwargs):
    if not created:
        return
    DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(instance)


def _extrair_igreja(instance):
    if hasattr(instance, 'igreja') and instance.igreja_id:
        return instance.igreja
    if hasattr(instance, 'caixa_origem') and instance.caixa_origem_id:
        return instance.caixa_origem.igreja
    if hasattr(instance, 'caixa_destino') and instance.caixa_destino_id:
        return instance.caixa_destino.igreja
    return None


def _extrair_usuario(instance):
    if hasattr(instance, 'usuario') and getattr(instance, 'usuario_id', None):
        return instance.usuario
    if hasattr(instance, 'usuario_registro_pagamento') and getattr(instance, 'usuario_registro_pagamento_id', None):
        return instance.usuario_registro_pagamento
    return None


def _extrair_valor(instance):
    if hasattr(instance, 'valor'):
        return instance.valor
    if hasattr(instance, 'saldo_final'):
        return instance.saldo_final
    return Decimal('0.00')


def _registrar_log(instance, tipo_lancamento, acao):
    igreja = _extrair_igreja(instance)
    if igreja is None:
        return

    LogTransacaoFinanceira.objects.create(
        igreja=igreja,
        usuario=_extrair_usuario(instance),
        tipo_lancamento=tipo_lancamento,
        acao=acao,
        referencia_modelo=instance.__class__.__name__,
        referencia_id=instance.pk or 0,
        valor=_extrair_valor(instance),
        detalhes=str(instance),
    )


@receiver(post_save, sender=Receitas)
def auditar_receita_save(sender, instance, created, **kwargs):
    _registrar_log(instance, 'receita', 'criado' if created else 'atualizado')


@receiver(post_delete, sender=Receitas)
def auditar_receita_delete(sender, instance, **kwargs):
    _registrar_log(instance, 'receita', 'excluido')


@receiver(post_save, sender=Despesas)
def auditar_despesa_save(sender, instance, created, **kwargs):
    _registrar_log(instance, 'despesa', 'criado' if created else 'atualizado')


@receiver(post_delete, sender=Despesas)
def auditar_despesa_delete(sender, instance, **kwargs):
    _registrar_log(instance, 'despesa', 'excluido')


@receiver(post_save, sender=TransferenciaCaixa)
def auditar_transferencia_save(sender, instance, created, **kwargs):
    _registrar_log(instance, 'transferencia', 'criado' if created else 'atualizado')


@receiver(post_delete, sender=TransferenciaCaixa)
def auditar_transferencia_delete(sender, instance, **kwargs):
    _registrar_log(instance, 'transferencia', 'excluido')


@receiver(post_save, sender=FechamentoCaixa)
def auditar_fechamento_save(sender, instance, created, **kwargs):
    _registrar_log(instance, 'fechamento', 'criado' if created else 'atualizado')


@receiver(post_delete, sender=FechamentoCaixa)
def auditar_fechamento_delete(sender, instance, **kwargs):
    _registrar_log(instance, 'fechamento', 'excluido')
