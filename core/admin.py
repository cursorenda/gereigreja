
from django.contrib import admin

# Configurações do Django Admin (apenas texto, sem HTML)
admin.site.site_title = "Gereigreja"
admin.site.site_header = "Gereigreja — Sistema de Gestão"
admin.site.index_title = "Bem-vindo ao Gereigreja"

try:
    from core.templatetags.versao import get_versao_gereigreja
    versao = get_versao_gereigreja()
    admin.site.site_header = f"Gereigreja — Versão {versao}"
    admin.site.index_title = f"Bem-vindo ao Gereigreja — Versão {versao}"
except:
    pass
