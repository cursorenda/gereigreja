from django.apps import AppConfig

class ConfiguracaoConfig(AppConfig):
    name = 'configuracao'

    def ready(self):
        import configuracao.signals
