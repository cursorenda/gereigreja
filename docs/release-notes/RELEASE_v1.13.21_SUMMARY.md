# RELEASE v1.13.21 - RESUMO EXECUTIVO

Data: 22/06/2026
Tipo: PATCH
Escopo: Secretaria premium com visitação unificada, inteligência pastoral e fluxo escalável de grupos/casas

## Resumo
A versão v1.13.21 consolida um pacote operacional da Secretaria focado em clareza de fluxo, confiabilidade de registro e escalabilidade. A entrega unifica a jornada de visitação em um único ponto de operação, aprimora os indicadores pastorais e moderniza a vinculação de pessoas em Grupos/Casas com busca paginada server-side.

## Principais Entregas
- Central de Visitação unificada:
  - formulário único para Visita Particular e Visita Familiar;
  - registro consistente de visita familiar com seleção de moradores;
  - robustez adicional no parsing/normalização de IDs postados.
- Inteligência Pastoral de Visitação:
  - cards e gráfico de cobertura com visão de visitadas e não visitadas;
  - leitura de famílias visitadas e famílias sem visita;
  - filtro de período padronizado para meses (1m, 3m, 6m, 12m);
  - semântica de KPI ajustada para priorizar contatos de visita.
- Grupos/Casas em padrão premium e escalável:
  - formulário migrado para base premium com UX mais orientada a operação;
  - endpoint AJAX de busca paginada de pessoas por escopo;
  - seleção persistente entre páginas e envio por inputs ocultos.
- Consistência de escopo e status:
  - alinhamento de regras entre visitação e grupos/casas;
  - respeito ao escopo da igreja ativa e permissões do usuário.

## Arquivos Impactados
- secretaria/views/visitantes.py
- secretaria/views/visitacao_metrics.py
- secretaria/views/dashboard.py
- secretaria/views/grupos_casa.py
- secretaria/views/__init__.py
- secretaria/urls.py
- secretaria/templates/secretaria/central_visitacao.html
- secretaria/templates/secretaria/dashboard.html
- secretaria/templates/secretaria/grupocasa_form.html
- secretaria/templates/secretaria/grupocasa_detail.html
- secretaria/templates/secretaria/grupocasa_list.html
- secretaria/templates/secretaria/acompanhamentos_visita_list.html
- secretaria/templates/secretaria/escolher_pessoa_para_acompanhamento.html
- secretaria/templates/secretaria/registrar_acompanhamento_visita.html
- templates/menu.html
- CHANGELOG.md

## Migrações
- Nenhuma.

## Validação
- python manage.py check executado com sucesso (0 issues).

## Impacto para o Usuário
- Operação de visitação mais simples e previsível.
- Melhor visibilidade pastoral para priorização de famílias.
- Menor atrito para vincular pessoas em grupos/casas com bases grandes.

## Impacto Técnico
- Reuso de métricas e padronização de filtros de período.
- Menor risco de inconsistência por IDs formatados localmente.
- Sem alterações de schema e sem breaking changes.
