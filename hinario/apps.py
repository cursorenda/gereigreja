from django.apps import AppConfig


class HinarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hinario'
    verbose_name = 'Hinário e Recursos Devocionais'

    def ready(self):
        """Registra signals ao inicializar a aplicação."""
        import hinario.signals  # noqa: F401
