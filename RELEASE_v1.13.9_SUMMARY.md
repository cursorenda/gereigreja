# RELEASE v1.13.9 - RESUMO EXECUTIVO

Data: 28/05/2026
Tipo: PATCH
Escopo: Escola Dominical (EBD)

## Resumo
A versao v1.13.9 consolida a governanca de periodo da EBD com base na configuracao do ministerio e padroniza o cabecalho do dashboard EBD para o mesmo comportamento visual dos demais dashboards do sistema.

## Principais Entregas
- Periodo EBD parametrizado por ministerio aplicado no backend do modulo.
- Dashboard EBD com filtro por Ano letivo + Periodo configurado.
- Comparativos e leituras do dashboard baseados no periodo selecionado e janela anterior equivalente.
- Cabecalho do dashboard EBD alinhado ao padrao de posicionamento (titulo, breadcrumb, filtros e chips de escopo).
- Breadcrumb atualizado para Home > Escola Dominical > Visao Geral.
- Correcao de formatacao do ano no filtro (2026 sem separador de milhar).

## Impacto para o Usuario
- Mais previsibilidade: o modulo respeita automaticamente o tipo de periodo definido pelo ministerio.
- Mais consistencia de uso: padrao visual e de navegacao igual aos demais dashboards.
- Melhor leitura operacional para secretaria/superintendencia EBD.

## Impacto Tecnico
- Sem migracoes de banco.
- Sem alteracoes de API publica.
- Compatibilidade mantida com fluxos existentes.

## Check de Qualidade
- Validacao Django executada com sucesso (`manage.py check`).
