from django import template
import os
import re

register = template.Library()

# Cache simples em memória (por processo)
_versao_cache = None
_data_cache = None

@register.simple_tag
def get_versao_gereigreja():
    global _versao_cache, _data_cache
    if _versao_cache is not None:
        if _data_cache:
            return f"{_versao_cache} — {_data_cache}"
        return _versao_cache
    changelog_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'CHANGELOG.md')
    try:
        with open(changelog_path, encoding='utf-8') as f:
            for line in f:
                if line.strip().lower().startswith('# changelog'):
                    continue
                # Captura versão e data
                match = re.match(r"##\s+(v[0-9.]+)\s*[—-]?\s*(\d{2}/\d{2}/\d{4})?", line)
                if match:
                    _versao_cache = match.group(1)
                    _data_cache = match.group(2)
                    if _data_cache:
                        return f"{_versao_cache} — {_data_cache}"
                    return _versao_cache
    except Exception:
        return 'Versão não disponível'
    return 'Versão não disponível'
