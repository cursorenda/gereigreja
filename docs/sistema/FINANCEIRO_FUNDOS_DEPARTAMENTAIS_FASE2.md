# Financeiro - Fundos Departamentais (Fase 2)

## Objetivo
Adicionar regras de consistencia por fundo departamental sem alterar fluxo visual atual.

## Escopo da Fase 2
- Evento sempre deve operar no fundo `EVENTOS`.
- Receita no fundo `EVENTOS` aceita apenas categoria `doacao`.
- Fluxos de receita em contexto de evento aplicam `doacao` automaticamente no backend.
- Regras implementadas no dominio (`models`) para manter consistencia em qualquer interface.

## Regras implementadas

### 1) Vinculo Evento x Fundo
- `Receitas`: se houver `evento`, o fundo deve ser `EVENTOS`.
- `Despesas`: se houver `evento`, o fundo deve ser `EVENTOS`.

### 2) Categoria de receita por fundo
- `EVENTOS`: somente `doacao`.
- `MISSOES`: `oferta`, `campanha`, `outro`.
- `ASSISTENCIA`: `doacao`, `campanha`, `outro`.
- `LOCAL`: `dizimo`, `oferta`, `voto`, `campanha`, `outro`.

## Compatibilidade e seguranca
- Sem mudanca de tela/formulario nesta fase.
- Com migracao de metadados do campo de categoria e normalizacao de dados legados (`oferta` -> `doacao`) para fundos `EVENTOS` e `ASSISTENCIA`.
- Fluxos existentes continuam funcionando; regras novas reforcam integridade para novas operacoes.

## Testes adicionados
- Validacao de evento com fundo incorreto em receita e despesa.
- Validacao de categoria `dizimo` bloqueada no fundo `EVENTOS`.

## Proxima fase
- Fase 3: introduzir selectors/services especificos por fundo para reduzir acoplamento das views e preparar cockpit premium por departamento.
