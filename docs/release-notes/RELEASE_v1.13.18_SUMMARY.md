# RELEASE v1.13.18 - RESUMO EXECUTIVO

Data: 19/06/2026
Tipo: PATCH
Escopo: Agenda e Eventos premium, recorrência avançada de programações e consolidação de fluxo operacional

## Resumo
A versão v1.13.18 consolida o domínio de eventos com foco em consistência funcional e experiência premium. O pacote elimina sobreposição de fluxo entre Agenda e Eventos, amplia as regras de recorrência de programações padrão e finaliza a premiumização das telas de eventos, incluindo melhorias de produtividade na marcação de presença.

## Principais Entregas
- Consolidação de fluxo Agenda x Eventos:
  - rotas legadas de CRUD na Agenda redirecionadas para o módulo Eventos;
  - importação de feriados unificada para o modelo Evento em fluxo web e comando;
  - Agenda mensal usando a mesma base de eventos do módulo principal.
- Evolução de Programações padrão da igreja:
  - suporte de hora de término com cálculo de duração;
  - validações condicionais de recorrência e resumo mais claro de configuração;
  - proteção contra conflitos entre Programações e Escola Bíblica Dominical.
- Premiumização completa das telas do módulo Eventos:
  - lista, criar, editar, detalhe, excluir e marcar presença padronizadas;
  - header, breadcrumb, botões e cards no mesmo design system;
  - limpeza de estilos inline com centralização em CSS compartilhado.
- Agenda premium com refinamento de UX:
  - cards de tipo, filtros e visual de eventos no calendário aprimorados;
  - leitura visual mais clara para hora/título de eventos;
  - remoção de elementos conflitantes da tela.
- Presença com operação acelerada:
  - ordenação A-Z/Z-A em colunas de texto;
  - busca em tempo real por nome;
  - ações em massa para marcar/desmarcar visíveis;
  - filtros e ações na mesma linha para ganho de espaço.

## Arquivos Impactados (Destaques)
- Agenda:
  - agenda/views.py
  - agenda/templates/agenda/agenda.html
  - agenda/management/commands/importar_feriados.py
- Configuração de Programações:
  - configuracao/models.py
  - configuracao/forms.py
  - configuracao/views.py
  - configuracao/services_programacao.py
  - configuracao/templates/configuracao/igrejas/editar_igreja_config.html
- Eventos:
  - eventos/models.py
  - eventos/templates/eventos/lista_eventos.html
  - eventos/templates/eventos/criar_evento.html
  - eventos/templates/eventos/editar_evento.html
  - eventos/templates/eventos/detalhe_evento.html
  - eventos/templates/eventos/excluir_evento.html
  - eventos/templates/eventos/marcar_presenca.html
- Estilos:
  - static/css/agenda.css
  - static/css/eventos_premium.css
  - static/css/eventos_lista_premium.css

## Migrações
- configuracao/migrations/0031_programacaopadraoigreja.py
- configuracao/migrations/0032_programacaopadraoigreja_regras_recorrencia.py
- configuracao/migrations/0033_programacaopadraoigreja_frequencia_avancada.py
- configuracao/migrations/0034_programacaopadraoigreja_hora_termino.py
- eventos/migrations/0015_evento_programacao_padrao.py

## Validação
- python manage.py check executado com sucesso (0 issues).

## Impacto para o Usuário
- Fluxo de eventos mais coerente e previsível.
- Ganho de produtividade na operação de presença.
- Melhor leitura e padrão premium em todo ciclo de vida do evento.

## Impacto Técnico
- Redução de ambiguidade entre apps Agenda e Eventos.
- Base visual e de comportamento mais centralizada e reaproveitável.
- Sem breaking changes de API pública.
