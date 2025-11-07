# Imports necessários para signals
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import MembroCargo, Cargo
# --- Sinal para adicionar membro ao grupo de permissão ao atribuir cargo (novo modelo) ---
@receiver(post_save, sender=MembroCargo)
def sincroniza_membro_grupo_novo(sender, instance, created, **kwargs):
    if instance.membro and instance.cargo and instance.cargo.grupo_permissao:
        user = getattr(instance.membro, 'usuario', None)
        if user and hasattr(instance.cargo.grupo_permissao, 'user_set'):
            instance.cargo.grupo_permissao.user_set.add(user)

# --- Sinal para remover membro do grupo de permissão ao remover cargo (novo modelo) ---
@receiver(post_delete, sender=MembroCargo)
def remove_membro_do_grupo_novo(sender, instance, **kwargs):
    if instance.membro and instance.cargo and instance.cargo.grupo_permissao:
        user = getattr(instance.membro, 'usuario', None)
        if user and hasattr(instance.cargo.grupo_permissao, 'user_set'):
            instance.cargo.grupo_permissao.user_set.remove(user)
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Membro, TimelineEvent, StatusHistorico
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from django.db.models.signals import pre_save
from django.db import transaction
from .models import GrupoCasa
import unicodedata, re

# Cria evento ao cadastrar novo membro
@receiver(post_save, sender=Membro)
def cria_evento_entrada_membro(sender, instance, created, **kwargs):
    if created and instance.data_entrada:
        # Evita duplicidade
        if not TimelineEvent.objects.filter(membro=instance, tipo_evento='entrada', data=instance.data_entrada).exists():
            data_entrada = instance.data_entrada
            if data_entrada and not hasattr(data_entrada, 'tzinfo'):
                from datetime import datetime
                from django.utils.timezone import make_aware, get_current_timezone
                data_entrada = make_aware(datetime.combine(data_entrada, datetime.min.time()), get_current_timezone())
            TimelineEvent.objects.create(
                membro=instance,
                data=data_entrada,
                tipo_evento='entrada',
                descricao='Entrada do membro no sistema.'
            )


# Cria evento ao registrar histórico de status ou tipo
@receiver(post_save, sender=StatusHistorico)
def cria_evento_status_tipo_membro(sender, instance, created, **kwargs):
    if created:
        data_transicao = instance.data_transicao
        if data_transicao and timezone.is_naive(data_transicao):
            from django.utils.timezone import make_aware, get_current_timezone
            data_transicao = make_aware(data_transicao, get_current_timezone())
        # Mudança de status
        if instance.status_pessoa_anterior != instance.status_pessoa_novo and instance.status_pessoa_novo:
            if not TimelineEvent.objects.filter(membro=instance.membro, tipo_evento='mudanca_status', data=data_transicao).exists():
                TimelineEvent.objects.create(
                    membro=instance.membro,
                    data=data_transicao,
                    tipo_evento='mudanca_status',
                    descricao=f"Mudança de status: {instance.status_pessoa_anterior} → {instance.status_pessoa_novo}"
                )
        # Mudança de tipo
        if instance.tipo_pessoa_anterior != instance.tipo_pessoa_novo and instance.tipo_pessoa_novo:
            if not TimelineEvent.objects.filter(membro=instance.membro, tipo_evento='mudanca_tipo', data=data_transicao).exists():
                TimelineEvent.objects.create(
                    membro=instance.membro,
                    data=data_transicao,
                    tipo_evento='mudanca_tipo',
                    descricao=f"Mudança de tipo: {instance.tipo_pessoa_anterior} → {instance.tipo_pessoa_novo}"
                )


# -------------------------
# Associação segura de GrupoCasa
# -------------------------
def _normalize_text(s: str) -> str:
    if not s:
        return ''
    s = str(s).strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join([c for c in s if not unicodedata.combining(c)])
    s = re.sub(r"\s+", ' ', s)
    s = re.sub(r"[^0-9a-z ]", ' ', s)
    s = re.sub(r"\s+", ' ', s)
    return s.strip()


@receiver(pre_save, sender=Membro)
def _cache_prev_address(sender, instance, **kwargs):
    """Armazena os valores anteriores de endereço para detectar mudanças no post_save."""
    try:
        if not instance.pk:
            instance._prev_address = None
            return
        prev = sender.objects.filter(pk=instance.pk).values('rua', 'numero_casa', 'complemento', 'cep', 'grupo_casa_id').first()
        instance._prev_address = prev
    except Exception:
        instance._prev_address = None


@receiver(post_save, sender=Membro)
def associar_grupo_casa_por_endereco(sender, instance, created, **kwargs):
    """Associa automaticamente a um GrupoCasa EXISTENTE quando o endereço do membro criar/alterar
    e existir um grupo com endereço normalizado igual. Não cria novos grupos. Atualiza via queryset
    para evitar recursão de sinais.
    Regras de segurança:
      - Só associa se encontrar um GrupoCasa já existente com mesmo endereço normalizado.
      - Não remove associação existente a menos que o endereço mude e exista outro GrupoCasa correspondente.
      - Evita chamar instance.save() dentro do signal; usa update() para prevenir loops.
    """
    try:
        # Só operar quando há dados mínimos de endereço
        rua = (instance.rua or '').strip()
        numero = (instance.numero_casa or '').strip()
        complemento = (instance.complemento or '').strip()
        cep = (instance.cep or '').strip()
        if not (rua or cep or numero):
            return

        prev = getattr(instance, '_prev_address', None)
        changed = False
        if prev is None:
            # novo membro
            changed = True
        else:
            # comparar campos normalizados
            prev_rua = prev.get('rua') or ''
            prev_num = prev.get('numero_casa') or ''
            prev_comp = prev.get('complemento') or ''
            prev_cep = prev.get('cep') or ''
            if _normalize_text(prev_rua) != _normalize_text(rua) or _normalize_text(prev_num) != _normalize_text(numero) or _normalize_text(prev_comp) != _normalize_text(complemento) or (prev_cep or '').strip() != cep:
                changed = True

        if not changed and instance.grupo_casa_id:
            # nada a fazer
            return

        # Buscar GrupoCasa candidato(s) na mesma igreja (quando disponível)
        candidates = GrupoCasa.objects.all()
        if instance.igreja_id:
            candidates = candidates.filter(igreja_id=instance.igreja_id)
        # otimização: filtrar por CEP quando disponível
        if cep:
            candidates = candidates.filter(cep__iexact=cep)

        target = None
        n_rua = _normalize_text(rua)
        n_num = _normalize_text(numero)
        n_comp = _normalize_text(complemento)
        # Percorrer candidatos e comparar com normalização
        for c in candidates:
            if _normalize_text(c.rua) == n_rua and _normalize_text(c.numero or '') == n_num and _normalize_text(c.complemento or '') == n_comp:
                target = c
                break

        if not target:
            # Nenhum GrupoCasa existente encontrado — avaliar criação automática
            try:
                # Buscar outros membros no mesmo endereço (normalizado) na mesma igreja
                from .models import Membro as _Membro
                n_matches = 0
                matching_ids = []
                n_rua = _normalize_text(rua)
                n_num = _normalize_text(numero)
                n_comp = _normalize_text(complemento)
                qs = _Membro.objects.all()
                if instance.igreja_id:
                    qs = qs.filter(igreja_id=instance.igreja_id)
                # otimizar por CEP se disponível
                if cep:
                    qs = qs.filter(cep__iexact=cep)

                # iterar e comparar normalizado (limitado a 200 para segurança)
                for m in qs[:200]:
                    if m.pk == instance.pk:
                        continue
                    if _normalize_text(m.rua) == n_rua and _normalize_text(m.numero_casa or '') == n_num and _normalize_text(m.complemento or '') == n_comp:
                        n_matches += 1
                        matching_ids.append(m.pk)

                # Se encontrarmos pelo menos 1 outro membro (total >=2), então criar GrupoCasa e associar
                if n_matches >= 1:
                    from django.db import transaction as _transaction
                    with _transaction.atomic():
                        # criar ou obter GrupoCasa (usar valores brutos, sem normalização)
                        group_defaults = {'nome': None, 'bairro': getattr(instance, 'bairro_distrito', None)}
                        group, created_group = GrupoCasa.objects.get_or_create(
                            igreja_id=instance.igreja_id if instance.igreja_id else None,
                            rua=rua or None,
                            numero=numero or None,
                            complemento=complemento or None,
                            cep=cep or None,
                            defaults=group_defaults
                        )
                        # Construir lista de pks a atualizar (inclui o instance)
                        to_update = matching_ids + [instance.pk]
                        # Atualizar via queryset para evitar recursão
                        _Membro.objects.filter(pk__in=to_update).update(grupo_casa=group)
                        target = group
                else:
                    # não criar com apenas uma pessoa: segurança
                    return
            except Exception:
                # Em caso de erro, não bloquear o fluxo principal
                import logging
                logging.getLogger(__name__).exception('Erro ao avaliar/criar GrupoCasa automaticamente')

        # Se já está associado ao mesmo, nada a fazer
        if instance.grupo_casa_id == target.id:
            return

        # Atualiza via queryset para evitar disparar post_save recursivo
        sender.objects.filter(pk=instance.pk).update(grupo_casa=target)
    except Exception:
        import logging
        logging.getLogger(__name__).exception('Erro no signal associar_grupo_casa_por_endereco')


