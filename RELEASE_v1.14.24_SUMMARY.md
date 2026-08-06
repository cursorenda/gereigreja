# Release v1.14.24 - 06/08/2026

## Resumo Executivo
Esta release consolida a evolucao da naturalidade para cobertura nacional completa no Brasil e melhora a experiencia de busca no cadastro/edicao da secretaria.

## Entregas Principais
- Importacao completa de municipios do Brasil via IBGE no comando de seed de localidades.
- Novas opcoes do comando:
  - `--brasil-completo`
  - `--ibge-timeout`
- Ajuste de robustez na importacao em lote para preservar unicidade por `nome_normalizado`.
- Filtro por UF no backend de autocomplete de cidades.
- Envio automatico de UF no frontend da naturalidade quando o campo estado estiver com sigla.
- Lista de sugestoes visivel e clicavel para naturalidade, reduzindo dependencia do comportamento nativo de datalist.

## Arquivos Alterados
- `CHANGELOG.md`
- `configuracao/management/commands/seed_localidades.py`
- `configuracao/services_localidades.py`
- `configuracao/views_localidades.py`
- `secretaria/forms.py`
- `secretaria/models.py`
- `secretaria/templates/partials/_form_pessoa_oficial.html`
- `secretaria/migrations/10008_pessoa_naturalidade_cidade.py`

## Validacoes Executadas
- `python manage.py check`
- Validacao de endpoint com UF (`q=sa&uf=SP`) retornando 200 e cidades de SP.
- Carga completa do Brasil concluida com sucesso:
  - Total BR no catalogo: 5570

## Comandos de Carga de Localidades
```bash
python manage.py seed_localidades --apenas-brasil --brasil-completo
```

## Observacoes
- Mantida compatibilidade retroativa com o campo textual legado `naturalidade`.
- O relacionamento catalogado (`naturalidade_cidade`) continua opcional.
