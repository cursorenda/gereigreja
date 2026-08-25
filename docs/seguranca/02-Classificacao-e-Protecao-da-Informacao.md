````markdown
Pasta:

docs/seguranca/

Arquivo:

02-Classificacao-e-Protecao-da-Informacao.md

Documento:

GSF-02

Código:

GSF-DATA-CLASSIFICATION

Família:

GSF — GereIgreja Security

Framework:

GSF — GereIgreja Security Framework

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GSF-02 — Classificação e Proteção da Informação

> "Nem toda informação possui o mesmo nível de sensibilidade. A proteção deverá ser proporcional ao risco, à finalidade e ao impacto de sua exposição."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Princípios
5. Informação como Ativo
6. Classificação Oficial
7. Informação Pública
8. Informação Interna
9. Informação Restrita
10. Informação Confidencial
11. Critérios de Classificação
12. Dados Pessoais
13. Dados Financeiros
14. Dados Ministeriais
15. Dados de Autenticação e Segurança
16. Dados Organizacionais
17. Configurações e Dados Técnicos
18. Credenciais e Segredos
19. Dados de Crianças e Adolescentes
20. Dados em Módulos do GereIgreja
21. Princípio da Minimização
22. Necessidade de Acesso
23. Coleta
24. Processamento
25. Armazenamento
26. Consulta
27. Exibição
28. Transmissão
29. Exportação
30. Relatórios
31. Logs e Auditoria
32. Cache
33. Backups
34. Integrações
35. APIs
36. Uploads e Arquivos
37. Ambientes de Desenvolvimento e Teste
38. Exclusão e Retenção
39. Mudança de Classificação
40. Isolamento Multi-Tenant
41. Controle de Acesso por Classificação
42. Exposição Acidental
43. Incidentes envolvendo Informação
44. Responsabilidades
45. Matriz de Classificação
46. Evidências Arquiteturais
47. Especificações Oficiais
48. Anti-Padrões
49. Checklist
50. Documentos Relacionados
51. Princípios Finais
52. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial de classificação e proteção das informações processadas pelo GereIgreja.

Seu objetivo é permitir que dados sejam protegidos de acordo com:

- sensibilidade;
- finalidade;
- contexto;
- impacto;
- necessidade de acesso;
- obrigação legal;
- risco de exposição;
- escopo organizacional.

A classificação deverá orientar decisões relacionadas a:

- armazenamento;
- acesso;
- visualização;
- transmissão;
- logging;
- auditoria;
- exportação;
- integração;
- retenção;
- exclusão;
- backup.

A existência de um dado no sistema não significa que todos os usuários autenticados possam acessá-lo.

---

# 2. Escopo

Este documento aplica-se a informações processadas em toda a plataforma GereIgreja.

Inclui informações presentes em:

- Core;
- Secretaria;
- Financeiro;
- Escola Bíblica;
- Eventos;
- Comunicação;
- Patrimônio;
- relatórios;
- configurações;
- usuários;
- Área de Gestão;
- Django Admin;
- Portal Público;
- APIs;
- integrações;
- automações;
- tarefas;
- banco de dados;
- logs;
- backups;
- exports;
- arquivos.

Também se aplica a informações temporariamente processadas, mesmo quando não são persistidas no banco de dados.

---

# 3. Papel deste Documento

O GSF-02 especializa o princípio de classificação estabelecido pelo GereIgreja Security Framework.

Sua posição documental é:

```text
GSF
 │
 ▼
GSF-01 — Fundamentos de Segurança
 │
 ▼
GSF-02 — Classificação e Proteção da Informação
 │
 ├── Identidade
 ├── Autorização
 ├── Multi-Tenant
 ├── Dados e Privacidade
 ├── APIs
 ├── Logging
 ├── Backup
 └── Conformidade
````

A classificação definida neste documento deverá ser utilizada pelos documentos especializados posteriores.

---

# 4. Princípios

A proteção da informação deverá observar:

* necessidade;
* finalidade;
* minimização;
* menor privilégio;
* confidencialidade;
* integridade;
* disponibilidade;
* rastreabilidade;
* isolamento;
* proporcionalidade.

Regra fundamental:

```text
Quanto maior a sensibilidade
          ↓
maior deverá ser o controle
```

Entretanto, informação de menor classificação não deverá ser considerada automaticamente irrelevante para segurança.

---

# 5. Informação como Ativo

Informação deverá ser tratada como ativo da plataforma e das organizações atendidas.

Ela poderá existir em diferentes estados:

```text
Em repouso
    │
    ├── Banco
    ├── Arquivo
    ├── Cache
    └── Backup

Em trânsito
    │
    ├── HTTPS
    ├── API
    ├── Integração
    └── Serviço externo

Em processamento
    │
    ├── Aplicação
    ├── Task
    ├── Relatório
    └── Automação
```

A classificação permanece relevante durante todos esses estados.

---

# 6. Classificação Oficial

O GereIgreja adota quatro níveis oficiais:

```text
PÚBLICA
   │
   ▼
INTERNA
   │
   ▼
RESTRITA
   │
   ▼
CONFIDENCIAL
```

As categorias representam níveis crescentes de necessidade de proteção.

| Classificação | Exposição                        | Controle esperado                |
| ------------- | -------------------------------- | -------------------------------- |
| Pública       | Pode ser destinada ao público    | Básico                           |
| Interna       | Uso operacional interno          | Controlado                       |
| Restrita      | Acesso limitado por função       | Elevado                          |
| Confidencial  | Informação de alta sensibilidade | Máximo compatível com o contexto |

A classificação deverá considerar o conteúdo real e não apenas o nome do campo ou da funcionalidade.

---

# 7. Informação Pública

Informação Pública é aquela cuja divulgação é autorizada ou necessária para a finalidade da plataforma.

Exemplos poderão incluir:

* informações institucionais destinadas ao Portal Público;
* horários de cultos publicados;
* endereço público da igreja;
* canais oficiais de contato;
* eventos explicitamente publicados;
* conteúdo institucional.

A classificação Pública não significa:

```text
Sem proteção
```

Informações públicas ainda deverão possuir proteção contra:

* alteração não autorizada;
* destruição;
* indisponibilidade;
* manipulação.

Portanto, informação poderá ser pública para leitura e restrita para alteração.

---

# 8. Informação Interna

Informação Interna é destinada ao funcionamento administrativo ou operacional da organização, mas não exige necessariamente o nível máximo de proteção.

Exemplos poderão incluir:

* determinadas configurações operacionais;
* informações administrativas não públicas;
* estruturas internas;
* dados auxiliares;
* informações de organização de módulos.

O acesso deverá permanecer restrito aos contextos legítimos da plataforma.

Informação Interna não deverá ser publicada automaticamente.

---

# 9. Informação Restrita

Informação Restrita possui acesso limitado a determinados usuários, papéis, grupos ou funções.

Exemplos poderão incluir:

* determinados cadastros administrativos;
* relatórios internos;
* informações de departamentos;
* determinadas informações de membros;
* configurações sensíveis;
* operações administrativas.

O acesso deverá considerar:

```text
Usuário
+
Permissão
+
Tenant
+
Contexto
```

A simples autenticação não deverá conceder acesso.

---

# 10. Informação Confidencial

Informação Confidencial representa o maior nível de sensibilidade previsto pela classificação geral do GSF.

O próprio framework estabelece tratamento confidencial para dados:

* pessoais;
* financeiros;
* ministeriais.

Também deverão receber proteção equivalente, conforme sua natureza:

* credenciais;
* tokens;
* segredos;
* determinadas informações de segurança;
* dados cuja exposição possa causar impacto significativo.

O acesso deverá ser estritamente limitado.

---

# 11. Critérios de Classificação

A classificação deverá considerar perguntas como:

```text
A informação é destinada ao público?

Contém dados pessoais?

Contém informações financeiras?

Contém informação ministerial?

Permite autenticação ou acesso?

Revela configuração sensível?

Sua exposição afeta uma pessoa?

Sua exposição afeta uma igreja?

Sua alteração indevida causa impacto?

Existe obrigação legal relacionada?

O dado pertence a um tenant específico?
```

Quando houver dúvida entre duas classificações, deverá ser adotada inicialmente a classificação mais protetiva até análise adequada.

---

# 12. Dados Pessoais

Dados relacionados a pessoas deverão ser protegidos conforme sua natureza e finalidade.

Podem incluir, conforme os cadastros existentes:

* nome;
* contato;
* endereço;
* informações cadastrais;
* vínculos;
* informações administrativas associadas à pessoa.

O GSF estabelece dados pessoais como informações confidenciais.

Isso não significa que todos os campos possuam necessariamente o mesmo impacto individual.

Entretanto, o conjunto deverá ser tratado com proteção compatível com sua natureza.

---

# 13. Dados Financeiros

Informações financeiras deverão ser classificadas como Confidenciais.

Isso inclui, conforme os módulos e funcionalidades aplicáveis:

* movimentações;
* lançamentos;
* valores;
* fundos;
* categorias financeiras;
* relatórios financeiros;
* consolidações;
* informações associadas a operações financeiras.

O acesso deverá ser limitado às funções legitimamente autorizadas.

Regra:

```text
Acesso ao sistema
      ≠
acesso ao Financeiro
```

E:

```text
Acesso ao Financeiro
      ≠
acesso irrestrito a toda operação financeira
```

---

# 14. Dados Ministeriais

Informações ministeriais deverão ser tratadas como Confidenciais conforme definido pelo GSF.

A classificação deverá considerar que determinados registros podem representar informações internas da vida administrativa e ministerial da igreja.

O acesso deverá respeitar:

* finalidade;
* função;
* permissão;
* tenant;
* necessidade.

---

# 15. Dados de Autenticação e Segurança

Informações relacionadas à autenticação ou à proteção da plataforma exigem tratamento especial.

Incluem:

* credenciais;
* tokens;
* sessões;
* códigos de recuperação;
* chaves;
* informações de autorização;
* determinadas informações de auditoria.

Esses dados não deverão ser expostos apenas porque pertencem ao usuário autenticado.

O tratamento deverá seguir o GAF e os documentos especializados do GSF.

---

# 16. Dados Organizacionais

Dados de uma igreja pertencem ao contexto organizacional correspondente.

A classificação da informação não substitui o isolamento multi-tenant.

Por exemplo:

```text
Informação Interna
da Igreja A
```

continua não sendo informação interna da Igreja B.

Portanto:

```text
Classificação
+
Tenant
=
Decisão de proteção
```

---

# 17. Configurações e Dados Técnicos

Configurações poderão possuir classificações diferentes.

Exemplos conceituais:

```text
Nome público da organização
→ Pública ou Interna

Configuração operacional
→ Interna ou Restrita

Configuração de segurança
→ Restrita ou Confidencial

Secret
→ Confidencial
```

A classificação deverá considerar o conteúdo e o impacto de exposição.

---

# 18. Credenciais e Segredos

Credenciais e segredos deverão ser tratados como Confidenciais.

Incluem:

* senhas;
* API keys;
* tokens;
* secrets;
* credenciais de banco;
* credenciais de serviços externos;
* chaves privadas quando existentes.

Esses dados deverão receber controles específicos.

Não deverão ser:

* enviados para logs;
* exibidos integralmente em interfaces;
* incluídos desnecessariamente em relatórios;
* armazenados diretamente no código-fonte;
* compartilhados por mecanismos inadequados.

---

# 19. Dados de Crianças e Adolescentes

Funcionalidades do GereIgreja que processem informações relacionadas a crianças e adolescentes deverão receber atenção reforçada.

Esse cenário poderá existir, por exemplo, em contextos educacionais ou ministeriais.

O tratamento deverá observar:

* necessidade;
* finalidade;
* minimização;
* autorização adequada;
* exposição mínima;
* legislação aplicável.

A presença desses dados deverá ser considerada durante análise de privacidade e conformidade.

---

# 20. Dados em Módulos do GereIgreja

A classificação deverá ser aplicada ao contexto real dos módulos.

Exemplo conceitual:

| Área           | Exemplos de informação            | Classificação predominante esperada |
| -------------- | --------------------------------- | ----------------------------------- |
| Portal Público | conteúdo publicado                | Pública                             |
| Secretaria     | cadastros de pessoas              | Confidencial                        |
| Financeiro     | movimentações e valores           | Confidencial                        |
| Escola Bíblica | dados administrativos e de alunos | Restrita/Confidencial               |
| Eventos        | dados operacionais                | Interna/Restrita                    |
| Comunicação    | contatos e destinatários          | Restrita/Confidencial               |
| Configurações  | parâmetros administrativos        | Interna/Restrita                    |
| Segurança      | credenciais e controles           | Confidencial                        |

Essa tabela representa orientação geral.

A classificação final deverá considerar o dado específico.

---

# 21. Princípio da Minimização

O GereIgreja deverá evitar coletar, armazenar, processar ou expor dados sem necessidade.

Pergunta obrigatória:

```text
Este dado é realmente necessário
para esta finalidade?
```

Se a resposta for negativa, sua coleta deverá ser evitada.

Minimização reduz:

* risco;
* exposição;
* complexidade;
* impacto de incidentes;
* obrigações de tratamento.

---

# 22. Necessidade de Acesso

A classificação deverá ser combinada com necessidade de acesso.

Não basta perguntar:

```text
O usuário possui permissão?
```

Também deverá ser considerado:

```text
Ele precisa desta informação
para executar sua função?
```

Esse princípio é especialmente relevante para informações Restritas e Confidenciais.

---

# 23. Coleta

Durante a coleta deverão ser considerados:

* finalidade;
* necessidade;
* classificação;
* validação;
* origem;
* autorização;
* tenant.

Campos não deverão ser adicionados apenas porque poderão ser úteis futuramente.

A finalidade deverá justificar sua existência.

---

# 24. Processamento

Durante o processamento, a informação deverá manter sua proteção.

Dados confidenciais não deixam de ser confidenciais porque estão temporariamente em memória ou sendo processados por uma task.

Processos deverão acessar apenas as informações necessárias.

---

# 25. Armazenamento

O armazenamento deverá considerar:

* classificação;
* acesso;
* tenant;
* necessidade;
* retenção;
* backup;
* integridade.

Dados não deverão ser duplicados sem necessidade.

Duplicações ampliam superfícies de exposição.

---

# 26. Consulta

Consultas deverão retornar apenas informações pertencentes ao escopo autorizado.

Especial atenção deverá ser dada a:

* selectors;
* managers;
* services;
* views;
* APIs;
* relatórios;
* buscas.

Regra fundamental:

```text
Encontrar o registro
      ≠
poder retornar o registro
```

---

# 27. Exibição

Interfaces deverão exibir somente as informações necessárias.

Isso inclui:

* páginas;
* cards;
* tabelas;
* modais;
* dashboards;
* formulários;
* tooltips;
* notificações.

Informação confidencial não deverá ser apresentada em componentes desnecessários apenas por conveniência técnica.

---

# 28. Transmissão

Informações deverão ser protegidas durante transmissão.

O GSF estabelece HTTPS como requisito.

Integrações deverão considerar adicionalmente:

* destino;
* autenticação;
* necessidade;
* minimização;
* classificação;
* logs;
* falhas.

---

# 29. Exportação

Exportações ampliam o risco porque retiram informações do controle direto da aplicação.

Antes de permitir exportação, avaliar:

```text
Quem pode exportar?

Quais dados?

De qual tenant?

Para qual finalidade?

O arquivo contém dados confidenciais?

A operação precisa ser auditada?
```

Exportação deverá possuir autorização própria quando o risco justificar.

---

# 30. Relatórios

Relatórios deverão respeitar as mesmas regras das consultas comuns.

A consolidação de dados poderá aumentar a sensibilidade da informação.

Por exemplo:

```text
Vários registros individualmente
          ↓
Relatório consolidado
          ↓
Maior impacto potencial
```

Portanto, relatórios não deverão assumir automaticamente a classificação dos campos isolados.

---

# 31. Logs e Auditoria

Logs deverão evitar exposição desnecessária de dados.

Informações confidenciais não deverão ser registradas integralmente sem necessidade operacional justificável.

Especial atenção deverá ser dada a:

* payloads;
* tokens;
* parâmetros;
* erros;
* dados pessoais;
* valores financeiros;
* credenciais.

Auditoria deverá registrar evidências suficientes sem reproduzir indiscriminadamente o conteúdo protegido.

---

# 32. Cache

Cache constitui armazenamento temporário e deverá ser tratado como tal.

Dados sensíveis em cache deverão considerar:

* escopo;
* chave;
* tenant;
* expiração;
* invalidação;
* exposição.

Uma chave de cache inadequada poderá causar vazamento entre tenants.

Portanto, o contexto organizacional deverá ser considerado quando aplicável.

---

# 33. Backups

A classificação permanece válida dentro dos backups.

Um dado Confidencial no banco continua Confidencial no backup.

Backups deverão possuir proteção compatível com:

* dados armazenados;
* retenção;
* acesso;
* restauração.

O tema será aprofundado no documento de continuidade.

---

# 34. Integrações

Antes de transmitir informações para serviço externo, deverá ser avaliado:

* quais dados serão enviados;
* por que serão enviados;
* classificação;
* tenant;
* destino;
* necessidade;
* credenciais;
* retenção quando conhecida;
* logging.

Não deverá ser enviado um objeto completo quando apenas alguns campos forem necessários.

---

# 35. APIs

APIs deverão limitar campos retornados.

Evitar:

```text
Serializar tudo
       ↓
esconder depois no frontend
```

Preferir:

```text
Selecionar somente
os campos autorizados
       ↓
retornar
```

A classificação deverá influenciar desenho de serializers, respostas e permissões.

---

# 36. Uploads e Arquivos

Arquivos enviados à plataforma deverão ser tratados conforme:

* origem;
* tipo;
* conteúdo;
* finalidade;
* proprietário;
* tenant;
* autorização.

O fato de um arquivo possuir URL não significa que deverá ser publicamente acessível.

A autorização de acesso deverá ser compatível com sua classificação.

---

# 37. Ambientes de Desenvolvimento e Teste

Ambientes não produtivos não deverão ser considerados automaticamente seguros para dados reais.

Deverá ser evitado o uso desnecessário de dados reais de produção em:

* desenvolvimento;
* testes;
* demonstrações;
* homologação.

Quando dados reais forem indispensáveis, controles apropriados deverão ser definidos.

Preferir dados sintéticos ou adequadamente tratados quando possível.

---

# 38. Exclusão e Retenção

Dados não deverão ser mantidos indefinidamente apenas porque existe capacidade técnica para armazená-los.

Políticas de retenção deverão considerar:

* finalidade;
* necessidade operacional;
* requisitos legais;
* auditoria;
* continuidade;
* histórico necessário.

A exclusão deverá considerar também cópias secundárias e ciclos de backup conforme política aplicável.

---

# 39. Mudança de Classificação

A classificação poderá mudar conforme o contexto.

Exemplo:

```text
Evento em elaboração
→ Interna

Evento publicado
→ parte das informações torna-se Pública
```

Outro exemplo:

```text
Informação pública
+
anotação administrativa
=
novo conteúdo possivelmente Restrito
```

Mudanças deverão ser deliberadas e não presumidas.

---

# 40. Isolamento Multi-Tenant

Classificação e isolamento são controles complementares.

Uma informação Pública poderá ser pública por decisão da própria organização.

Uma informação Interna, Restrita ou Confidencial deverá permanecer limitada ao tenant correspondente, salvo regra arquitetural explícita.

Nunca utilizar somente:

```text
pk=id
```

como critério suficiente de acesso quando o recurso estiver sujeito a tenant.

O acesso deverá considerar o escopo organizacional.

---

# 41. Controle de Acesso por Classificação

A classificação deverá influenciar a intensidade dos controles.

Modelo conceitual:

```text
Pública
   ↓
controle de integridade

Interna
   ↓
autenticação/contexto

Restrita
   ↓
autorização específica

Confidencial
   ↓
autorização estrita
+ minimização
+ auditoria quando aplicável
+ proteção reforçada
```

Essa representação não elimina controles adicionais necessários em cada caso.

---

# 42. Exposição Acidental

Possíveis canais de exposição incluem:

* resposta HTTP;
* template;
* API;
* log;
* traceback;
* export;
* cache;
* backup;
* integração;
* URL;
* mensagem de erro;
* notificação.

Revisões deverão considerar canais indiretos de exposição.

---

# 43. Incidentes envolvendo Informação

Exposição, alteração ou destruição indevida de informação poderá constituir incidente de segurança.

Exemplos:

```text
Usuário acessou dados
de outro tenant
```

```text
Informação confidencial
foi registrada em log público
```

```text
Exportação foi disponibilizada
a usuário sem autorização
```

```text
Credencial foi exposta
no repositório
```

O tratamento deverá seguir o processo oficial de gestão de incidentes.

---

# 44. Responsabilidades

## Engenharia

Deverá definir mecanismos técnicos compatíveis com a classificação.

## Desenvolvedores

Deverão identificar dados sensíveis durante implementação.

## Responsáveis Funcionais

Deverão auxiliar na identificação da finalidade e necessidade das informações.

## Operações

Deverá preservar a proteção em infraestrutura, backups e processos operacionais.

## Qualidade

Deverá testar cenários de exposição e autorização relevantes.

---

# 45. Matriz de Classificação

A seguinte matriz deverá orientar decisões iniciais:

| Informação                           | Pública | Interna | Restrita | Confidencial |
| ------------------------------------ | :-----: | :-----: | :------: | :----------: |
| Conteúdo institucional publicado     |    X    |         |          |              |
| Horários publicamente divulgados     |    X    |         |          |              |
| Configuração operacional comum       |         |    X    |          |              |
| Informação administrativa            |         |    X    |     X    |              |
| Relatórios internos                  |         |         |     X    |       X      |
| Cadastro de pessoas                  |         |         |          |       X      |
| Dados financeiros                    |         |         |          |       X      |
| Dados ministeriais                   |         |         |          |       X      |
| Credenciais                          |         |         |          |       X      |
| API keys e tokens                    |         |         |          |       X      |
| Configurações de segurança sensíveis |         |         |     X    |       X      |
| Logs técnicos                        |         |    X    |     X    |       X      |
| Backups                              |         |         |          |       X      |

A classificação de logs dependerá de seu conteúdo.

A classificação de backups deverá considerar o maior nível de sensibilidade dos dados armazenados.

---

# 46. Evidências Arquiteturais

## EA-GSF-DATA-001

O GSF define oficialmente quatro categorias de informação:

* Pública;
* Interna;
* Restrita;
* Confidencial.

## EA-GSF-DATA-002

O GSF determina tratamento confidencial para dados pessoais, financeiros e ministeriais.

## EA-GSF-DATA-003

O GereIgreja possui arquitetura multi-tenant documentada.

## EA-GSF-DATA-004

O backend possui documentação de Selectors e Managers, camadas relevantes para limitação de consultas.

## EA-GSF-DATA-005

O backend possui documentação de Services, responsável por regras de negócio.

## EA-GSF-DATA-006

O backend possui documentação específica de Permissions.

## EA-GSF-DATA-007

O projeto possui documentação específica relacionada ao módulo Financeiro.

## EA-GSF-DATA-008

O projeto possui documentação relacionada à Escola Dominical e a seus fluxos operacionais.

## EA-GSF-DATA-009

O projeto possui documentação operacional relacionada à Comunicação e automações.

## EA-GSF-DATA-010

O GSF estabelece proteção durante armazenamento, processamento, transmissão, backup e restauração.

---

# 47. Especificações Oficiais

## GSF-DATA-001

Toda informação deverá possuir tratamento compatível com sua sensibilidade.

## GSF-DATA-002

As classificações oficiais são Pública, Interna, Restrita e Confidencial.

## GSF-DATA-003

Dados pessoais deverão ser tratados como Confidenciais.

## GSF-DATA-004

Dados financeiros deverão ser tratados como Confidenciais.

## GSF-DATA-005

Dados ministeriais deverão ser tratados como Confidenciais.

## GSF-DATA-006

Credenciais e segredos deverão ser tratados como Confidenciais.

## GSF-DATA-007

A classificação não deverá substituir autorização.

## GSF-DATA-008

A classificação não deverá substituir isolamento multi-tenant.

## GSF-DATA-009

Informações deverão ser coletadas somente quando necessárias à finalidade.

## GSF-DATA-010

Respostas deverão expor somente os dados necessários.

## GSF-DATA-011

Exports deverão respeitar autorização, tenant e classificação.

## GSF-DATA-012

Relatórios deverão considerar o impacto da consolidação de dados.

## GSF-DATA-013

Logs não deverão registrar indiscriminadamente informações confidenciais.

## GSF-DATA-014

Backups deverão preservar o nível de proteção dos dados armazenados.

## GSF-DATA-015

Integrações deverão transmitir somente os dados necessários.

## GSF-DATA-016

APIs deverão limitar os campos retornados conforme necessidade e autorização.

## GSF-DATA-017

Arquivos deverão respeitar autorização compatível com sua classificação.

## GSF-DATA-018

Dados de produção não deverão ser copiados indiscriminadamente para ambientes não produtivos.

## GSF-DATA-019

Cache contendo dados de tenant deverá possuir escopo adequado.

## GSF-DATA-020

Quando houver dúvida relevante de classificação, deverá ser utilizado inicialmente o nível mais protetivo até revisão.

## GSF-DATA-021

Mudanças de classificação deverão ser deliberadas.

## GSF-DATA-022

Informações Públicas continuam sujeitas a controles de integridade.

## GSF-DATA-023

O acesso a informação Confidencial deverá seguir o princípio do mínimo acesso necessário.

## GSF-DATA-024

A retenção deverá ser compatível com finalidade e requisitos aplicáveis.

## GSF-DATA-025

Exposição indevida de informação deverá ser avaliada como possível incidente de segurança.

---

# 48. Anti-Padrões

São considerados anti-padrões:

```text
Está no banco
=
pode aparecer na tela
```

---

```text
Usuário autenticado
=
pode visualizar cadastro
```

---

```text
É da mesma aplicação
=
não precisa validar tenant
```

---

```text
Serializer do model inteiro
=
resposta padrão da API
```

---

```text
Enviar objeto completo
para integração
mesmo usando apenas dois campos
```

---

```text
Logar request.POST completo
para facilitar diagnóstico
```

---

```text
Copiar banco de produção
para notebook de desenvolvimento
```

---

```text
Arquivo possui URL
=
arquivo é público
```

---

```text
Backup está fora da aplicação
=
não contém dados confidenciais
```

---

```text
Dado não é senha
=
não é sensível
```

---

# 49. Checklist

## Identificação

* [ ] informações processadas identificadas;
* [ ] finalidade identificada;
* [ ] tenant identificado;
* [ ] classificação atribuída;
* [ ] dados pessoais identificados;
* [ ] dados financeiros identificados;
* [ ] dados ministeriais identificados;
* [ ] credenciais identificadas.

## Coleta

* [ ] dado realmente necessário;
* [ ] finalidade definida;
* [ ] campos desnecessários removidos;
* [ ] entrada validada.

## Acesso

* [ ] autenticação definida;
* [ ] autorização definida;
* [ ] tenant validado;
* [ ] menor privilégio aplicado;
* [ ] necessidade de acesso avaliada.

## Exibição

* [ ] somente campos necessários exibidos;
* [ ] informações confidenciais minimizadas;
* [ ] componentes auxiliares revisados;
* [ ] mensagens de erro revisadas.

## APIs

* [ ] campos retornados revisados;
* [ ] serializers revisados;
* [ ] autorização aplicada;
* [ ] tenant aplicado;
* [ ] payloads minimizados.

## Integrações

* [ ] destino conhecido;
* [ ] finalidade conhecida;
* [ ] dados enviados minimizados;
* [ ] credenciais protegidas;
* [ ] logging revisado.

## Logs

* [ ] ausência de senhas;
* [ ] ausência de tokens;
* [ ] ausência de secrets;
* [ ] dados pessoais minimizados;
* [ ] payloads revisados.

## Arquivos e Exports

* [ ] autorização de download;
* [ ] tenant validado;
* [ ] classificação considerada;
* [ ] exportação auditada quando aplicável.

## Infraestrutura

* [ ] backup protegido;
* [ ] cache isolado;
* [ ] ambiente não produtivo revisado;
* [ ] dados reais minimizados.

## Retenção

* [ ] necessidade de retenção definida;
* [ ] exclusão considerada;
* [ ] requisitos de auditoria considerados.

---

# 50. Documentos Relacionados

## Frameworks

* GSF — GereIgreja Security Framework
* GAF — GereIgreja Authentication Framework
* GQF — GereIgreja Quality Framework
* GDF — GereIgreja Documentation Framework

## Segurança

* GSF-01 — Fundamentos de Segurança
* GSF-03 — Gestão de Identidade
* GSF-04 — Autorização e Controle de Acesso
* GSF-05 — Segurança Multi-Tenant
* GSF-07 — Segurança das APIs
* GSF-08 — Segurança de Dados e Privacidade
* GSF-10 — Logging, Monitoramento e Auditoria
* GSF-11 — Backup, Continuidade e Recuperação
* GSF-14 — Conformidade e LGPD

## Arquitetura

* GEA-05 — Arquitetura do Banco de Dados
* GEA-07 — Arquitetura da Segurança
* GEA-08 — Arquitetura Multi-Tenant

## Backend

* Models
* Services
* Selectors
* Managers
* Permissions
* Logging
* Cache
* Exceptions

## Governança

* Padrões de Models
* Padrões de Permissões
* Padrões de Segurança
* Gestão da Documentação
* Auditoria 360 do GereIgreja

---

# 51. Princípios Finais

Toda informação processada pelo GereIgreja deverá possuir proteção compatível com seu contexto.

A classificação deverá responder:

```text
O que é esta informação?
        +
Quão sensível ela é?
        +
Quem precisa acessá-la?
        +
A qual organização pertence?
        +
Para qual finalidade será utilizada?
```

O GereIgreja não deverá proteger informações apenas no banco de dados.

A proteção deverá acompanhar todo o ciclo:

```text
Coletar
   ↓
Validar
   ↓
Processar
   ↓
Armazenar
   ↓
Consultar
   ↓
Exibir
   ↓
Transmitir
   ↓
Exportar
   ↓
Reter
   ↓
Excluir
```

Informação Pública deverá preservar integridade.

Informação Interna deverá permanecer dentro do contexto autorizado.

Informação Restrita deverá possuir acesso limitado.

Informação Confidencial deverá possuir proteção reforçada.

Dados pessoais, financeiros e ministeriais deverão ser tratados como Confidenciais conforme estabelecido pelo GSF.

Segredos deverão receber proteção própria.

Dados de uma igreja não deverão atravessar a fronteira de outra igreja por falha de consulta, autorização, cache, relatório, API, task ou integração.

A regra final é:

```text
Coletar menos
+
Expor menos
+
Autorizar explicitamente
+
Isolar corretamente
+
Registrar com responsabilidade
+
Reter somente o necessário
=
Redução de risco
```

---

# 52. Status do Documento

**Pasta**

`docs/seguranca/`

**Arquivo**

`02-Classificacao-e-Protecao-da-Informacao.md`

**Documento**

`GSF-02`

**Código**

`GSF-DATA-CLASSIFICATION`

**Framework**

`GSF — GereIgreja Security Framework`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Responsável**

`Equipe de Engenharia`

**Última atualização**

`Agosto de 2026`

**Próximo documento**

`03-Gestao-de-Identidade.md`

**Código do próximo documento**

`GSF-03`

```
```
