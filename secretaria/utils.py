# c:\Gereigreja\secretaria\utils.py
from django.contrib.auth.models import User, Group
from configuracao.models import Igreja, PerfilUsuario # Importar PerfilUsuario e Igreja
from django.db.models import Q # Importar Q para consultas complexas
from contas.constants import ADMIN_MINISTERIO, PASTOR_REGIONAL, SECRETARIO_LOCAL, TESOUREIRO

# --- Funções de Verificação de Grupo (Reutilizáveis) ---

def _user_in_group(user, group_name):
    """Verifica se o usuário pertence a um grupo específico."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    # Otimização: Verificar se o usuário já tem os grupos pré-carregados
    if hasattr(user, '_prefetched_objects_cache') and 'groups' in user._prefetched_objects_cache:
        return any(group.name == group_name for group in user.groups.all())
    # Fallback: Consultar o banco de dados
    from contas.constants import user_tem_grupo
    return user_tem_grupo(user, group_name)

def is_admin_org(user):
    """Verifica se o usuário é Admin da Ministério."""
    from contas.constants import user_has_permission_level_or_higher, ADMIN_MINISTERIO
    return user_has_permission_level_or_higher(user, ADMIN_MINISTERIO)

def is_secretario(user):
    """Verifica se o usuário é Secretário."""
    from contas.constants import user_has_permission_level_or_higher, SECRETARIO_LOCAL
    return user_has_permission_level_or_higher(user, SECRETARIO_LOCAL)

def is_lider_igreja(user):
    """Verifica se o usuário é Pastor Regional."""
    from contas.constants import user_has_permission_level_or_higher, PASTOR_REGIONAL
    return user_has_permission_level_or_higher(user, PASTOR_REGIONAL)

def is_tesoureiro(user):
    """Verifica se o usuário é Tesoureiro."""
    from contas.constants import user_has_permission_level_or_higher, TESOUREIRO
    return user_has_permission_level_or_higher(user, TESOUREIRO)


# Nova função para líder da secretaria
def is_secretaria_leader(user):
    """ Verifica se o usuário é Admin da Ministério ou pertence ao grupo 'Secretaria Ministerial'. """
    from contas.constants import user_has_permission_level_or_higher, LIDERANCA_SECRETARIA
    return user_has_permission_level_or_higher(user, LIDERANCA_SECRETARIA)

# --- Funções de Verificação de Permissão para secretaria de Membros ---

def has_membro_view_permission(user):
    """Verifica se o usuário tem permissão para VER dados de membros.""" # Adicionado is_secretaria_leader
    from contas.constants import user_has_permission_level_or_higher, SECRETARIO_LOCAL
    return user_has_permission_level_or_higher(user, SECRETARIO_LOCAL)

def has_membro_edit_permission(user):
    """Verifica se o usuário tem permissão para EDITAR/ADICIONAR/INATIVAR dados de membros."""
    from contas.constants import user_has_permission_level_or_higher, SECRETARIO_LOCAL
    return user_has_permission_level_or_higher(user, SECRETARIO_LOCAL)


# --- Funções de agrupamento de GrupoCasa reutilizáveis (preview/apply) ---
from .models import Pessoa, GrupoCasa
import unicodedata, re

def _normalize_text_for_group(s: str) -> str:
    if not s:
        return ''
    s = str(s).strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join([c for c in s if not unicodedata.combining(c)])
    s = re.sub(r"\s+", ' ', s)
    s = re.sub(r"[^0-9a-z ]", ' ', s)
    s = re.sub(r"\s+", ' ', s)
    return s.strip()


def agrupar_preview_for_queryset(person_qs):
    """Gera preview de grupos detectados a partir de um queryset de `Pessoa`.
    Retorna lista de dicionários com keys: igreja_id, cep, rua, numero, complemento, pessoas_ids, pessoas_nomes, count
    """
    groups = {}
    for p in person_qs:
        key = (
            p.igreja_id or 0,
            _normalize_text_for_group(p.cep or ''),
            _normalize_text_for_group(p.rua or ''),
            _normalize_text_for_group(p.numero_casa or ''),
            _normalize_text_for_group(p.complemento or '')
        )
        groups.setdefault(key, []).append(p)

    rows = []
    for key, plist in groups.items():
        igreja_id, cep, rua, numero, complemento = key
        ids = [p.pk for p in plist]
        nomes = [p.nome for p in plist]
        rows.append({
            'igreja_id': igreja_id,
            'cep': cep,
            'rua': rua,
            'numero': numero,
            'complemento': complemento,
            'pessoas_ids': ids,
            'pessoas_nomes': nomes,
            'count': len(plist),
        })
    # ordenar por rua/numero para apresentação
    rows.sort(key=lambda r: (r.get('rua') or '', r.get('numero') or ''))
    return rows
    updated = 0
    from django.db import transaction

    def _pretty_address(rua_val, numero_val, complemento_val, cep_val):
        parts = []
        try:
            if rua_val:
                parts.append(str(rua_val).strip())
            if numero_val:
                parts.append(str(numero_val).strip())
            if complemento_val:
                parts.append(str(complemento_val).strip())
            if cep_val:
                parts.append(str(cep_val).strip())
        except Exception:
            pass
        if not parts:
            return 'Casa'
        txt = ', '.join(parts)
        try:
            return txt.title()
        except Exception:
            return txt

    with transaction.atomic():
        for r in rows:
            igreja_id = r.get('igreja_id') or None
            rua = r.get('rua') or None
            numero = r.get('numero') or None
            complemento = r.get('complemento') or None
            cep = r.get('cep') or None

            nome_padrao = f"Casa — {_pretty_address(rua, numero, complemento, cep)}"

            # Tentar extrair bairro/cidade/estado a partir dos moradores (primeiro não-vazio)
            bairro_val = None
            cidade_val = None
            estado_val = None
            ids = r.get('pessoas_ids', [])
            persons_qs = Pessoa.objects.filter(pk__in=ids)
            for p in persons_qs:
                # Pessoa armazena bairro no campo 'bairro_distrito'
                if not bairro_val and getattr(p, 'bairro_distrito', None):
                    bairro_val = p.bairro_distrito.strip()
                if not cidade_val and getattr(p, 'cidade', None):
                    cidade_val = p.cidade.strip()
                if not estado_val and getattr(p, 'estado', None):
                    estado_val = p.estado.strip()
                if bairro_val and cidade_val and estado_val:
                    break

            defaults = {'nome': nome_padrao}
            # Only include address fields in defaults if we have values
            if bairro_val:
                defaults['bairro'] = bairro_val
            if cidade_val:
                defaults['cidade'] = cidade_val
            if estado_val:
                defaults['estado'] = estado_val

            group, created_flag = GrupoCasa.objects.get_or_create(
                igreja_id=igreja_id,
                rua=rua,
                numero=numero,
                complemento=complemento,
                cep=cep,
                defaults=defaults
            )

            if created_flag:
                created += 1
            else:
                # Se o grupo já existia mas não tinha bairro/cidade/estado, atualizá-los quando possível
                changed = False
                if not getattr(group, 'bairro', None) and bairro_val:
                    group.bairro = bairro_val
                    changed = True
                if not getattr(group, 'cidade', None) and cidade_val:
                    group.cidade = cidade_val
                    changed = True
                if not getattr(group, 'estado', None) and estado_val:
                    group.estado = estado_val
                    changed = True
                if changed:
                    try:
                        group.save()
                    except Exception:
                        # don't let a save error abort the entire atomic operation
                        pass

            # associar pessoas
            for p in persons_qs:
                if p.grupo_casa_id != group.id:
                    p.grupo_casa = group
                    p.save()
                    updated += 1

    return {'created': created, 'updated': updated}

# --- Função para Obter Igrejas Permitidas para secretaria de Membros ---

def get_allowed_churches_for_membros(user, ministerio_param=None): # Adicionado ministerio_param
    # Esta função foi ajustada para aceitar um ministerio_param opcional.
    # Se fornecido, usaremos esse ministério como contexto de filtro em vez de depender
    # estritamente de `user.perfil.ministerio`. Isso permite que views que já
    # resolveram o ministério (ex: via get_ministerio_or_error(request)) passem
    # o contexto corretamente e evitem retornos vazios por causa de perfis ausentes
    # ou desencontro de ministérios entre request e user.perfil.
    """
    Retorna um QuerySet das Igrejas que o usuário tem permissão para acessar no contexto de membros.
    - Admin Org ou Líder Secretaria: Todas as igrejas do ministério ou as permitidas no perfil + subordinadas.
    - Secretário, Líder Igreja, Tesoureiro (não líderes): Igrejas associadas no PerfilUsuario.
    - Outros: Nenhuma igreja.
    - Retorna QuerySet vazio se o usuário não tiver perfil/ministério ou permissão de visualização.
    """

    if not user.is_authenticated:
        return Igreja.objects.none()

    # Preferir o ministerio passado explicitamente; caso contrário, tentar extrair
    # do perfil do usuário. Se não houver ministério disponível, retornamos vazio.
    ministerio = ministerio_param
    if ministerio is None:
        try:
            ministerio = user.perfil.ministerio
        except Exception:
            ministerio = None

    # SUPERUSUÁRIO SEMPRE VÊ TODAS AS IGREJAS DO MINISTÉRIO OU DO SISTEMA
    if user.is_superuser:
        # Superusuário SEMPRE vê todas as igrejas, independente de perfil ou ministério
        return Igreja.objects.all()

    if not ministerio:
        return Igreja.objects.none()

    # Verifica se o usuário tem PELO MENOS permissão de visualização de membros
    if not has_membro_view_permission(user):
        return Igreja.objects.none()

    # Se o usuário é Admin da Ministério ou Líder da Secretaria, expandir permissões
    if is_secretaria_leader(user):
        igrejas_base_permitidas = user.perfil.igrejas_permitidas.filter(ministerio=ministerio)

        
        # Se for Admin do Minist. e não tiver igrejas específicas no perfil, vê todas do ministério
        if is_admin_org(user) and not igrejas_base_permitidas.exists():
            return Igreja.objects.filter(ministerio=ministerio)

        todas_igrejas_permitidas_ids = set()

        def get_subordinadas_recursivamente(igreja_obj):
            sub_ids = set()
            sub_ids.add(igreja_obj.pk) # Adiciona a própria igreja
            # Busca subordinadas que pertencem à mesma ministério (segurança)
            # Assumindo que o related_name no modelo Igreja para igreja_superior é 'igrejas_subordinadas'
            for sub_igreja in igreja_obj.igrejas_subordinadas.filter(ministerio=ministerio):
                sub_ids.update(get_subordinadas_recursivamente(sub_igreja))
            return sub_ids

        for igreja_permitida in igrejas_base_permitidas:
            todas_igrejas_permitidas_ids.update(get_subordinadas_recursivamente(igreja_permitida))
            
        if todas_igrejas_permitidas_ids:
            return Igreja.objects.filter(pk__in=list(todas_igrejas_permitidas_ids), ministerio=ministerio)
        else:
            # Se o líder não tem igrejas no perfil ou elas não existem na ministério, retorna vazio.
            return Igreja.objects.none()



    elif is_secretario(user) or is_lider_igreja(user) or is_tesoureiro(user):
        # Secretário, Líder e Tesoureiro têm acesso às igrejas explicitamente permitidas no perfil
        # Garante que as igrejas retornadas pertencem à ministério do usuário (segurança extra)
        igrejas_perfil = user.perfil.igrejas_permitidas.filter(ministerio=ministerio)
        if igrejas_perfil.exists():
            return igrejas_perfil

        # Fallback seguro: usa igreja(s) vinculada(s) ao membro do próprio usuário.
        try:
            igrejas_membro = Igreja.objects.filter(
                membros__usuario=user,
                ministerio=ministerio,
            ).distinct()
            if igrejas_membro.exists():
                return igrejas_membro
        except Exception:
            pass

        return Igreja.objects.none()
    else:
        # Por segurança, retorna vazio.
        return Igreja.objects.none()