from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet que implementa soft delete com padrão de ocultar deletados."""

    def alive(self):
        """Retorna apenas registros não deletados."""
        return self.filter(deleted_at__isnull=True)

    def deleted(self):
        """Retorna apenas registros deletados (soft delete)."""
        return self.filter(deleted_at__isnull=False)

    def soft_delete(self):
        """Marca registros como deletados (soft delete)."""
        return self.update(deleted_at=timezone.now())

    def restore(self):
        """Restaura registros deletados."""
        return self.update(deleted_at=None)


class HinoGlobalManager(models.Manager):
    """Manager para HinoGlobal com helpers de negócio."""

    def get_queryset(self):
        """Padrão: oculta deletados."""
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def all_including_deleted(self):
        """Retorna todos os registros incluindo deletados."""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def ativos(self):
        """Retorna hinos ativos e não deletados."""
        return self.filter(ativo=True)

    def disponiveis_publicacao(self):
        """
        Retorna hinos disponíveis para exibição pública:
        - Ativo
        - Não deletado
        - Não bloqueado
        - Licença não expirada
        """
        from django.db.models import Q
        from django.utils import timezone

        today = timezone.now().date()
        return self.filter(
            ativo=True,
            blocked_for_public_use=False,
        ).filter(
            Q(license_expires_at__isnull=True) | Q(license_expires_at__gte=today)
        )

    def por_colecao(self, colecao):
        """Retorna hinos de uma coleção específica."""
        return self.filter(colecao=colecao)


class HinoDaIgrejaManager(models.Manager):
    """Manager para HinoDaIgreja com isolamento multi-tenant."""

    def get_queryset(self):
        """Padrão: oculta deletados."""
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def all_including_deleted(self):
        """Retorna todos os registros incluindo deletados."""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def da_igreja(self, igreja_id):
        """Retorna hinos customizados de uma igreja específica."""
        return self.filter(igreja_id=igreja_id)

    def ativos(self):
        """Retorna hinos ativos e não deletados."""
        return self.filter(ativo=True)

    def disponiveis_publicacao(self):
        """Retorna hinos disponíveis para exibição pública."""
        from django.db.models import Q
        from django.utils import timezone

        today = timezone.now().date()
        return self.filter(
            ativo=True,
            blocked_for_public_use=False,
        ).filter(
            Q(license_expires_at__isnull=True) | Q(license_expires_at__gte=today)
        )


class HinoAuditLogManager(models.Manager):
    """Manager para HinoAuditLog com filtros de rastreamento."""

    def para_chiesa(self, igreja_id):
        """Retorna eventos de auditoria de uma chiesa específica."""
        return self.filter(tenant_igreja_id=igreja_id)

    def acoes_compliance(self):
        """Retorna eventos relacionados a compliance e legal."""
        return self.filter(
            action__in=['blocked', 'unblocked', 'reviewed', 'imported']
        )
