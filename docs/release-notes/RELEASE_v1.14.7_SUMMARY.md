# RELEASE v1.14.7 - Dashboard Dev Fase 2

A release v1.14.7 consolida a Fase 2 do Dashboard do Desenvolvedor, introduzindo uma camada operacional orientada a ação com prioridades do dia e estados operacionais consolidados. A proposta reduz carga cognitiva, acelera resposta técnica e melhora a governança diária da plataforma.

## Entregas principais
- Seção Prioridades do Dia com itens automáticos e ordenação por severidade.
- Seção Estados Operacionais com status por domínio:
  - Backups
  - Infraestrutura (CPU/RAM)
  - Aplicação (erros em logs)
  - Compliance de hinos
  - Custo WhatsApp (risco e share)
- Resumo executivo com panorama geral (ok/alerta/critico) e contadores por status.
- Layout responsivo da nova área com grade adaptável desktop/mobile.

## Benefícios
- Ação mais rápida sobre problemas críticos.
- Leitura operacional clara para staff técnico.
- Base pronta para expandir automações e alertas na próxima etapa.

## Validação
- `python manage.py check` executado com sucesso.
- `pytest painel_desenvolvedor/tests.py -q` executado com sucesso.
