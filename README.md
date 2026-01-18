#
# Exibição automática da versão do sistema

O sistema exibe automaticamente a versão atual (e data) em todos os rodapés e pode exibir também no admin, lendo o número da versão do arquivo `CHANGELOG.md`.

## Como funciona
- O arquivo `core/templatetags/versao.py` define uma template tag chamada `get_versao_gereigreja`.
- Essa tag lê a primeira linha de versão do `CHANGELOG.md` (ex: `## v1.0.5 — 17/01/2026`).
- O valor é cacheado em memória para performance.
- Se não conseguir ler, exibe "Versão não disponível".

## Como usar
- No template base, use:
  ```django
  {% load versao %}
  {% get_versao_gereigreja as versao_sistema %}
  Versão {{ versao_sistema }}
  ```
- Para exibir no admin, veja instrução abaixo.

## Exibir versão no admin
Adicione o seguinte em `core/admin.py`:
```python
from django.contrib import admin
from django.utils.html import format_html
from core.templatetags.versao import get_versao_gereigreja

admin.site.site_header = f"Gereigreja — Versão {get_versao_gereigreja()}"
admin.site.site_title = f"Gereigreja — Versão {get_versao_gereigreja()}"
admin.site.index_title = format_html("<span style='font-size:1.1em'>Bem-vindo ao Gereigreja<br>Versão {}</span>", get_versao_gereigreja())
```
Assim, a versão aparecerá no topo e título do admin.

## Observações
- O padrão pode ser usado para outros metadados globais (build, ambiente, etc).
- Se mudar o local do `CHANGELOG.md`, ajuste o caminho na tag.

# Organização do fluxo de Visitas e Visitantes

## Visitas (Acompanhamento de Visitas)
- O fluxo de visitas refere-se ao acompanhamento realizado pela igreja na casa das pessoas.
- As páginas e templates relacionados ao acompanhamento de visitas são:
  - `acompanhamentos_visita_list.html`: lista de acompanhamentos de visita
  - `registrar_acompanhamento_visita.html`: registro de novo acompanhamento
  - `ver_acompanhamento_visita.html`: detalhes do acompanhamento
  - `editar_acompanhamento_visita.html`: edição do acompanhamento
  - `excluir_acompanhamento_visita.html`: exclusão do acompanhamento
  - `escolher_pessoa_para_acompanhamento.html`: seleção de pessoa para acompanhamento
- Todos os links internos entre essas páginas apontam para o fluxo correto de visitas.
- Não há mais links para páginas de visitantes/recepção dentro do fluxo de visitas.

## Visitantes (Recepção)
- O fluxo de visitantes refere-se às pessoas que vêm à igreja, geralmente relacionado à recepção e eventos.
- As páginas de visitantes estão separadas e não misturadas com o fluxo de visitas.

## Organização e Manutenção
- O fluxo de visitas está centralizado e sem duplicidade.
- Links e breadcrumbs revisados para evitar mistura de fluxos.
- Caso novas páginas sejam criadas, garantir que o fluxo de visitas e visitantes permaneça separado.

---

Última revisão: 14/11/2025
Alteração: Removido link para "Lista de Visitantes" do template `registrar_acompanhamento_visita.html` e substituído por "Lista de Visitas".
