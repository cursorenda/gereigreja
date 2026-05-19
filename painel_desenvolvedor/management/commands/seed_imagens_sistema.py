"""
Management command para popular a galeria de imagens do sistema.

Insere automaticamente os ativos visuais estáticos do Gereigreja
(logos, favicon, avatar padrão, previews, etc.) na tabela SistemaImagem,
sem duplicar registros já existentes.

Uso:
    python manage.py seed_imagens_sistema
    python manage.py seed_imagens_sistema --dry-run
    python manage.py seed_imagens_sistema --force   # sobrescreve existentes
"""
import os
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from painel_desenvolvedor.models import SistemaImagem


# ---------------------------------------------------------------------------
# Mapeamento das imagens estáticas do sistema
# Cada entrada define: arquivo (relativo a STATICFILES_DIRS[0] ou BASE_DIR/static),
# tipo, variacao, descricao, notas e se deve ser marcada como ativa.
# ---------------------------------------------------------------------------
IMAGENS_DO_SISTEMA = [
    # ── Identidade / Favicon ───────────────────────────────────────────────
    {
        'arquivo': 'favicon.ico',
        'tipo': 'favicon',
        'variacao': 'original',
        'descricao': 'Favicon ICO do Gereigreja',
        'notas': (
            'Arquivo ICO multi-resolução (16×16, 32×32, 48×48). '
            'Referenciado em todos os base templates via rel="icon".'
        ),
        'ativo': True,
    },
    {
        'arquivo': 'favicon.svg',
        'tipo': 'favicon',
        'variacao': 'original',
        'descricao': 'Favicon SVG do Gereigreja',
        'notas': (
            'Versão vetorial — preferida por navegadores modernos. '
            'Substitui o ICO quando suportado.'
        ),
        'ativo': False,
    },

    # NOTA: static/img/logo1.png e logo2.png NÃO são logos da plataforma Gereigreja.
    # São logos da igreja/ministério ID 1, armazenados em static como fallback
    # para o relatório financeiro. Logos de clientes pertencem ao módulo
    # configuracao (campo Igreja.logo1 / Igreja.logo2), não aqui.

    # ── Avatar padrão ──────────────────────────────────────────────────────
    {
        'arquivo': 'img/default_avatar.png',
        'tipo': 'avatar_padrao',
        'variacao': 'original',
        'descricao': 'Avatar padrão de usuário/membro',
        'notas': (
            'Exibido em todos os pontos do sistema onde o membro '
            'ou usuário ainda não possui foto cadastrada '
            '(secretaria, suporte, menu, portal do membro).'
        ),
        'ativo': True,
    },
    {
        'arquivo': 'img/default_ministerio.png',
        'tipo': 'padrao_ministerio',
        'variacao': 'original',
        'descricao': 'Fallback Oficial de Ministério',
        'notas': (
            'Imagem ativa da galeria usada como fallback visual para Ministério '
            'quando não houver logo própria cadastrada em configuracao.Ministerio.logo.'
        ),
        'ativo': True,
    },
    {
        'arquivo': 'img/default_igreja.png',
        'tipo': 'padrao_igreja',
        'variacao': 'original',
        'descricao': 'Fallback Oficial de Igreja',
        'notas': (
            'Imagem ativa da galeria usada como fallback visual para Igreja '
            'quando não houver logo1/logo2 cadastradas em configuracao.Igreja.'
        ),
        'ativo': True,
    },

    # ── Preview do Dashboard (marketing) ──────────────────────────────────
    {
        'arquivo': 'img/dashboard_preview1.png',
        'tipo': 'dashboard_preview',
        'variacao': 'grande',
        'descricao': 'Preview do Dashboard — versão principal (landing page)',
        'notas': (
            'Imagem de destaque exibida na seção hero da landing page pública '
            '(contas/landing_page.html). Representa visualmente o produto.'
        ),
        'ativo': True,
    },
    {
        'arquivo': 'img/dashboard_preview.png',
        'tipo': 'dashboard_preview',
        'variacao': 'medio',
        'descricao': 'Preview do Dashboard — versão compacta',
        'notas': (
            'Versão menor do preview do dashboard. '
            'Reservada para uso em cards ou thumbnails.'
        ),
        'ativo': False,
    },
    {
        'arquivo': 'img/gereigreja_og_image.png',
        'tipo': 'og_image',
        'variacao': '1200x630',
        'descricao': 'Imagem Open Graph do Gereigreja',
        'notas': (
            'Usada em compartilhamentos sociais (Open Graph/Twitter) '
            'na landing page pública do Gereigreja.'
        ),
        'ativo': True,
    },

    # ── Placeholder / Ilustrações ─────────────────────────────────────────
    {
        'arquivo': 'assets/img/error-404-monochrome.svg',
        'tipo': 'placeholder',
        'variacao': 'original',
        'descricao': 'Ilustração de erro 404 (monocromática)',
        'notas': (
            'SVG exibido nas páginas de erro 404 do sistema. '
            'Estilo monocromático compatível com tema claro e escuro.'
        ),
        'ativo': True,
    },
]


def _encontrar_static_root():
    """
    Retorna o diretório base de arquivos estáticos do projeto.
    Tenta STATICFILES_DIRS primeiro, depois BASE_DIR/static.
    """
    dirs = getattr(settings, 'STATICFILES_DIRS', [])
    for d in dirs:
        p = Path(d)
        if p.is_dir():
            return p
    fallback = Path(settings.BASE_DIR) / 'static'
    if fallback.is_dir():
        return fallback
    return None


class Command(BaseCommand):
    help = (
        'Popula a galeria de Imagens do Sistema com os ativos '
        'estáticos do Gereigreja (logos, favicon, avatar, etc.).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas simula — não salva nada no banco.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recria registros mesmo se já existirem (substitui).',
        )

    # -----------------------------------------------------------------------

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        static_root = _encontrar_static_root()
        if not static_root:
            raise CommandError(
                'Diretório de arquivos estáticos não encontrado. '
                'Verifique STATICFILES_DIRS ou BASE_DIR/static.'
            )

        self.stdout.write(self.style.HTTP_INFO(
            f'\nDiretório estático: {static_root}'
        ))
        if dry_run:
            self.stdout.write(self.style.WARNING('  [DRY-RUN] Nenhum dado será salvo.\n'))

        criados = 0
        ignorados = 0
        erros = 0

        secao_atual = None

        for cfg in IMAGENS_DO_SISTEMA:
            # Cabeçalho de seção no output
            secao = dict(SistemaImagem.TIPO_CHOICES).get(cfg['tipo'], cfg['tipo'])
            if secao != secao_atual:
                secao_atual = secao
                self.stdout.write('')
                self.stdout.write(self.style.MIGRATE_HEADING(f'  ── {secao} ──'))

            arquivo_path = static_root / cfg['arquivo']

            if not arquivo_path.is_file():
                self.stdout.write(self.style.WARNING(
                    f'  [AUSENTE]  {cfg["arquivo"]} — arquivo não encontrado, pulando.'
                ))
                erros += 1
                continue

            # Verifica duplicata pela descricao (identificador legível único)
            existe = SistemaImagem.objects.filter(
                descricao=cfg['descricao']
            ).first()

            if existe and not force:
                self.stdout.write(
                    f'  [JÁ EXISTE] {cfg["descricao"]} (id={existe.pk})'
                )
                ignorados += 1
                continue

            if dry_run:
                self.stdout.write(self.style.SUCCESS(
                    f'  [SIMULADO]  {cfg["descricao"]} ← {cfg["arquivo"]}'
                ))
                criados += 1
                continue

            # Criação ou substituição
            try:
                if existe and force:
                    existe.delete()

                instancia = SistemaImagem(
                    tipo=cfg['tipo'],
                    variacao=cfg['variacao'],
                    descricao=cfg['descricao'],
                    notas=cfg.get('notas', ''),
                    ativo=cfg.get('ativo', False),
                )

                with open(arquivo_path, 'rb') as f:
                    nome_arquivo = arquivo_path.name
                    instancia.imagem.save(nome_arquivo, File(f), save=False)

                # Extrai dimensões para imagens raster
                try:
                    from PIL import Image as PILImage
                    extensao = arquivo_path.suffix.lower()
                    if extensao not in ('.svg', '.ico'):
                        with open(arquivo_path, 'rb') as f:
                            img = PILImage.open(f)
                            instancia.largura, instancia.altura = img.size
                except Exception:
                    pass  # dimensões são opcionais

                # Se ativo=True, garante que não haja outra ativa com mesmo tipo+variacao
                if instancia.ativo:
                    SistemaImagem.objects.filter(
                        tipo=instancia.tipo,
                        variacao=instancia.variacao,
                        ativo=True,
                    ).update(ativo=False)

                instancia.save()

                label_ativo = '✓ ativa' if instancia.ativo else '  inativa'
                dims = (
                    f' [{instancia.largura}×{instancia.altura}px]'
                    if instancia.largura else ''
                )
                self.stdout.write(self.style.SUCCESS(
                    f'  [CRIADO]    {cfg["descricao"]}{dims} ({label_ativo})'
                ))
                criados += 1

            except Exception as exc:
                self.stdout.write(self.style.ERROR(
                    f'  [ERRO]      {cfg["descricao"]}: {exc}'
                ))
                erros += 1

        # Resumo final
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING('  ── Resumo ──'))
        self.stdout.write(self.style.SUCCESS(f'  Criados:   {criados}'))
        if ignorados:
            self.stdout.write(f'  Ignorados: {ignorados} (já existiam)')
        if erros:
            self.stdout.write(self.style.WARNING(f'  Problemas: {erros}'))
        self.stdout.write('')
