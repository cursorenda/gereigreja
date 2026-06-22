# RELEASE v1.13.22 - RESUMO EXECUTIVO

Data: 22/06/2026
Tipo: PATCH
Escopo: proteção de agrupamentos manuais no fluxo de Grupos/Casas da Secretaria

## Resumo
A versão v1.13.22 corrige um risco operacional crítico no módulo de Grupos/Casas da Secretaria. O agrupamento automático deixava de respeitar, em cenários específicos, decisões manuais de remanejamento, podendo desfazer trabalho já concluído pela equipe. A atualização estabelece proteção de vínculos manuais e melhora a rastreabilidade da execução.

## Principais Entregas
- Proteção de vínculos manuais durante agrupamento automático:
  - o processo automático não remaneja mais pessoas que já possuem grupo/casa definido;
  - o automático passa a atuar como complemento seguro para pessoas sem vínculo.
- Mensageria operacional aprimorada:
  - o sistema informa quantos vínculos manuais foram preservados em cada execução de agrupar/reagrupar.

## Arquivos Impactados
- secretaria/utils.py
- secretaria/views/grupos_casa.py
- CHANGELOG.md

## Migrações
- Nenhuma.

## Validação
- python manage.py check executado com sucesso (0 issues).

## Impacto para o Usuário
- Segurança para manter grupos/casas montados manualmente.
- Menor risco de retrabalho e perda de organização pastoral.
- Fluxo automático e fluxo manual passam a coexistir sem conflito.

## Impacto Técnico
- Hardenização das regras de associação em agrupar/reagrupar.
- Telemetria funcional mais clara via mensagens de retorno.
- Sem alterações de schema e sem breaking changes.
