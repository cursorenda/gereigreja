from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core import signing
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import reverse
from django.shortcuts import redirect, render
from django.utils import formats
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt

from contas.constants import ADMIN_MINISTERIO, LIDERANCA_SECRETARIA, user_tem_qualquer_grupo
from core.decorators import page_access_required
from core.utils import get_ministerio_or_error
from secretaria.models import InfoEclesiastica, Membro
from secretaria.utils import get_allowed_churches_for_membros
from secretaria.views._helpers import get_request_scoped_churches


def _formatar_data_br(data_obj):
    if not data_obj:
        return ''
    return formats.date_format(data_obj, 'd/m/Y')


def _texto_ou_nao_informado(valor):
    texto = (str(valor).strip() if valor is not None else '')
    return texto or 'Nao informado'


def _gerar_token_validacao(membro, ministerio_id, data_emissao):
    if not membro:
        return ''
    payload = f"{membro.pk}|{ministerio_id}|{data_emissao.isoformat()}"
    signer = signing.TimestampSigner(salt='secretaria.carteirinha.qr')
    return signer.sign(payload)


def _montar_url_validacao(request, token):
    if not token:
        return ''
    path = reverse('secretaria:carteirinha_validar_qr', kwargs={'token': token})
    return request.build_absolute_uri(path)


@login_required
@page_access_required('dashboard_secretaria')
@xframe_options_exempt
def carteirinha_premium_1(request):
    return _render_carteirinha_premium(request)


def _render_carteirinha_premium(request):
    try:
        ministerio = get_ministerio_or_error(request)
    except (PermissionDenied, Http404):
        return redirect('secretaria:dashboard')

    permitir_secretaria_local = bool(getattr(ministerio, 'carteirinha_permitir_secretaria_local', False))
    eh_secretaria_central = user_tem_qualquer_grupo(request.user, [ADMIN_MINISTERIO, LIDERANCA_SECRETARIA])
    if eh_secretaria_central and request.path.startswith('/secretaria/documentos/carteirinha/premium-1/'):
        destino = reverse('configuracao:carteirinha_ministerio')
        qs = request.GET.urlencode()
        if qs:
            destino = f"{destino}?{qs}"
        return redirect(destino)
    if not permitir_secretaria_local and not eh_secretaria_central:
        messages.error(
            request,
            'A emissao de carteirinhas esta centralizada na Secretaria Ministerial. Procure a administracao do ministerio.'
        )
        return redirect('secretaria:dashboard')

    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    scoped_churches = get_request_scoped_churches(request, allowed_churches)
    churches_for_members = scoped_churches if scoped_churches.exists() else allowed_churches

    membros_qs = (
        Membro.objects
        .filter(igreja__in=churches_for_members)
        .select_related('igreja', 'tipo_pessoa', 'status_pessoa')
        .order_by('nome')
    )

    membro_id = (request.GET.get('membro') or '').strip()
    membro_id_normalizado = ''.join(ch for ch in membro_id if ch.isdigit())
    membro = None
    if membro_id_normalizado:
        membro = membros_qs.filter(pk=int(membro_id_normalizado)).first()
    if membro is None:
        membro = membros_qs.first()

    info_eclesiastica = None
    if membro:
        info_eclesiastica = (
            InfoEclesiastica.objects
            .filter(membro_id=membro.pk)
            .order_by('-id')
            .first()
        )

    cargo_grau = ''
    if membro:
        cargo_grau = (
            membro.get_grau_eclesiastico_display()
            if getattr(membro, 'grau_eclesiastico', None)
            else ''
        )
        if not cargo_grau and getattr(membro, 'tipo_pessoa', None):
            cargo_grau = membro.tipo_pessoa.nome

    data_batismo = ''
    if info_eclesiastica and getattr(info_eclesiastica, 'data_batismo', None):
        data_batismo = _formatar_data_br(info_eclesiastica.data_batismo)
    elif membro and getattr(membro, 'data_entrada', None):
        data_batismo = _formatar_data_br(membro.data_entrada)

    logo_ministerio_url = ''
    try:
        if getattr(ministerio, 'logo_png', None):
            logo_ministerio_url = ministerio.logo_png.url
        elif getattr(ministerio, 'logo_pequeno', None):
            logo_ministerio_url = ministerio.logo_pequeno.url
        elif getattr(ministerio, 'logo_grande', None):
            logo_ministerio_url = ministerio.logo_grande.url
        elif getattr(ministerio, 'logo_url', None):
            logo_ministerio_url = ministerio.logo_url
    except Exception:
        logo_ministerio_url = ''

    data_emissao = timezone.localdate()
    token_validacao = _gerar_token_validacao(
        membro=membro,
        ministerio_id=getattr(ministerio, 'pk', ''),
        data_emissao=data_emissao,
    )
    qr_validation_url = _montar_url_validacao(request, token_validacao)

    context = {
        'ministerio': ministerio,
        'nome_ministerio': (ministerio.nome_fantasia or '').strip(),
        'logo_ministerio_url': logo_ministerio_url,
        'membros_disponiveis': membros_qs[:500],
        'membro_selecionado_id': str(membro.pk) if membro else '',
        'membro': membro,
        'nome_membro': membro.nome if membro else 'Selecione um membro',
        'cargo_grau': cargo_grau or 'Sem cargo definido',
        'data_batismo': data_batismo or 'Nao informado',
        'data_nascimento': _formatar_data_br(getattr(membro, 'nascimento', None)) if membro else '',
        'data_emissao': _formatar_data_br(data_emissao),
        'cpf_membro': _texto_ou_nao_informado(getattr(membro, 'cpf', '')) if membro else 'Nao informado',
        'rg_membro': _texto_ou_nao_informado(getattr(membro, 'rg', '')) if membro else 'Nao informado',
        'nome_pai': _texto_ou_nao_informado(getattr(membro, 'nome_pai', '')) if membro else 'Nao informado',
        'nome_mae': _texto_ou_nao_informado(getattr(membro, 'nome_mae', '')) if membro else 'Nao informado',
        'numero_id_membro': _texto_ou_nao_informado(getattr(membro, 'pk', '')) if membro else 'Nao informado',
        'nome_congregacao': _texto_ou_nao_informado(getattr(getattr(membro, 'igreja', None), 'nome_igreja', '')) if membro else 'Nao informado',
        'qr_validation_url': qr_validation_url,
        'can_personalizar_carteirinha': eh_secretaria_central,
    }
    response = render(request, 'configuracao/ministerio/carteirinha_ministerio_editor.html', context)
    # Permite preview em iframe na mesma origem (aba Carteirinha em Configuracoes do Ministerio).
    response['X-Frame-Options'] = 'SAMEORIGIN'
    response['Content-Security-Policy'] = "frame-ancestors 'self'"
    return response


def validar_carteirinha_qr(request, token):
    signer = signing.TimestampSigner(salt='secretaria.carteirinha.qr')
    contexto = {
        'valido': False,
        'mensagem': 'Token invalido.',
        'membro': None,
        'data_emissao': '',
        'token': token,
    }

    try:
        raw = signer.unsign(token, max_age=60 * 60 * 24 * 730)
        membro_id, ministerio_id, emissao_iso = raw.split('|', 2)
        membro = Membro.objects.select_related('igreja', 'status_pessoa').filter(pk=int(membro_id)).first()
        if not membro:
            contexto['mensagem'] = 'Membro nao encontrado.'
        else:
            ministerio_membro_id = getattr(getattr(membro, 'igreja', None), 'ministerio_id', None)
            if str(ministerio_membro_id or '') != str(ministerio_id or ''):
                contexto['mensagem'] = 'Carteirinha fora do ministerio esperado.'
            else:
                contexto['valido'] = True
                contexto['mensagem'] = 'Carteirinha validada com sucesso.'
                contexto['membro'] = membro
                try:
                    data_emissao = timezone.datetime.fromisoformat(emissao_iso).date()
                    contexto['data_emissao'] = _formatar_data_br(data_emissao)
                except Exception:
                    contexto['data_emissao'] = emissao_iso
    except signing.SignatureExpired:
        contexto['mensagem'] = 'Token expirado.'
    except Exception:
        contexto['mensagem'] = 'Token invalido ou adulterado.'

    return render(request, 'secretaria/documentos/carteirinha/validacao_qr.html', contexto)
