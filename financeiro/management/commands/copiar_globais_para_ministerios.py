from django.core.management.base import BaseCommand
from configuracao.models import Ministerio, Igreja
from financeiro.models import CategoriaDespesa, Fornecedor, ContaBancaria
from django.db import transaction

class Command(BaseCommand):
    help = 'Copia dados globais (categorias, fornecedores, contas bancárias) para todos os ministérios/igrejas existentes.'

    def handle(self, *args, **options):
        import logging
        logger = logging.getLogger('copiar_globais')
        self.stdout.write(self.style.NOTICE('Iniciando cópia dos dados globais para todos os ministérios/igrejas...'))
        with transaction.atomic():
            # Categorias
            globais_cat = list(CategoriaDespesa.objects.filter(padrao_global=True))
            for ministerio in Ministerio.objects.all():
                for cat in globais_cat:
                    obj, created = CategoriaDespesa.objects.get_or_create(
                        ministerio=ministerio,
                        nome=cat.nome
                    )
                    if created:
                        msg = f"Categoria '{cat.nome}' criada para Ministério '{ministerio.nome_fantasia}'"
                        self.stdout.write(self.style.SUCCESS(msg))
                        logger.info(msg)
                    else:
                        logger.info(f"Categoria '{cat.nome}' já existia para Ministério '{ministerio.nome_fantasia}'")
            # Fornecedores
            globais_forn = list(Fornecedor.objects.filter(padrao_global=True))
            for ministerio in Ministerio.objects.all():
                for forn in globais_forn:
                    obj, created = Fornecedor.objects.get_or_create(
                        ministerio=ministerio,
                        nome=forn.nome,
                        defaults={
                            'cnpj_cpf': forn.cnpj_cpf,
                            'telefone': forn.telefone,
                            'email': forn.email,
                            'endereco': forn.endereco,
                            'observacoes': forn.observacoes,
                            'ativo': forn.ativo
                        }
                    )
                    if created:
                        msg = f"Fornecedor '{forn.nome}' criado para Ministério '{ministerio.nome_fantasia}'"
                        self.stdout.write(self.style.SUCCESS(msg))
                        logger.info(msg)
                    else:
                        logger.info(f"Fornecedor '{forn.nome}' já existia para Ministério '{ministerio.nome_fantasia}'")
            # Contas Bancárias
            globais_conta = list(ContaBancaria.objects.filter(padrao_global=True))
            for igreja in Igreja.objects.all():
                for conta in globais_conta:
                    obj, created = ContaBancaria.objects.get_or_create(
                        igreja=igreja,
                        nome_identificacao=conta.nome_identificacao,
                        defaults={
                            'tipo': conta.tipo,
                            'instituicao_bancaria': conta.instituicao_bancaria,
                            'agencia': conta.agencia,
                            'conta': conta.conta,
                            'saldo_inicial': 0,
                            'saldo_atual': 0
                        }
                    )
                    if created:
                        msg = f"Conta Bancária '{conta.nome_identificacao}' criada para Igreja '{igreja.nome_igreja}'"
                        self.stdout.write(self.style.SUCCESS(msg))
                        logger.info(msg)
                    else:
                        logger.info(f"Conta Bancária '{conta.nome_identificacao}' já existia para Igreja '{igreja.nome_igreja}'")
        self.stdout.write(self.style.SUCCESS('Cópia concluída!'))
