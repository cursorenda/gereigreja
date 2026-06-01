# Escola Dominical - Checklist de Homologacao (Config Local por Igreja)

Data: 01/06/2026
Escopo: apps configuracao, escola_biblica, eventos

## Objetivo

Validar com seguranca o comportamento church-first da configuracao EBD:
- primeiro usa configuracao da igreja
- se vazio, herda do ministerio

## Pre-condicoes

- Migrations aplicadas com sucesso.
- Usuario de teste com permissao de configuracao organizacional.
- Pelo menos 2 igrejas no mesmo ministerio (ideal para validar cenario multi-igreja).

## Cenario A - Configuracao local ativa

1. Abrir Gerenciar Igrejas.
2. Editar uma igreja.
3. Na aba EBD, preencher:
   - periodo
   - dia da semana
   - horario
4. Salvar alteracoes.

Resultado esperado:
- Dashboard EBD mostra origem da configuracao como local da igreja.
- Tela de turmas mostra origem local da configuracao.
- Wizard de cronograma sugere horario da igreja.
- Eventos macro da EBD usam horario local da igreja.

## Cenario B - Fallback ministerial

1. Na mesma igreja, limpar os 3 campos EBD locais.
2. Salvar alteracoes.
3. Garantir que o ministerio possui configuracao EBD preenchida.

Resultado esperado:
- Dashboard EBD mostra origem herdada do ministerio.
- Tela de turmas mostra origem herdada.
- Wizard usa horario do ministerio.
- Eventos macro seguem horario ministerial.

## Cenario C - Multi-igreja

1. Sem igreja ativa definida, abrir dashboard EBD.
2. Usar atalho Configurar EBD da igreja.
3. Validar redirecionamento para lista de igrejas.

Resultado esperado:
- Atalho nao desaparece no dashboard.
- Usuario chega na lista de igrejas para escolher a igreja correta.

## Cenario D - Aba EBD em Configuracao da Igreja

1. Abrir editar igreja.
2. Ir para aba EBD.
3. Validar secao Estrutura EBD - Classes.

Resultado esperado:
- Mini-lista exibe classes da igreja.
- Botao Gerenciar classes abre lista filtrada por igreja.
- Botao Nova classe abre formulario com igreja pre-selecionada.
- Botao Editar na mini-lista abre edicao da classe.

## Cenario E - Tela ministerial legado

1. Abrir configuracoes do ministerio.
2. Ir para aba Escola Biblica (legado).

Resultado esperado:
- Tela exibe aviso de modo legado.
- Tela aponta para Gerenciar Igrejas como fluxo principal.

## Cenario F - Validacao tecnica

1. Executar check do Django.
2. Revisar migrations aplicadas.

Resultado esperado:
- Sem erros de validacao de projeto.
- Sem migrations pendentes.

## Check de saida (Go/No-Go)

Marcar Go somente se todos os itens abaixo estiverem verdadeiros:

- Origem local e herdada alternam corretamente.
- Horario do wizard respeita local/ministerio conforme regra.
- Atalhos de configuracao por igreja estao visiveis e funcionais.
- Mini-lista de classes em EBD da igreja esta funcional.
- Nenhum erro em manage.py check.

## Rollback rapido

Se precisar rollback funcional sem reverter codigo:

- Limpar campos EBD locais nas igrejas.
- Manter apenas configuracao EBD ministerial.

Com isso o sistema volta a operar com comportamento herdado, preservando compatibilidade.
