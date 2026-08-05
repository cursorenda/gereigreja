# RELEASE v1.14.9 - Localização dos Dias da Semana

A release v1.14.9 elimina a exibição de nomes de dias da semana em inglês no dashboard da Secretaria, introduzindo um helper centralizado e reutilizável em `core/utils.py`. A solução é projetada para suportar futura expansão multilíngue sem necessidade de refatoração distribuída.

## Entregas principais
- Helper centralizado `get_weekday_label(value, language='pt')` em `core/utils.py`:
  - Retorna abreviações em português por padrão: `SEG`, `TER`, `QUA`, `QUI`, `SEX`, `SÁB`, `DOM`.
  - Aceita parâmetro `language` para expansão futura (ex.: `'en'`).
  - Mapeamento explícito em dicionário `WEEKDAY_LABELS` de fácil manutenção.
- Correção em `secretaria/views/dashboard.py`:
  - Substituído `data.strftime('%a').upper()` pelo helper centralizado.
- Correção em `secretaria/views/_legacy.py`:
  - Mesma substituição aplicada no bloco de próximos eventos.
- Teste automatizado `tests/test_weekday_i18n.py`:
  - Cobertura para português (SEG) e inglês (MON).
  - 2 testes passando com sucesso.

## Benefícios
- Elimina completamente nomes de dias em inglês para todos os usuários do sistema.
- Lógica de localização concentrada em um único ponto — fácil de manter e estender.
- Base pronta para expansão a outros idiomas sem alterar os pontos de uso.

## Validação
- `pytest tests/test_weekday_i18n.py -q` — 2 passed.
- `python manage.py check` executado sem erros de configuração.
