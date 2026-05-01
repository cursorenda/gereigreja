from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from configuracao.models import Ministerio, Igreja
from secretaria.models import Pessoa, TipoPessoa, StatusPessoa
from financeiro.models import Despesas, Receitas

class Command(BaseCommand):
    help = 'Remove todos os dados de demonstração (modo demo) para resetar o ambiente.'

    def handle(self, *args, **options):

        # Remove receitas/despesas demo PRIMEIRO para evitar ProtectedError
        Receitas.objects.filter(observacao__icontains='Demo').delete()
        Despesas.objects.filter(observacao__icontains='Demo').delete()

        # Remove participações e eventos demo antes de remover igrejas demo
        try:
            from eventos.models import Evento, ParticipacaoEvento
            # Remove participações de eventos demo
            ParticipacaoEvento.objects.filter(evento__titulo__icontains='DEMO').delete()
            # Remove eventos demo
            Evento.objects.filter(titulo__icontains='DEMO').delete()
        except Exception as e:
            self.stderr.write(f'Erro ao remover eventos demo: {e}')

        # Remove membros demo
        Pessoa.objects.filter(email__icontains='@demo.com').delete()

        # Remove igrejas demo
        Igreja.objects.filter(nome_igreja__icontains='DEMO').delete()

        # Remove ministério demo
        Ministerio.objects.filter(nome_fantasia='DEMONSTRAÇÃO').delete()

        # Remove tipos/status demo criados
        TipoPessoa.objects.filter(nome='Membro', descricao__icontains='demo').delete()
        StatusPessoa.objects.filter(nome='Ativo', descricao__icontains='demo').delete()

        # Remove usuários demo
        User = get_user_model()
        User.objects.filter(username__icontains='demo').delete()

        self.stdout.write(self.style.SUCCESS('Dados demo removidos com sucesso!'))
