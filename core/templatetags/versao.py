from django import template
import os
import re
from django.conf import settings

register = template.Library()

# Cache apenas em produção (não em DEBUG)
_versao_cache = None
_data_cache = None

@register.simple_tag
def get_versao_gereigreja():
    global _versao_cache, _data_cache
    
    # Em desenvolvimento (DEBUG=True), sempre recarregar do arquivo
    # Em produção (DEBUG=False), usar cache para performance
    if settings.DEBUG or _versao_cache is None:
        changelog_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'CHANGELOG.md')
        try:
            with open(changelog_path, encoding='utf-8') as f:
                for line in f:
                    if line.strip().lower().startswith('# changelog'):
                        continue
                    # Captura versão e data
                    match = re.match(r"#{1,6}\s+(v\d+\.\d+\.\d+)\b\s*[—-]?\s*(\d{2}/\d{2}/\d{4})?", line)
                    if match:
                        _versao_cache = match.group(1)
                        _data_cache = match.group(2)
                        if _data_cache:
                            return f"{_versao_cache} — {_data_cache}"
                        return _versao_cache
        except Exception:
            return 'Versão não disponível'
        return 'Versão não disponível'
    
    # Retornar do cache (apenas em produção)
    if _data_cache:
        return f"{_versao_cache} — {_data_cache}"
    return _versao_cache
