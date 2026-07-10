Pasta:
docs/backend/

Arquivo:
05-Services.md

Documento:
GBE-05

Seção:
Backend

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 05 - Services

> "Toda regra de negócio deve possuir um único lugar para existir. No GereIgreja, esse lugar são os Services."

---

# Sumário

1. Objetivo
2. Filosofia dos Services
3. Papel dos Services na Arquitetura
4. Responsabilidade dos Services
5. Estrutura Oficial
6. Organização do Diretório services/
7. Convenções de Nomenclatura
8. Fluxo de Execução
9. Comunicação com Models
10. Comunicação com Selectors
11. Comunicação com Views
12. Comunicação entre Apps
13. Boas Práticas
14. Documentos Relacionados
15. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para implementação da camada de Services do GereIgreja.

Seu propósito é centralizar toda a lógica de negócio da plataforma, garantindo organização, reutilização, testabilidade e consistência entre os módulos.

Toda regra de negócio deverá ser implementada nesta camada.

---

# 2. Filosofia dos Services

Os Services representam o coração da lógica da aplicação.

Enquanto os Models representam dados e as Views coordenam requisições, os Services executam as regras do domínio.

Todo processamento relevante deverá ocorrer nesta camada.

Os Services devem ser:

- pequenos;
- especializados;
- reutilizáveis;
- testáveis;
- independentes da interface.

A lógica implementada em um Service deve poder ser utilizada por uma View Web, uma API, uma Task assíncrona ou um comando administrativo sem qualquer alteração.

---

# 3. Papel dos Services na Arquitetura

Na arquitetura oficial do GereIgreja, os Services ocupam a camada central da aplicação.

Fluxo oficial:

```text
Usuário

↓

URL

↓

View

↓

Permissões

↓

Form / Serializer

↓

Service

↓

Selector (quando necessário)

↓

Model

↓

Banco de Dados
```

Nenhuma camada superior deverá implementar regras de negócio que pertençam aos Services.

---

# 4. Responsabilidade dos Services

Os Services poderão ser responsáveis por:

- criação de registros;
- atualização de dados;
- exclusão lógica;
- validações de negócio;
- cálculos;
- processamento de informações;
- integrações entre módulos;
- integração com APIs externas;
- envio de eventos;
- auditoria;
- coordenação de operações complexas.

Não deverão ser responsáveis por:

- renderização de templates;
- definição de URLs;
- consultas exclusivamente de leitura (Selectors);
- configuração de formulários;
- componentes visuais.

---

# 5. Estrutura Oficial

Cada App poderá possuir seu próprio diretório de Services.

Estrutura recomendada:

```text
services/

__init__.py

membro_service.py

familia_service.py

cargo_service.py

importacao_service.py

relatorio_service.py
```

Quando o módulo for pequeno, poderá existir apenas um arquivo:

```text
services.py
```

À medida que o projeto crescer, a divisão em múltiplos arquivos será obrigatória.

---

# 6. Organização do Diretório services/

Cada arquivo deverá possuir responsabilidade única.

Exemplo:

```text
services/

membro_service.py

→ operações relacionadas aos membros

familia_service.py

→ operações relacionadas às famílias

cargo_service.py

→ operações relacionadas aos cargos

importacao_service.py

→ importações

relatorio_service.py

→ geração de relatórios
```

Evitar Services genéricos contendo regras de múltiplos domínios.

---

# 7. Convenções de Nomenclatura

Classes deverão utilizar o padrão:

```python
MembroService

FamiliaService

FinanceiroService

EventoService
```

Métodos deverão utilizar verbos.

Exemplos:

```python
criar()

atualizar()

desativar()

reativar()

cancelar()

registrar()

importar()

exportar()

processar()
```

Evitar nomes genéricos como:

```python
executar()

fazer()

processo()

acao()
```

O nome do método deve indicar claramente sua finalidade.

---

# 8. Fluxo de Execução

Todo processamento deverá seguir uma sequência previsível.

Exemplo:

```text
Receber parâmetros

↓

Validar regras de negócio

↓

Consultar dados (Selectors)

↓

Executar alterações (Models)

↓

Registrar auditoria

↓

Retornar resultado
```

Esse fluxo facilita testes, manutenção e depuração.

---

# 9. Comunicação com Models

Os Services são a principal camada autorizada a modificar os Models.

Exemplos:

- criar registros;
- atualizar entidades;
- excluir logicamente;
- alterar status;
- persistir alterações.

Toda modificação deverá passar por um Service.

---

# 10. Comunicação com Selectors

Quando um Service precisar realizar consultas complexas, deverá utilizar Selectors.

Exemplo:

```python
membros = MembroSelector.listar_ativos(igreja)
```

Isso evita duplicação de consultas e mantém a separação entre leitura e escrita.

---

# 11. Comunicação com Views

As Views não deverão conhecer detalhes da lógica de negócio.

Fluxo recomendado:

```python
resultado = MembroService.criar(dados)
```

A View apenas:

- recebe a requisição;
- valida a entrada;
- chama o Service;
- devolve a resposta.

---

# 12. Comunicação entre Apps

Quando um módulo precisar utilizar funcionalidades de outro, a integração deverá ocorrer preferencialmente por meio dos Services públicos desse módulo.

Exemplo:

```python
FinanceiroService.registrar_recebimento()

EventoService.confirmar_inscricao()
```

Evitar acesso direto aos Models de outro domínio quando existir um Service apropriado.

---

# 13. Boas Práticas

Os Services deverão:

- possuir responsabilidade única;
- ser reutilizáveis;
- ser pequenos;
- possuir documentação quando necessário;
- facilitar testes automatizados;
- evitar dependências desnecessárias;
- respeitar a arquitetura da plataforma.

Sempre que um Service crescer excessivamente, avaliar sua divisão em novos Services.

---

# 14. Documentos Relacionados

- GEA-02 — Arquitetura da Plataforma
- GEA-03 — Arquitetura dos Módulos
- GBE-03 — Arquitetura dos Apps
- GBE-04 — Models
- GBE-06 — Selectors
- GAF — Framework de Autenticação
- GQF — Framework de Qualidade

---

# 15. Princípios Finais

Os Services representam a camada responsável por transformar regras de negócio em comportamento consistente da aplicação.

Toda funcionalidade relevante deverá passar por essa camada.

A centralização da lógica reduz duplicação, facilita manutenção e garante que diferentes interfaces (Web, API, tarefas assíncronas e integrações) compartilhem exatamente o mesmo comportamento.

A qualidade dos Services influencia diretamente a confiabilidade, escalabilidade e evolução do GereIgreja.

---

# 16. Transações (Transactions)

Operações que envolvam múltiplas alterações no banco de dados deverão ser executadas dentro de transações.

O padrão oficial será utilizar:

```python
from django.db import transaction

@transaction.atomic
def registrar_membro(...):
    ...
```

Sempre que uma operação envolver:

- criação de múltiplos registros;
- alterações em tabelas diferentes;
- movimentações financeiras;
- importações;
- alterações críticas;

deverá ser utilizada uma transação atômica.

Caso qualquer etapa falhe, toda a operação deverá ser revertida (rollback).

A integridade dos dados é prioridade.

---

# 17. Tratamento de Exceções

Os Services deverão capturar apenas exceções que possam tratar adequadamente.

Evitar:

```python
except:
    pass
```

Ou:

```python
except Exception:
    ...
```

sem necessidade.

Preferir exceções específicas.

Exemplo:

```python
except Membro.DoesNotExist:
    ...
```

ou

```python
except ValidationError:
    ...
```

Exceções inesperadas deverão ser registradas e propagadas para tratamento global.

---

# 18. Validações de Negócio

Validações relacionadas ao domínio pertencem aos Services.

Exemplos:

- impedir matrícula duplicada;
- impedir movimentação financeira em caixa fechado;
- impedir exclusão de registros vinculados;
- validar regras ministeriais;
- validar limites operacionais.

Não confundir validações de negócio com validações de formulário ou serializer.

---

# 19. Idempotência

Sempre que possível, os Services deverão ser idempotentes.

Ou seja:

Executar a mesma operação diversas vezes deverá produzir o mesmo resultado quando apropriado.

Exemplos:

- confirmar inscrição;
- sincronizar dados;
- importar registros;
- atualizar cadastro.

Isso reduz inconsistências causadas por repetição de requisições.

---

# 20. Logging

Operações relevantes deverão produzir registros de log.

Exemplos:

- início de processamento;
- conclusão;
- falhas;
- integrações;
- operações demoradas.

Os logs deverão ser claros e objetivos.

Jamais registrar:

- senhas;
- tokens;
- dados sensíveis;
- informações pessoais desnecessárias.

---

# 21. Auditoria

Além dos logs técnicos, determinadas operações deverão gerar registros de auditoria.

Exemplos:

- criação de usuários;
- alteração de permissões;
- movimentações financeiras;
- alteração cadastral;
- exclusões;
- exportações de dados.

A auditoria deverá permitir rastreabilidade completa.

---

# 22. Integrações Externas

Todo acesso a serviços externos deverá ocorrer através de Services especializados.

Exemplos:

```text
WhatsappService

EmailService

SmsService

CepService

PagamentoService

GoogleCalendarService
```

Nunca espalhar chamadas HTTP diretamente pelo sistema.

Isso facilita:

- manutenção;
- substituição de provedores;
- testes;
- monitoramento.

---

# 23. Comunicação com APIs

Quando um Service consumir APIs externas deverá:

- validar respostas;
- tratar timeouts;
- tratar indisponibilidade;
- registrar erros;
- prever retentativas quando apropriado.

Nunca assumir que um serviço externo estará sempre disponível.

---

# 24. Comunicação entre Services

Um Service poderá utilizar outro Service quando houver dependência de domínio.

Exemplo:

```python
EventoService.confirmar_inscricao()

↓

FinanceiroService.registrar_pagamento()

↓

NotificacaoService.enviar_confirmacao()
```

Entretanto, evitar cadeias longas de chamadas que dificultem o entendimento do fluxo.

---

# 25. Composição de Services

Operações complexas poderão ser compostas por diversos Services menores.

Exemplo:

```text
CadastroService

↓

ValidacaoService

↓

MembroService

↓

FamiliaService

↓

AuditoriaService

↓

NotificacaoService
```

Essa abordagem favorece reutilização e reduz duplicação de código.

---

# 26. Performance

Os Services deverão evitar:

- consultas repetidas;
- loops com acesso ao banco;
- processamento desnecessário;
- carregamento de grandes volumes de dados sem paginação.

Sempre utilizar Selectors para consultas complexas.

Quando necessário:

- select_related();
- prefetch_related();
- bulk_create();
- bulk_update();
- cache.

---

# 27. Retorno dos Services

Os Services deverão retornar informações claras e previsíveis.

Evitar múltiplos formatos de retorno.

Preferir objetos, dataclasses ou estruturas padronizadas.

Exemplo conceitual:

```python
ResultadoService(
    sucesso=True,
    mensagem="Membro cadastrado com sucesso.",
    dados=membro
)
```

A padronização facilita integração com Views, APIs e Tasks.

---

# 28. Reutilização

Um Service deverá poder ser utilizado por:

- Views Web;
- APIs REST;
- Comandos administrativos;
- Tasks assíncronas;
- Scripts de importação;
- Testes automatizados.

Se um Service depende da interface, provavelmente sua responsabilidade está incorreta.

---

# 29. Testabilidade

Os Services deverão ser escritos para facilitar testes unitários.

Boas práticas:

- métodos pequenos;
- poucas dependências;
- injeção de dependências quando necessário;
- ausência de efeitos colaterais desnecessários.

Quanto mais isolado o Service, mais fácil será testá-lo.

---

# 30. Documentação dos Services

Services relevantes deverão possuir documentação.

Exemplo:

```python
class MembroService:
    """
    Responsável pelas regras de negócio
    relacionadas aos membros da igreja.
    """
```

Métodos públicos também deverão ser documentados quando executarem processos complexos.

A documentação facilita manutenção e onboarding.

---

# 31. Exemplo de Estrutura de um Service

Cada Service deverá possuir uma responsabilidade claramente definida.

Exemplo:

```python
class MembroService:

    @staticmethod
    def criar(dados):
        ...

    @staticmethod
    def atualizar(membro, dados):
        ...

    @staticmethod
    def desativar(membro):
        ...

    @staticmethod
    def reativar(membro):
        ...
```

Os métodos deverão ser pequenos, objetivos e focados em uma única operação.

---

# 32. Organização por Domínio

À medida que um módulo crescer, os Services poderão ser divididos por domínio.

Exemplo:

```text
services/

cadastro_service.py

financeiro_service.py

ministerio_service.py

importacao_service.py

relatorio_service.py

notificacao_service.py
```

Cada arquivo deverá concentrar apenas responsabilidades relacionadas ao seu domínio.

Evitar arquivos com centenas de linhas.

---

# 33. Exemplo de Fluxo Completo

Um cadastro de membro poderá seguir o seguinte fluxo:

```text
View

↓

Form

↓

MembroService.criar()

↓

Validação de negócio

↓

Selector (verificar CPF duplicado)

↓

Model.save()

↓

Auditoria

↓

Notificação

↓

Resposta
```

Todo o processamento ocorre dentro do Service.

---

# 34. Comunicação com o Core

Sempre que um comportamento for reutilizado por diversos módulos, ele deverá ser movido para o Core.

Exemplos:

- envio de e-mails;
- geração de protocolos;
- geração de números sequenciais;
- auditoria;
- upload de arquivos;
- exportação de dados.

Os Services dos Apps deverão consumir essas funcionalidades compartilhadas.

---

# 35. Comunicação com Tasks

Processamentos demorados não deverão bloquear a resposta ao usuário.

Sempre que apropriado, delegar para Tasks.

Exemplos:

- envio de e-mails em massa;
- geração de relatórios extensos;
- importações grandes;
- sincronizações externas;
- processamento de imagens.

O Service deverá apenas iniciar o processamento.

---

# 36. Comunicação com Signals

Signals deverão complementar os Services, nunca substituí-los.

Fluxo recomendado:

```text
Service

↓

Model.save()

↓

Signal

↓

Atualização de estatísticas

↓

Logs

↓

Notificações secundárias
```

Regras críticas jamais deverão depender exclusivamente de Signals.

---

# 37. Escalabilidade

Os Services deverão ser preparados para o crescimento da plataforma.

Boas práticas:

- métodos pequenos;
- baixa dependência;
- reutilização;
- separação por domínio;
- documentação;
- testes automatizados.

A escalabilidade começa na organização do código.

---

# 38. Exemplo de Organização Completa

```text
membros/

services/

__init__.py

cadastro_service.py

atualizacao_service.py

ministerio_service.py

familia_service.py

importacao_service.py

relatorio_service.py

estatistica_service.py

auditoria_service.py
```

Essa estrutura facilita localização e evolução.

---

# 39. Anti-patterns

Evitar:

- Services com milhares de linhas;
- métodos enormes;
- múltiplas responsabilidades;
- consultas SQL espalhadas;
- lógica duplicada;
- dependências circulares;
- chamadas HTTP diretamente em Views;
- regras de negócio dentro dos Models;
- regras de negócio dentro dos Forms;
- regras de negócio dentro dos Templates.

Esses problemas aumentam significativamente o custo de manutenção.

---

# 40. Refatoração Contínua

Sempre que um Service crescer demasiadamente:

- dividir métodos;
- criar novos Services especializados;
- extrair componentes reutilizáveis;
- mover funcionalidades para o Core quando aplicável.

A arquitetura deverá evoluir continuamente.

---

# 41. Checklist para Criação de um Service

Antes da implementação verificar:

- responsabilidade única;
- nome adequado;
- reutilização possível;
- validações de negócio implementadas;
- tratamento de exceções previsto;
- auditoria considerada;
- transações avaliadas;
- documentação criada;
- testes planejados.

---

# 42. Checklist para Revisão

Durante uma revisão arquitetural verificar:

- código limpo;
- ausência de duplicação;
- métodos pequenos;
- separação adequada de responsabilidades;
- uso correto de Selectors;
- uso correto de Models;
- logs apropriados;
- tratamento adequado de erros;
- documentação atualizada.

---

# 43. Evolução dos Services

A camada de Services deverá evoluir continuamente.

Novos requisitos poderão exigir:

- especialização de Services;
- reorganização por domínio;
- novas integrações;
- otimizações;
- melhoria dos fluxos internos.

As mudanças deverão preservar a simplicidade e a previsibilidade da arquitetura.

---

# 44. Documentos Relacionados

- GEA-02 — Arquitetura da Plataforma
- GEA-03 — Arquitetura dos Módulos
- GBE-03 — Arquitetura dos Apps
- GBE-04 — Models
- GBE-06 — Selectors
- GBE-07 — Managers
- GAF — Framework de Autenticação
- GSF — Framework de Segurança
- GQF — Framework de Qualidade

---

# 45. Princípios Finais

Os Services representam a camada onde reside toda a inteligência de negócio do GereIgreja.

Cada regra deverá possuir um único local de implementação, evitando duplicações e garantindo consistência entre todas as interfaces da plataforma.

Services bem estruturados tornam o sistema mais previsível, reutilizável, testável e preparado para crescer.

Ao centralizar a lógica de negócio nessa camada, o GereIgreja preserva uma arquitetura limpa, modular e sustentável, capaz de evoluir continuamente sem comprometer a organização do código.

Toda funcionalidade crítica da plataforma deverá nascer, evoluir e ser mantida dentro dos Services, respeitando os princípios definidos pela Engenharia do GereIgreja.

