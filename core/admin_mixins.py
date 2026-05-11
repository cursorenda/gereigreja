"""
Admin mixins reutilizaveis para reducao de duplicacao de codigo.

Padroes comuns encapsulados para uso em multiplos AdminClasses.
"""
from django.contrib import admin


class ReadOnlyAdminMixin:
    """
    Desabilita criacao, edicao e delecao - apenas visualizacao.
    Ideal para modelos de auditoria/historico.
    """
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False


class NoAddDeleteMixin:
    """
    Desabilita criacao e delecao, mas permite edicao.
    Ideal para modelos gerenciados automaticamente.
    """
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SuperuserOnlyMixin:
    """
    Restringe visualizacao apenas a superusers.
    Ideal para modelos sensiveis.
    """
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class TimestampReadOnlyMixin:
    """
    Torna campos de timestamp automaticos como read-only.
    Aplica-se a modelos com criado_em/atualizado_em.
    """
    readonly_fields = ('criado_em', 'atualizado_em')


class MinisterioFilteredMixin:
    """
    Filtra automaticamente queryset por ministerio do usuario logado.
    Usuarios comuns veem apenas seu ministerio.
    Superusers veem todos.
    """
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filtro por ministerio do usuario
        try:
            ministerio = request.user.profile.ministerio
            return qs.filter(ministerio=ministerio)
        except AttributeError:
            return qs.none()


class IgrejaFilteredMixin:
    """
    Filtra automaticamente queryset por igrejas do usuario logado.
    Usuarios comuns veem apenas suas igrejas permitidas.
    Superusers veem todas.
    """
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            igrejas = request.user.profile.igrejas_permitidas.all()
            if igrejas.exists():
                return qs.filter(igreja__in=igrejas)
            return qs.none()
        except AttributeError:
            return qs.none()


class DateHierarchyMixin:
    """
    Adiciona hierarquia temporal em campo 'criado_em'.
    Use apenas com modelos que possuem campo 'criado_em'.
    Override em subclasses se campo diferente.
    """
    date_hierarchy = 'criado_em'


class DataInicioHierarchyMixin:
    """
    Hierarquia temporal em data_inicio.
    Use com modelos de eventos/agendamentos.
    """
    date_hierarchy = 'data_inicio'


class DataTransicaoHierarchyMixin:
    """
    Hierarquia temporal em data_transicao.
    Use com modelos de historico de mudancas.
    """
    date_hierarchy = 'data_transicao'


class DataHierarchyMixin:
    """
    Hierarquia temporal em campo 'data'.
    Use com modelos que possuem campo 'data'.
    """
    date_hierarchy = 'data'


class SearchMixin:
    """
    Define campos de busca padrao - deve ser sobrescrito por subclasses.
    Convencionalmente busca em nome/titulo/email/username.
    """
    def get_search_fields(self):
        """Override em subclasses com campos especificos."""
        return ()


class ReadableDisplayMixin:
    """
    Adiciona metodos de display legivel para campos booleanos.
    Use com list_display = ['campo_sim_nao', ...].
    """
    @admin.display(boolean=True)
    def campo_sim_nao(self, obj):
        """Exemplo - sobrescrever em subclasses."""
        return bool(obj.ativo)


class AuditoriaTimestampMixin(TimestampReadOnlyMixin, ReadOnlyAdminMixin):
    """
    Combinacao de timestamp read-only + visualizacao apenas.
    Ideal para logs/auditoria.
    """
    pass


class TenantFilteredAuditMixin(MinisterioFilteredMixin, AuditoriaTimestampMixin):
    """
    Combinacao: filtrado por ministerio + read-only + timestamp.
    Ideal para logs de operacoes por ministerio.
    """
    pass
