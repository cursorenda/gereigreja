from django.apps import AppConfig

class EscolaBiblicaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'escola_biblica'
    verbose_name = 'Escola Bíblica Dominical'

    def ready(self):
        import escola_biblica.signals
