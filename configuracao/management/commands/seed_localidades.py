from django.core.management.base import BaseCommand
from django.db import transaction
import requests

from configuracao.models import (
    CidadeCatalogo,
    CidadeTraducao,
    Pais,
    PaisTraducao,
    SubdivisaoAdministrativa,
    SubdivisaoTraducao,
    normalizar_texto_catalogo,
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
        parser.add_argument(
            '--brasil-completo',
            action='store_true',
            help='Importa todos os municipios do Brasil a partir da API publica do IBGE.',
        )
        parser.add_argument(
            '--ibge-timeout',
            type=int,
            default=60,
            help='Timeout (segundos) para chamadas HTTP ao IBGE no modo --brasil-completo.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        apenas_brasil = options['apenas_brasil']
        brasil_completo = options['brasil_completo']
        ibge_timeout = max(10, int(options['ibge_timeout'] or 60))

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

        ufs_map = self._seed_brasil(pais_br)

        if brasil_completo:
            self._seed_brasil_municipios_ibge(pais_br, ufs_map, timeout=ibge_timeout)

        if not apenas_brasil:
            self._seed_paises_base()

        self.stdout.write(self.style.SUCCESS('Catalogo de localidades carregado com sucesso.'))

    def _seed_brasil(self, pais_br):
        ufs_map = {}
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
            ufs_map[uf] = subdivisao

        return ufs_map

    def _seed_brasil_municipios_ibge(self, pais_br, ufs_map, timeout=60):
        self.stdout.write('Importando municipios do Brasil via IBGE...')

        response = requests.get(
            'https://servicodados.ibge.gov.br/api/v1/localidades/municipios',
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, list):
            raise RuntimeError('Resposta inesperada da API do IBGE para municipios.')

        nomes_por_uf = {uf: set() for uf in ufs_map.keys()}
        for item in payload:
            nome = (item or {}).get('nome')
            if not nome:
                continue
            nome = str(nome).strip()
            if not nome:
                continue

            microrregiao = (item or {}).get('microrregiao') or {}
            mesorregiao = microrregiao.get('mesorregiao') or {}
            uf_obj = mesorregiao.get('UF') or {}
            uf_sigla = (uf_obj.get('sigla') or '').strip().upper()
            if uf_sigla in nomes_por_uf:
                nomes_por_uf[uf_sigla].add(nome)

        total_novas = 0
        for uf, subdivisao in ufs_map.items():
            nomes = nomes_por_uf.get(uf) or set()
            if not nomes:
                continue

            existentes_norm = set(
                CidadeCatalogo.objects.filter(pais=pais_br, subdivisao=subdivisao).values_list('nome_normalizado', flat=True)
            )
            novos = []
            for nome in sorted(nomes):
                nome_norm = normalizar_texto_catalogo(nome)
                if nome_norm in existentes_norm:
                    continue
                existentes_norm.add(nome_norm)
                novos.append(
                    CidadeCatalogo(
                        pais=pais_br,
                        subdivisao=subdivisao,
                        nome=nome,
                        nome_normalizado=nome_norm,
                        ativo=True,
                    )
                )

            if novos:
                CidadeCatalogo.objects.bulk_create(novos, batch_size=1000)
                total_novas += len(novos)

        total_br = CidadeCatalogo.objects.filter(pais=pais_br).count()
        self.stdout.write(
            self.style.SUCCESS(
                f'IBGE importado com sucesso. Novas cidades: {total_novas}. Total BR no catalogo: {total_br}.'
            )
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
