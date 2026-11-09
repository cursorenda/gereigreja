# Desenvolvimento — Guias para o Ambiente de Desenvolvimento

Desenvolvimento  
↓  
Como executar tarefas recorrentes no ambiente local de desenvolvimento do GereIgreja.

Esta pasta reúne guias práticos voltados ao trabalho diário de desenvolvimento.

Ela não substitui:

- `docs/backend/` — padrões de engenharia e arquitetura de backend;
- `docs/frontend/` — padrões de engenharia de frontend;
- `docs/qualidade/` — critérios e procedimentos de qualidade;
- `docs/deploy/` — publicação e transição entre ambientes;
- `docs/infraestrutura/` — ambientes, serviços e infraestrutura;
- `docs/frameworks/` — políticas e referenciais estruturantes.

## Finalidade da pasta

- documentar comandos recorrentes de desenvolvimento local;
- orientar execução de testes;
- registrar setup local quando necessário;
- documentar ferramentas usadas no fluxo de desenvolvimento;
- reduzir dependência de conhecimento informal;
- centralizar guias operacionais voltados ao desenvolvedor.

## O que pertence nesta pasta

São adequados aqui documentos que respondem perguntas como:

```text
Como executar os testes localmente?
Como preparar o ambiente de desenvolvimento?
Como rodar uma ferramenta de apoio?
Como reproduzir uma rotina de desenvolvimento?
```

Não devem ser criados aqui documentos que definem:

- arquitetura;
- regras de negócio;
- políticas de qualidade;
- processos de deploy;
- runbooks de produção;
- padrões globais de segurança.

## Índice atual

| Documento | Finalidade | Situação |
|---|---|---|
| [Como-Rodar-Testes.md](Como-Rodar-Testes.md) | Execução local da suíte de testes | Canônico |

## Como-Rodar-Testes.md

Este documento está corretamente classificado nesta pasta.

Ele registra três formas de executar testes:

### Django

```bash
python manage.py test --settings=core.settings_test
```

### Pytest

```bash
python -m pytest -q
```

### Runner padronizado

```bash
python scripts/automation/test_runner.py
```

Também documenta o uso de:

```text
core.settings_test
```

para testes comuns e:

```text
core.settings_test_migrations
```

quando migrations reais precisam ser executadas.

## Fronteira com Qualidade

A divisão correta é:

```text
docs/desenvolvimento/
↓
como o desenvolvedor executa os testes

docs/qualidade/
↓
quais critérios devem ser satisfeitos
```

Exemplo:

```text
Como-Rodar-Testes.md
→ comando e ambiente de execução

Checklist de homologação
→ critérios de aprovação
```

Não duplicar os mesmos comandos em vários checklists sem necessidade.

## Fronteira com Backend

`docs/backend/` define padrões técnicos como:

- arquitetura de testes;
- organização de código;
- Services;
- Selectors;
- Models;
- autorização;
- padrões de implementação.

`docs/desenvolvimento/` deve permanecer mais operacional e orientado a tarefas.

## Ambientes de teste

Os guias desta pasta devem respeitar a matriz oficial de ambientes.

Para testes comuns:

```text
core.settings_test
→ SQLite em memória
```

Para testes que precisam executar migrations reais:

```text
core.settings_test_migrations
→ SQLite em memória
```

A configuração de desenvolvimento deve impedir que uma execução local de testes utilize banco de produção por engano.

## Regra para criar um novo guia

Antes de adicionar um novo arquivo:

1. confirme que a tarefa é recorrente no fluxo de desenvolvimento;
2. verifique se já existe documentação equivalente em backend, frontend, qualidade ou infraestrutura;
3. documente pré-requisitos;
4. informe o diretório de execução quando relevante;
5. registre comandos exatos;
6. explique resultado esperado;
7. destaque riscos de ambiente;
8. referencie documentação especializada;
9. mantenha exemplos compatíveis com o estado atual do projeto;
10. atualize este README.

## Nomenclatura

Guias podem utilizar nomes descritivos em formato legível.

Exemplos:

```text
Como-Rodar-Testes.md
Como-Configurar-Ambiente-Local.md
Como-Debugar-Localmente.md
```

Não é necessário criar uma sequência numérica nesta pasta.

O nome deve permitir identificar imediatamente a tarefa documentada.

## Estado atual

A pasta contém apenas um guia.

Isso não representa uma lacuna que precise ser preenchida artificialmente.

Novos arquivos só devem ser criados quando houver uma tarefa recorrente real que ainda dependa de conhecimento informal.

A família pode permanecer pequena.

## Possíveis lacunas futuras

Somente criar se a necessidade estiver comprovada.

Exemplos possíveis:

```text
Como-Configurar-Ambiente-Local.md
Como-Executar-Lint-e-Formatacao.md
Como-Debugar-Localmente.md
```

Esses nomes são exemplos de classificação, não documentos previstos ou obrigatórios.

## Relação com CI

O arquivo `Como-Rodar-Testes.md` cita um runner padronizado para equipe/CI.

Isso não transforma `docs/desenvolvimento/` na autoridade sobre CI/CD.

Configuração de pipeline, gates automatizados e infraestrutura de CI devem permanecer na família técnica responsável.

Aqui deve constar somente o que o desenvolvedor precisa saber para reproduzir localmente o comportamento relevante.

## Princípio de manutenção

Um guia de desenvolvimento deve ser executável.

Todo documento desta pasta deve permitir responder:

```text
O que quero executar?
Quais pré-requisitos existem?
Qual comando devo usar?
Em qual ambiente?
Qual resultado devo esperar?
Como evitar executar contra o ambiente errado?
```

Se o documento define política ou arquitetura em vez de orientar uma tarefa, provavelmente pertence a outra família.
