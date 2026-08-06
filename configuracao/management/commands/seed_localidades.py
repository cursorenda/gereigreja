from django.core.management.base import BaseCommand
from django.db import transaction

from configuracao.models import (
    CidadeCatalogo,
    CidadeTraducao,
    Pais,
    PaisTraducao,
    SubdivisaoAdministrativa,
    SubdivisaoTraducao,
)


BR_ESTADOS_CAPITAIS = [
    ('AC', 'Acre', 'Rio Branco'),
    ('AL', 'Alagoas', 'Maceio'),
    ('AP', 'Amapa', 'Macapa'),
    ('AM', 'Amazonas', 'Manaus'),
    ('BA', 'Bahia', 'Salvador'),
    ('CE', 'Ceara', 'Fortaleza'),
    ('DF', 'Distrito Federal', 'Brasilia'),
    ('ES', 'Espirito Santo', 'Vitoria'),
    ('GO', 'Goias', 'Goiania'),
    ('MA', 'Maranhao', 'Sao Luis'),
    ('MT', 'Mato Grosso', 'Cuiaba'),
    ('MS', 'Mato Grosso do Sul', 'Campo Grande'),
    ('MG', 'Minas Gerais', 'Belo Horizonte'),
    ('PA', 'Para', 'Belem'),
    ('PB', 'Paraiba', 'Joao Pessoa'),
    ('PR', 'Parana', 'Curitiba'),
    ('PE', 'Pernambuco', 'Recife'),
    ('PI', 'Piaui', 'Teresina'),
    ('RJ', 'Rio de Janeiro', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte', 'Natal'),
    ('RS', 'Rio Grande do Sul', 'Porto Alegre'),
    ('RO', 'Rondonia', 'Porto Velho'),
    ('RR', 'Roraima', 'Boa Vista'),
    ('SC', 'Santa Catarina', 'Florianopolis'),
    ('SP', 'Sao Paulo', 'Sao Paulo'),
    ('SE', 'Sergipe', 'Aracaju'),
    ('TO', 'Tocantins', 'Palmas'),
]


class Command(BaseCommand):
    help = 'Carrega catálogo global de localidades (base internacional + Brasil inicial).'

    def add_arguments(self, parser):
        parser.add_argument('--apenas-brasil', action='store_true', help='Carrega somente o catálogo inicial brasileiro.')

    @transaction.atomic
    def handle(self, *args, **options):
        apenas_brasil = options['apenas_brasil']

        pais_br, _ = Pais.objects.update_or_create(
            codigo_iso2='BR',
            defaults={
                'codigo_iso3': 'BRA',
                'nome_oficial': 'Brasil',
                'nome_curto': 'Brasil',
                'idioma_padrao': 'pt-BR',
                'ativo': True,
            },
        )
        PaisTraducao.objects.update_or_create(
            pais=pais_br,
            idioma='pt-BR',
            defaults={'nome': 'Brasil'},
        )
        PaisTraducao.objects.update_or_create(
            pais=pais_br,
            idioma='en-US',
            defaults={'nome': 'Brazil'},
        )

        self._seed_brasil(pais_br)

        if not apenas_brasil:
            self._seed_paises_base()

        self.stdout.write(self.style.SUCCESS('Catalogo de localidades carregado com sucesso.'))

    def _seed_brasil(self, pais_br):
        for uf, nome_estado, capital in BR_ESTADOS_CAPITAIS:
            subdivisao, _ = SubdivisaoAdministrativa.objects.update_or_create(
                pais=pais_br,
                codigo=uf,
                defaults={
                    'nome': nome_estado,
                    'nivel': SubdivisaoAdministrativa.NIVEL_ESTADO,
                    'ativo': True,
                },
            )
            SubdivisaoTraducao.objects.update_or_create(
                subdivisao=subdivisao,
                idioma='pt-BR',
                defaults={'nome': nome_estado},
            )
            SubdivisaoTraducao.objects.update_or_create(
                subdivisao=subdivisao,
                idioma='en-US',
                defaults={'nome': nome_estado},
            )

            cidade, _ = CidadeCatalogo.objects.update_or_create(
                pais=pais_br,
                subdivisao=subdivisao,
                nome=capital,
                defaults={'ativo': True},
            )
            CidadeTraducao.objects.update_or_create(
                cidade=cidade,
                idioma='pt-BR',
                defaults={'nome': capital},
            )
            CidadeTraducao.objects.update_or_create(
                cidade=cidade,
                idioma='en-US',
                defaults={'nome': capital},
            )

    def _seed_paises_base(self):
        base = [
            ('US', 'USA', 'United States', 'United States', 'en-US', 'Estados Unidos'),
            ('PT', 'PRT', 'Portugal', 'Portugal', 'pt-PT', 'Portugal'),
            ('ES', 'ESP', 'Spain', 'Spain', 'es-ES', 'Espanha'),
        ]
        for iso2, iso3, nome_oficial_en, nome_curto_en, idioma_padrao, nome_pt in base:
            pais, _ = Pais.objects.update_or_create(
                codigo_iso2=iso2,
                defaults={
                    'codigo_iso3': iso3,
                    'nome_oficial': nome_oficial_en,
                    'nome_curto': nome_curto_en,
                    'idioma_padrao': idioma_padrao,
                    'ativo': True,
                },
            )
            PaisTraducao.objects.update_or_create(pais=pais, idioma='en-US', defaults={'nome': nome_oficial_en})
            PaisTraducao.objects.update_or_create(pais=pais, idioma='pt-BR', defaults={'nome': nome_pt})
