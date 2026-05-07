from django.apps import AppConfig


class ComunicacaoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comunicacao'

    def ready(self):
        import comunicacao.signals  # noqa: F401
