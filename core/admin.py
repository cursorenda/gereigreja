
from django.contrib import admin
from django.utils.html import format_html
from core.templatetags.versao import get_versao_gereigreja

admin.site.site_header = f"Gereigreja — Versão {get_versao_gereigreja()}"
admin.site.site_title = f"Gereigreja — Versão {get_versao_gereigreja()}"
admin.site.index_title = format_html("<span style='font-size:1.1em'>Bem-vindo ao Gereigreja<br>Versão {}</span>", get_versao_gereigreja())
