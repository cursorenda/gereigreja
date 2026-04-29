# App notificacoes

Centraliza toda a lógica de notificações do sistema.

## Funções principais
- Envio de notificações in-app, push, SMS, etc.
- Painel de notificações do usuário
- API de notificações

## Como usar
- Utilize as funções de `services.py` para disparar notificações de qualquer app.
- Consulte as views para integração com frontend.

## Migração
- Modelos, views e serviços de notificações foram movidos do app comunicacao para cá.
- Apps como secretaria, financeiro, eventos agora usam notificacoes para disparar alertas.

## Futuro
- Suporte a múltiplos canais
- Templates dinâmicos
- Integrações externas
