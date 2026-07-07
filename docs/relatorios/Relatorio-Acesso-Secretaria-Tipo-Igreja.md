# Relatorio breve: acesso da Secretaria por perfil e tipo de igreja

## Regra aplicada

- Secretario Local: sempre pode acessar Secretaria.
- Admin/Presidente: pode acessar somente quando a igreja ativa for do tipo Sede (S) ou Independente (D).
- Admin/Presidente: nao pode acessar quando a igreja ativa for Regional (R) ou Congregacao (C).
- Usuario comum: nunca pode acessar.

## Impacto em seguranca

- Reduz risco de administracao indevida da Secretaria em niveis Regional/Congregacao para perfis ministeriais.
- Centraliza a regra em uma unica funcao (`pode_acessar_secretaria`), diminuindo inconsistencias entre telas.
- Mantem excecao explicita para Secretario Local, preservando o papel operacional.

## Impacto em usabilidade

- O dashboard e as telas da Secretaria passam a refletir o mesmo criterio de permissao da camada de protecao de views.
- Admin/Presidente continua com fluidez operacional nos contextos Sede/Independente, sem liberacao ampla em toda a arvore.

## Impacto em escalabilidade

- A regra centralizada facilita evolucao futura (novos tipos de igreja, novos perfis, politicas por modulo).
- O uso da matriz de permissoes por pagina evita duplicacao de condicoes em views individuais.
- A suite de testes cobre os 6 cenarios principais e previne regressao em alteracoes futuras.
