from django.db.models.signals import post_save
from django.dispatch import receiver
from configuracao.models import Ministerio
from financeiro.models import CategoriaDespesa

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
