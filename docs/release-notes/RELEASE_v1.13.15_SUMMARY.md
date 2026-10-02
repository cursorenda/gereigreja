# RELEASE v1.13.15 - RESUMO EXECUTIVO

Data: 08/06/2026
Tipo: PATCH
Escopo: Permissoes Secretaria + Assinatura/Stripe (Checkout)

## Resumo
A versao v1.13.15 consolida o novo controle de acesso da Secretaria por tipo de igreja, melhora a experiencia de escolha de plano para usuarios autenticados e reforca a resiliencia do checkout Stripe em producao, incluindo validacao/sincronizacao de cupons e hardening da sincronizacao de precos.

## Principais Entregas
- Nova regra de acesso da Secretaria por tipo de igreja e papel:
  - secretario permitido;
  - administrador permitido apenas em sede/independente;
  - bloqueio para perfis fora da politica.
- Permissao request-aware aplicada de ponta a ponta:
  - decoradores,
  - template tags,
  - dashboard e fluxo demo.
- Mensageria dinamica no formulario de Tipo de Igreja para orientar impacto de acesso.
- Botoes de planos ajustados para checkout correto de usuarios autenticados:
  - landing page,
  - pagina publica de planos,
  - tela interna de assinatura.
- Checkout com cupom fortalecido:
  - resolucao robusta de codigo promocional/cupom,
  - fallback no Stripe quando nao encontrado localmente,
  - sincronizacao local no webhook.
- Comando `configurar_planos_stripe` fortalecido para ambiente real:
  - valida IDs existentes antes de reutilizar,
  - recria preco quando ID estiver invalido/incompativel.

## Migracoes
- Nenhuma.

## Impacto para o Usuario
- Menor risco de acesso indevido na Secretaria.
- Melhor clareza no cadastro/edicao de igrejas sobre quem acessa o dashboard.
- Menos friccao para contratar/alterar plano com checkout iniciado a partir dos botoes corretos.
- Melhor estabilidade no uso de cupom em producao.

## Impacto Tecnico
- Sem alteracao de schema.
- Sem breaking changes de API publica.
- Reforco de consistencia entre permissao de rota e visibilidade de UI.

## Check de Qualidade
- Testes de permissao de Secretaria por tipo de igreja executados com sucesso (6 cenarios).
- Verificacao de modo Stripe live realizada via shell.
- Diagnostico de producao concluido: erros de autenticacao Stripe dependem de chave live valida no ambiente Render.
