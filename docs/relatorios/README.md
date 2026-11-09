# Relatórios — Análises, Diagnósticos e Evidências

Relatórios  
↓  
Registros analíticos e históricos produzidos para apoiar decisões, auditorias técnicas e evolução do GereIgreja.

Esta pasta reúne documentos de natureza analítica, diagnóstica ou executiva.

Ela não é uma família normativa.

Relatórios descrevem o que foi observado, analisado ou recomendado em determinado contexto e momento.

## Finalidade da pasta

- registrar análises técnicas ou funcionais;
- consolidar diagnósticos;
- documentar comparação de cenários;
- registrar evidências que apoiaram uma decisão;
- preservar resumos executivos;
- manter relatórios pontuais de impacto, acesso, UX ou arquitetura;
- permitir rastrear o raciocínio histórico que levou a uma mudança.

## Fronteira com outras famílias

### `docs/apps/`

Contém a regra funcional canônica atual de cada domínio.

Um relatório pode ter servido como fonte para consolidar uma regra em `apps/`, mas não deve continuar sendo tratado como autoridade superior ao documento canônico.

### `docs/arquitetura/`

Define arquitetura vigente.

Uma análise arquitetural pontual pode permanecer em `relatorios/`, mas decisões adotadas devem ser refletidas na arquitetura e, quando necessário, em ADR.

### `docs/auditoria/`

É destinada a registros formais de auditoria, evidências de conformidade e verificações controladas.

Nem todo relatório é auditoria.

### `docs/qualidade/`

Contém procedimentos recorrentes de validação.

Relatórios de execução, achados ou diagnósticos históricos não devem virar checklists permanentes apenas porque analisam qualidade.

### `docs/release-notes/`

Registra o que mudou em uma release.

Relatórios explicam análise ou impacto; release notes registram entrega.

## Índice atual

| Documento | Natureza | Situação |
|---|---|---|
| [Relatorio-Acesso-Secretaria-Tipo-Igreja.md](Relatorio-Acesso-Secretaria-Tipo-Igreja.md) | Relatório de regra de acesso e impacto | Manter como evidência histórica |
| [RESUMO_EXECUTIVO_CADASTROS.md](RESUMO_EXECUTIVO_CADASTROS.md) | Resumo executivo de análise | Manter |
| [README_ANALISE_CADASTROS.md](README_ANALISE_CADASTROS.md) | Guia/resumo de um conjunto de análises | Manter, mas não confundir com README da pasta |
| [INDICE_ANALISE_CADASTROS.md](INDICE_ANALISE_CADASTROS.md) | Índice temático de análise | Manter |
| [ANTES_E_DEPOIS_CONSOLIDACAO.md](ANTES_E_DEPOIS_CONSOLIDACAO.md) | Comparação de cenários | Manter |
| [ANALISE_CADASTRO_PESSOA_ALUNO.md](ANALISE_CADASTRO_PESSOA_ALUNO.md) | Análise técnica/funcional | Manter |
| [PROBLEMA_UX_PAGINA_VAZIA.md](PROBLEMA_UX_PAGINA_VAZIA.md) | Diagnóstico de UX | Manter como análise histórica |

## Ausência de README canônico

A pasta não possuía um:

```text
docs/relatorios/README.md
```

O arquivo:

```text
README_ANALISE_CADASTROS.md
```

não é o README da família.

Ele é um documento temático referente especificamente à análise dos cadastros Secretaria × EBD.

Essa distinção deve permanecer clara.

## Relatório de Acesso da Secretaria

`Relatorio-Acesso-Secretaria-Tipo-Igreja.md` registra uma regra aplicada e seus impactos em:

- segurança;
- usabilidade;
- escalabilidade.

Esse relatório foi útil como evidência para consolidar a documentação funcional da Secretaria.

Hoje, a regra canônica deve ser consultada primeiro em:

```text
docs/apps/02-Secretaria.md
```

O relatório continua válido como evidência histórica da implementação e da motivação.

## Conjunto de Análise de Cadastros

Existe um conjunto documental dedicado ao problema de duplicidade entre cadastros de Pessoa na Secretaria e registros da EBD.

Esse conjunto inclui:

```text
RESUMO_EXECUTIVO_CADASTROS.md
README_ANALISE_CADASTROS.md
INDICE_ANALISE_CADASTROS.md
ANTES_E_DEPOIS_CONSOLIDACAO.md
ANALISE_CADASTRO_PESSOA_ALUNO.md
```

O material documenta:

- problema observado;
- alternativas;
- recomendação;
- roadmap;
- impacto;
- proposta técnica.

Ele deve ser tratado como fotografia analítica daquele momento.

Afirmações como:

```text
"pronto para sprint"
"baixo risco"
"sem breaking changes"
```

não devem ser reutilizadas automaticamente como verdade atual sem verificar o código e o estado atual do projeto.

## ANALISE_SISTEMA_DEPLOY.md

A auditoria de `docs/deploy/` identificou:

```text
ANALISE_SISTEMA_DEPLOY.md
```

Esse documento analisa historicamente o sistema interno de deploy na versão 1.5.0, incluindo:

- pontos fortes;
- problemas;
- melhorias;
- propostas;
- exemplos de implementação.

Por natureza, ele se encaixa melhor em `docs/relatorios/` do que em `docs/deploy/`.

Reclassificação recomendada:

```text
docs/deploy/ANALISE_SISTEMA_DEPLOY.md
        ↓
docs/relatorios/ANALISE_SISTEMA_DEPLOY.md
```

Não mover antes de verificar referências no repositório.

## Relatório versus Documento Canônico

A relação correta é:

```text
Relatório
↓
observa / analisa / recomenda

Decisão
↓
é adotada ou rejeitada

Documento canônico
↓
registra a regra vigente
```

Portanto, um relatório não deve permanecer como única fonte de uma regra funcional ou arquitetural já adotada.

Quando a conclusão de um relatório virar regra oficial:

- atualizar `apps/`, `arquitetura/`, `seguranca/` ou família responsável;
- criar ADR quando a decisão for arquiteturalmente relevante;
- manter o relatório como histórico.

## Regra para criar um novo relatório

Antes de adicionar arquivo em `docs/relatorios/`:

1. identifique claramente o objeto analisado;
2. registre data ou contexto temporal;
3. diferencie fato observado de recomendação;
4. informe fontes ou evidências utilizadas;
5. registre limitações da análise;
6. não apresente proposta como implementação concluída;
7. indique decisão tomada posteriormente, quando conhecida;
8. aponte para o documento canônico se a regra já tiver sido consolidada.

## Nomenclatura

Relatórios não exigem numeração sequencial.

Nomes devem ser descritivos.

Exemplos adequados:

```text
ANALISE_SISTEMA_DEPLOY.md
Relatorio-Acesso-Secretaria-Tipo-Igreja.md
ANALISE_CADASTRO_PESSOA_ALUNO.md
```

Evitar nomes genéricos como:

```text
RELATORIO.md
ANALISE.md
NOVO_RELATORIO.md
```

## Família contínua

`docs/relatorios/` é uma família **contínua**.

Ela não possui um número final planejado.

Novos relatórios podem surgir conforme novas análises forem realmente necessárias.

Isso é diferente de famílias baseline como API, Segurança ou Frameworks.

## Retenção e obsolescência

Relatório antigo não precisa ser apagado apenas porque deixou de representar o estado atual.

Seu valor pode ser histórico.

Entretanto, deve ficar claro quando:

- a recomendação foi implementada;
- a recomendação foi rejeitada;
- a arquitetura mudou;
- o diagnóstico não representa mais o sistema.

Documentação histórica não deve parecer normativa por acidente.

## Princípio de manutenção

Todo relatório deve permitir distinguir:

```text
O que foi observado?
Quando?
Com quais evidências?
O que foi concluído?
O que foi apenas recomendado?
Qual é a fonte canônica atual?
```

Se essas distinções não estiverem claras, o relatório pode induzir decisões baseadas em contexto antigo.
