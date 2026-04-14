from django.contrib import admin
from .models_onboarding import OnboardingStatus

@admin.register(OnboardingStatus)
class OnboardingStatusAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'etapa_atual', 'etapas_concluidas', 'data_inicio', 'data_ultima_acao')
    search_fields = ('usuario__username', 'usuario__email')
    list_filter = ('etapa_atual',)
