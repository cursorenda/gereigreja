# RELEASE v1.13.19 - RESUMO EXECUTIVO

Data: 22/06/2026
Tipo: PATCH
Escopo: Correção de persistência na marcação de presença em Eventos

## Resumo
A versão v1.13.19 corrige de forma definitiva uma inconsistência no fluxo de presença de eventos, em que marcações realizadas na interface poderiam não persistir corretamente em alguns cenários. A solução combina endurecimento do payload no frontend com parser robusto no backend, além de telemetria de execução para auditoria de recebimento dos dados.

## Principais Entregas
- Persistência de presença reforçada no módulo de Eventos:
  - envio de presença por IDs de participação (`presentes=[pk,...]`);
  - fallback de envio por JSON (`presentes_json`) para maior resiliência;
  - parser de POST com priorização do JSON e fallback para envio tradicional.
- Estabilidade de navegação na tela de presença:
  - alteração de sessão (dia) por GET em vez de submit do formulário principal;
  - redução de risco de submissões acidentais.
- Sincronização contínua do estado no frontend:
  - atualização do payload em alterações individuais, ações em massa e no submit.
- Observabilidade operacional:
  - log técnico estruturado por evento/sessão para facilitar suporte e validação pós-release.

## Arquivos Impactados
- `eventos/views.py`
- `eventos/templates/eventos/marcar_presenca.html`
- `CHANGELOG.md`

## Migrações
- Nenhuma.

## Validação
- `python manage.py check` executado com sucesso (0 issues).
- Teste técnico do fluxo de POST realizado com persistência confirmada em registros de participação.

## Impacto para o Usuário
- Marcações de presença mais confiáveis.
- Menos retrabalho operacional na conferência de presença.
- Maior segurança na mudança de sessão durante o preenchimento.

## Impacto Técnico
- Fluxo de submissão mais resiliente a interferência de scripts/client-side.
- Melhor diagnóstica em produção via logs estruturados.
- Sem alteração de schema e sem breaking changes.
