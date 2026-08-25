Pasta:

docs/seguranca/

Arquivo:

08-Seguranca-de-Dados-e-Privacidade.md

Documento:

GSF-08

Código:

GSF-DATA-PRIVACY

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

# GSF-08 — Segurança de Dados e Privacidade

> "Proteger dados no GereIgreja significa controlar todo o seu ciclo de vida: coleta, uso, armazenamento, acesso, compartilhamento, retenção, exclusão, backup e restauração."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Relação com Classificação da Informação
5. Princípios
6. Ciclo de Vida dos Dados
7. Confidencialidade
8. Integridade
9. Disponibilidade
10. Privacidade por Design
11. Minimização de Dados
12. Finalidade
13. Necessidade
14. Proporcionalidade
15. Dados Pessoais
16. Dados Financeiros
17. Dados Ministeriais
18. Dados Organizacionais
19. Dados de Autenticação
20. Dados Técnicos
21. Dados de Crianças e Adolescentes
22. Dados Sensíveis por Contexto
23. Coleta
24. Validação na Coleta
25. Consentimento e Base de Tratamento
26. Uso Interno
27. Processamento
28. Armazenamento
29. Banco de Dados
30. Criptografia em Trânsito
31. Criptografia em Repouso
32. Hashing
33. Senhas
34. Tokens
35. Secrets
36. Consultas
37. Selectors
38. Services
39. Managers
40. Multi-Tenant
41. Exibição em Tela
42. Mascaramento
43. Logs
44. Auditoria
45. Cache
46. Sessões
47. Arquivos
48. Uploads
49. Downloads
50. Exportações
51. Importações
52. Relatórios
53. Dashboards
54. APIs
55. Integrações
56. Comunicação
57. E-mails e Mensagens
58. Compartilhamento Externo
59. Ambientes Não Produtivos
60. Backups
61. Restauração
62. Retenção
63. Exclusão
64. Anonimização e Pseudonimização
65. Portabilidade e Exportação de Dados
66. Correção de Dados
67. Acesso por Usuário
68. Acesso Administrativo
69. Django Admin
70. Permissões
71. Revogação
72. Dados em Financeiro
73. Dados em Secretaria
74. Dados em Escola Bíblica
75. Dados em Eventos
76. Dados em Comunicação
77. Dados em Patrimônio
78. Dados em Relatórios
79. Incidentes de Dados
80. Vazamento
81. Alteração Indevida
82. Perda de Dados
83. Notificação e Escalonamento
84. Evidências
85. Testes
86. Testes de Privacidade
87. Testes Multi-Tenant
88. Testes de Exportação
89. Testes de Logs
90. Testes de Retenção
91. Evidências Arquiteturais
92. Especificações Oficiais
93. Anti-Padrões
94. Checklist
95. Documentos Relacionados
96. Princípios Finais
97. Status do Documento

---

# 1. Objetivo

Este documento estabelece os padrões oficiais de segurança de dados e privacidade do GereIgreja.

Seu objetivo é garantir que toda informação processada pela plataforma seja protegida durante seu ciclo de vida e utilizada somente de forma compatível com:

- sua finalidade;
- sua classificação;
- sua sensibilidade;
- o contexto organizacional;
- as permissões aplicáveis;
- os requisitos de segurança;
- os requisitos de privacidade;
- as obrigações de conformidade.

O GereIgreja deverá evitar tanto acesso indevido quanto coleta, exposição, retenção ou compartilhamento desnecessário de dados.

---

# 2. Escopo

Este documento aplica-se a dados presentes em:

- banco de dados;
- arquivos;
- uploads;
- relatórios;
- exports;
- imports;
- cache;
- logs;
- sessões;
- APIs;
- integrações;
- tarefas;
- automações;
- backups;
- ambientes de desenvolvimento;
- ambientes de homologação;
- produção.

Também se aplica a dados exibidos ou processados por:

- Área de Gestão;
- Django Admin;
- Portal Público;
- Secretaria;
- Financeiro;
- Escola Bíblica;
- Eventos;
- Comunicação;
- Patrimônio;
- Relatórios;
- Configurações.

---

# 3. Papel deste Documento

O GSF-08 detalha a proteção dos dados após sua classificação.

Sua relação é:

```text
GSF-02
Classificação da Informação
        ↓
GSF-08
Segurança de Dados e Privacidade
        ↓
Como proteger durante
todo o ciclo de vida
````

O GSF-02 responde:

```text
Quão sensível é este dado?
```

O GSF-08 responde:

```text
Como ele deverá ser protegido?
```

---

# 4. Relação com Classificação da Informação

Os níveis oficiais definidos pelo GSF-02 são:

```text
Pública
Interna
Restrita
Confidencial
```

A proteção aplicada deverá ser proporcional à classificação.

Entretanto, a classificação não deverá ser o único critério.

Também deverão ser considerados:

* tenant;
* finalidade;
* volume;
* contexto;
* associação entre dados;
* impacto de exposição.

Um conjunto de dados poderá possuir impacto maior que seus campos isolados.

---

# 5. Princípios

A segurança de dados deverá seguir:

* minimização;
* finalidade;
* necessidade;
* menor privilégio;
* proteção em profundidade;
* isolamento;
* confidencialidade;
* integridade;
* disponibilidade;
* rastreabilidade;
* retenção controlada;
* exclusão responsável.

---

# 6. Ciclo de Vida dos Dados

Todo dado deverá ser analisado ao longo de:

```text
Coleta
  ↓
Validação
  ↓
Processamento
  ↓
Armazenamento
  ↓
Consulta
  ↓
Exibição
  ↓
Compartilhamento
  ↓
Retenção
  ↓
Exclusão
```

Também deverão ser considerados caminhos secundários:

```text
Cache
Logs
Backup
Exportação
Integração
Ambiente de teste
```

A proteção não termina no banco principal.

---

# 7. Confidencialidade

Confidencialidade significa que o dado somente deverá estar disponível a sujeitos autorizados.

Deverão ser considerados:

* identidade;
* permissão;
* tenant;
* recurso;
* finalidade.

---

# 8. Integridade

Integridade significa impedir alteração incorreta ou não autorizada.

Deverão ser utilizados controles como:

* validação;
* autorização;
* regras de negócio;
* transações;
* constraints quando adequadas;
* auditoria.

---

# 9. Disponibilidade

Dados necessários à operação deverão permanecer disponíveis conforme os requisitos da plataforma.

A disponibilidade depende de:

* infraestrutura;
* backups;
* restauração;
* monitoramento;
* continuidade.

---

# 10. Privacidade por Design

A privacidade deverá ser considerada desde a concepção da funcionalidade.

Antes de criar um campo, relatório ou integração, perguntar:

```text
Precisamos deste dado?

Para qual finalidade?

Quem realmente precisa vê-lo?

Por quanto tempo?

Ele precisa sair do GereIgreja?
```

---

# 11. Minimização de Dados

O GereIgreja deverá coletar e processar somente o necessário.

Evitar:

```text
Talvez seja útil no futuro
→ vamos armazenar
```

Preferir:

```text
Existe finalidade clara?
        ↓
Sim → avaliar coleta
Não → não coletar
```

---

# 12. Finalidade

Toda coleta deverá possuir finalidade legítima e compreensível.

Dados não deverão ser reutilizados automaticamente para finalidade incompatível com aquela para a qual foram coletados.

---

# 13. Necessidade

A existência de capacidade técnica não justifica processamento.

Pergunta:

```text
O módulo precisa deste dado
para executar sua função?
```

---

# 14. Proporcionalidade

A intensidade do controle deverá ser proporcional ao impacto potencial.

Exemplo:

```text
Horário de culto publicado
```

possui tratamento diferente de:

```text
Movimentação financeira interna
```

---

# 15. Dados Pessoais

Dados pessoais deverão ser tratados como Confidenciais conforme o GSF.

Podem incluir, conforme a implementação:

* nome;
* telefone;
* e-mail;
* endereço;
* documentos;
* datas;
* vínculos;
* informações cadastrais.

A plataforma deverá evitar exposição excessiva.

---

# 16. Dados Financeiros

Dados financeiros são Confidenciais.

Incluem:

* valores;
* receitas;
* despesas;
* lançamentos;
* saldos;
* fundos;
* relatórios;
* estornos;
* movimentações.

Acesso deverá ser restrito às funções autorizadas.

---

# 17. Dados Ministeriais

Dados ministeriais deverão ser tratados como Confidenciais.

O acesso deverá respeitar:

* finalidade;
* função;
* tenant;
* permissões.

---

# 18. Dados Organizacionais

Dados administrativos de uma igreja deverão permanecer vinculados ao tenant correspondente.

O fato de um dado não ser pessoal não significa que possa atravessar tenants.

---

# 19. Dados de Autenticação

Dados relacionados a autenticação deverão possuir proteção reforçada.

Incluem:

* credenciais;
* hashes;
* tokens;
* sessões;
* códigos temporários.

O tratamento técnico específico deverá seguir o GAF.

---

# 20. Dados Técnicos

Informações técnicas também podem ser sensíveis.

Exemplos:

* configurações;
* IDs internos;
* endpoints;
* stack traces;
* logs;
* infraestrutura.

A exposição deverá ser limitada à necessidade.

---

# 21. Dados de Crianças e Adolescentes

Quando funcionalidades processarem dados de crianças ou adolescentes, deverão ser aplicados cuidados adicionais.

Isso é especialmente relevante em contextos como:

* Escola Bíblica;
* ministérios;
* eventos;
* cadastros relacionados.

O tratamento deverá respeitar necessidade, minimização e legislação aplicável.

---

# 22. Dados Sensíveis por Contexto

Um dado aparentemente comum poderá tornar-se sensível em determinado contexto.

Exemplo:

```text
Nome
+
informação ministerial
+
histórico
=
conjunto potencialmente confidencial
```

A análise deverá considerar o conjunto.

---

# 23. Coleta

Campos somente deverão existir quando necessários.

Durante a coleta deverá ser avaliado:

* finalidade;
* classificação;
* necessidade;
* validação;
* tenant;
* retenção.

---

# 24. Validação na Coleta

Dados incorretos também representam risco.

A validação deverá evitar:

* formatos inválidos;
* relacionamentos incorretos;
* tenant incorreto;
* valores incoerentes;
* manipulação.

---

# 25. Consentimento e Base de Tratamento

Quando consentimento ou outra base legal for necessária, sua definição deverá seguir a política de conformidade e LGPD da plataforma.

Este documento não inventa bases legais específicas para cada funcionalidade.

A definição deverá estar alinhada ao GSF-14 e à documentação jurídica aplicável.

---

# 26. Uso Interno

Dados internos deverão ser utilizados somente dentro das finalidades autorizadas.

Acesso técnico não deverá ser confundido com autorização funcional.

---

# 27. Processamento

Processos deverão acessar somente os dados necessários.

Tasks não deverão receber objetos completos quando apenas identificadores ou campos mínimos forem suficientes.

---

# 28. Armazenamento

O armazenamento deverá considerar:

* tipo do dado;
* classificação;
* necessidade;
* integridade;
* tenant;
* retenção;
* backup.

---

# 29. Banco de Dados

O banco de dados deverá preservar:

* integridade;
* relacionamentos;
* tenant;
* tipos adequados;
* constraints quando necessárias.

O banco não substitui autorização da aplicação.

---

# 30. Criptografia em Trânsito

O GSF estabelece HTTPS.

Dados transmitidos pela plataforma em produção deverão utilizar transporte seguro.

Isso inclui:

* aplicação;
* APIs;
* integrações;
* webhooks quando suportado.

---

# 31. Criptografia em Repouso

Informações críticas poderão utilizar criptografia adicional em repouso quando o risco justificar.

A decisão deverá considerar:

* tipo de dado;
* ameaça;
* infraestrutura;
* impacto operacional;
* gestão de chaves.

Não deverá ser adotada criptografia customizada improvisada.

---

# 32. Hashing

Dados que não precisam ser recuperados em texto original poderão utilizar mecanismos de hashing apropriados.

O exemplo principal são credenciais, cuja implementação deverá seguir o GAF e os mecanismos oficiais do Django.

---

# 33. Senhas

Senhas não deverão ser armazenadas em texto puro.

O GereIgreja deverá utilizar os mecanismos oficiais de armazenamento de credenciais do framework de autenticação.

---

# 34. Tokens

Tokens deverão ser tratados como dados Confidenciais.

Não deverão ser:

* exibidos indiscriminadamente;
* armazenados em logs;
* enviados em URLs quando evitável;
* compartilhados indevidamente.

---

# 35. Secrets

Segredos deverão possuir proteção própria e serão aprofundados no GSF-09.

---

# 36. Consultas

Consultas deverão limitar:

```text
Dados necessários
+
Tenant autorizado
+
Permissão
```

Não buscar dados globais apenas para filtrar posteriormente.

---

# 37. Selectors

Selectors deverão ser utilizados para consultas reutilizáveis e seguras conforme a arquitetura backend.

Eles deverão preservar:

* tenant;
* minimização;
* filtros de domínio.

---

# 38. Services

Services deverão evitar processamento excessivo de dados.

Também deverão preservar regras de integridade e segurança.

---

# 39. Managers

Managers poderão reforçar escopos estruturais quando isso fizer parte da arquitetura oficial.

---

# 40. Multi-Tenant

O isolamento definido no GSF-05 deverá ser aplicado a todo dado organizacional.

Regra:

```text
Dado da Igreja A
não deverá chegar à Igreja B
```

por nenhum dos seguintes canais:

* query;
* cache;
* API;
* export;
* task;
* relatório;
* arquivo;
* integração.

---

# 41. Exibição em Tela

Interfaces deverão exibir somente o necessário.

Evitar tabelas com excesso de dados pessoais.

Exemplo:

```text
Listagem de membros
```

não precisa necessariamente mostrar:

* endereço completo;
* documento;
* informações administrativas;
* histórico.

---

# 42. Mascaramento

Quando for útil reduzir exposição visual, poderá ser utilizado mascaramento.

Exemplos conceituais:

```text
***.***.***-**
```

ou:

```text
********1234
```

Mascaramento não substitui autorização.

---

# 43. Logs

Logs deverão seguir minimização.

Não registrar indiscriminadamente:

* senha;
* token;
* secret;
* documento;
* payload completo;
* dados financeiros completos.

---

# 44. Auditoria

Auditoria deverá registrar evidências suficientes para rastreabilidade sem reproduzir desnecessariamente o dado protegido.

---

# 45. Cache

Cache deverá preservar:

* tenant;
* usuário quando necessário;
* classificação;
* expiração;
* invalidação.

Dados Confidenciais não deverão ser cacheados sem análise adequada.

---

# 46. Sessões

Sessões deverão armazenar somente informações necessárias ao funcionamento.

Evitar persistir grandes objetos ou dados confidenciais sem necessidade.

---

# 47. Arquivos

Arquivos deverão possuir classificação e controle equivalentes aos dados que contêm.

---

# 48. Uploads

Uploads deverão considerar:

* proprietário;
* tenant;
* tipo;
* tamanho;
* finalidade;
* autorização.

---

# 49. Downloads

Arquivos privados deverão exigir autorização.

Conhecer a URL não deverá ser suficiente.

---

# 50. Exportações

Exportações representam aumento de exposição.

Antes de exportar, avaliar:

```text
Quem?
Qual tenant?
Quais registros?
Quais campos?
Qual finalidade?
Precisa auditar?
```

---

# 51. Importações

Importações deverão evitar associação indevida de dados.

O tenant deverá ser derivado ou validado pelo servidor.

---

# 52. Relatórios

Relatórios podem concentrar grandes volumes de informação.

Sua autorização deverá ser proporcional ao impacto.

---

# 53. Dashboards

Dashboards deverão seguir minimização.

KPIs poderão revelar informação mesmo sem listar registros.

Exemplo:

```text
saldo financeiro
```

é informação confidencial mesmo sendo apenas um número.

---

# 54. APIs

APIs deverão seguir o GSF-07.

Respostas deverão limitar campos e tenant.

---

# 55. Integrações

Integrações externas deverão receber somente o necessário.

Evitar enviar objetos completos quando poucos campos forem suficientes.

---

# 56. Comunicação

O módulo de Comunicação poderá processar:

* telefones;
* e-mails;
* destinatários;
* conteúdo;
* históricos.

Esses dados deverão ser protegidos durante envio, armazenamento e integração.

---

# 57. E-mails e Mensagens

Mensagens não deverão incluir informações confidenciais sem finalidade legítima.

Também deverá ser avaliado o risco de envio ao destinatário incorreto.

---

# 58. Compartilhamento Externo

Antes de compartilhar dados com terceiros, deverá existir análise de:

* finalidade;
* necessidade;
* classificação;
* quantidade;
* destino;
* proteção;
* conformidade.

---

# 59. Ambientes Não Produtivos

Dados reais de produção não deverão ser copiados indiscriminadamente para:

* desenvolvimento;
* testes;
* homologação;
* demonstrações.

Preferir:

* dados sintéticos;
* dados anonimizados;
* subconjuntos controlados.

---

# 60. Backups

Backups herdam a classificação dos dados armazenados.

Se contêm dados Confidenciais, o backup deverá ser protegido como Confidencial.

---

# 61. Restauração

Restauração deverá preservar:

* integridade;
* tenant;
* controles de acesso;
* consistência.

Testes de restauração não deverão criar cópias inseguras de dados.

---

# 62. Retenção

Dados deverão ser mantidos somente pelo período necessário segundo:

* finalidade;
* operação;
* auditoria;
* requisitos legais;
* política aplicável.

Retenção indefinida deverá ser evitada sem justificativa.

---

# 63. Exclusão

Exclusão deverá distinguir:

```text
Remover acesso
```

de:

```text
Remover registro
```

e:

```text
Remover histórico
```

Esses conceitos possuem impactos diferentes.

---

# 64. Anonimização e Pseudonimização

Quando apropriado, dados poderão ser anonimizados ou pseudonimizados para reduzir exposição.

Esses mecanismos deverão ser utilizados com critério e não apenas como alteração visual.

---

# 65. Portabilidade e Exportação de Dados

Solicitações relacionadas à disponibilização de dados deverão seguir a política de conformidade e as permissões apropriadas.

A plataforma deverá evitar exportar informações de terceiros fora do escopo legítimo.

---

# 66. Correção de Dados

Dados incorretos deverão poder ser corrigidos conforme as regras funcionais e legais aplicáveis.

Alterações relevantes poderão exigir auditoria.

---

# 67. Acesso por Usuário

Usuários deverão acessar apenas dados necessários à sua função.

Acesso a módulo não significa acesso integral a todos os dados desse módulo.

---

# 68. Acesso Administrativo

Usuários administrativos poderão possuir maior acesso, mas o princípio do menor privilégio continua aplicável.

---

# 69. Django Admin

O Django Admin deverá exibir somente informações necessárias aos usuários técnicos autorizados.

Customizações deverão evitar exposição indiscriminada de campos Confidenciais.

---

# 70. Permissões

Permissões deverão seguir o GSF-04.

O controle de dados deverá considerar:

```text
Identidade
+
Permissão
+
Tenant
+
Recurso
```

---

# 71. Revogação

Quando acesso for revogado, o usuário não deverá continuar recebendo dados por:

* sessão antiga;
* cache;
* link anterior;
* API;
* export temporário.

---

# 72. Dados em Financeiro

O Financeiro possui alta sensibilidade.

Deverão ser protegidos:

* lançamentos;
* receitas;
* despesas;
* saldos;
* estornos;
* categorias;
* fundos;
* relatórios;
* dashboards.

Especial atenção a:

* precisão;
* autorização;
* tenant;
* auditoria;
* exportação.

---

# 73. Dados em Secretaria

A Secretaria processa volume relevante de dados pessoais.

Listagens e formulários deverão seguir minimização.

Exports deverão possuir controles adicionais quando necessário.

---

# 74. Dados em Escola Bíblica

Podem existir dados de:

* alunos;
* professores;
* turmas;
* frequência;
* crianças e adolescentes.

A exposição deverá ser restrita à necessidade operacional.

---

# 75. Dados em Eventos

Eventos poderão misturar conteúdo público com informações administrativas.

Essas duas categorias deverão ser separadas.

---

# 76. Dados em Comunicação

Devem ser protegidos:

* contatos;
* listas;
* destinatários;
* históricos;
* agendamentos;
* informações de entrega.

---

# 77. Dados em Patrimônio

Dados patrimoniais deverão permanecer associados à organização correta e acessíveis apenas às funções autorizadas.

---

# 78. Dados em Relatórios

Relatórios deverão aplicar:

* tenant;
* permissão;
* minimização;
* classificação.

O simples fato de um relatório ser gerado pelo sistema não torna seu conteúdo seguro para qualquer usuário.

---

# 79. Incidentes de Dados

Qualquer evento que afete:

* confidencialidade;
* integridade;
* disponibilidade;

deverá ser avaliado como possível incidente.

---

# 80. Vazamento

Exemplos:

```text
Dados da Igreja A
expostos à Igreja B
```

```text
Export confidencial
acessível sem autorização
```

```text
Dados pessoais
registrados em log inadequado
```

---

# 81. Alteração Indevida

Alterações não autorizadas também constituem incidente de integridade.

Exemplos:

* valor financeiro alterado;
* cadastro modificado;
* permissão adulterada;
* tenant trocado.

---

# 82. Perda de Dados

Perda acidental ou indisponibilidade prolongada deverá ser tratada conforme o processo de incidentes e continuidade.

---

# 83. Notificação e Escalonamento

O processo formal será definido no GSF-13 e GSF-14.

A classificação do incidente deverá considerar:

* dados afetados;
* volume;
* sensibilidade;
* tenants;
* impacto.

---

# 84. Evidências

Eventos relevantes deverão preservar evidências suficientes para investigação.

Não destruir logs ou registros necessários durante tentativa de correção.

---

# 85. Testes

A proteção de dados deverá ser testada.

---

# 86. Testes de Privacidade

Verificar:

* campos excessivos;
* telas;
* APIs;
* logs;
* exports;
* relatórios;
* mensagens.

---

# 87. Testes Multi-Tenant

Padrão:

```text
Usuário A
não recebe
dados da Igreja B
```

Testar em:

* listagem;
* detalhe;
* dashboard;
* relatório;
* API;
* export;
* cache.

---

# 88. Testes de Exportação

Validar:

* usuário;
* permissão;
* tenant;
* campos;
* volume;
* arquivo final.

---

# 89. Testes de Logs

Verificar ausência de:

* senhas;
* tokens;
* secrets;
* payloads confidenciais completos.

---

# 90. Testes de Retenção

Quando existirem regras automatizadas de retenção ou exclusão, deverão possuir testes próprios.

---

# 91. Evidências Arquiteturais

## EA-GSF-DP-001

O GSF estabelece proteção de dados durante armazenamento, processamento, transmissão, backup e restauração.

## EA-GSF-DP-002

O GSF classifica dados pessoais, financeiros e ministeriais como Confidenciais.

## EA-GSF-DP-003

O GereIgreja possui arquitetura de banco de dados documentada.

## EA-GSF-DP-004

O GereIgreja possui arquitetura multi-tenant documentada.

## EA-GSF-DP-005

O backend possui documentação de Models, Services, Selectors e Managers.

## EA-GSF-DP-006

O backend possui documentação de Cache, Logging e Tasks.

## EA-GSF-DP-007

O projeto possui documentação de LGPD em `docs/deploy/LGPD_IMPLEMENTACAO.md`.

## EA-GSF-DP-008

O projeto possui módulos que processam dados pessoais, financeiros, ministeriais e operacionais.

## EA-GSF-DP-009

O GSF exige HTTPS.

## EA-GSF-DP-010

O GSF estabelece backups e testes de restauração como parte da proteção.

---

# 92. Especificações Oficiais

## GSF-DP-001

Dados deverão ser protegidos durante todo o ciclo de vida.

## GSF-DP-002

A coleta deverá respeitar minimização e finalidade.

## GSF-DP-003

Dados pessoais deverão ser tratados como Confidenciais.

## GSF-DP-004

Dados financeiros deverão ser tratados como Confidenciais.

## GSF-DP-005

Dados ministeriais deverão ser tratados como Confidenciais.

## GSF-DP-006

Dados de autenticação deverão possuir proteção reforçada.

## GSF-DP-007

HTTPS deverá proteger dados em trânsito em produção.

## GSF-DP-008

Criptografia adicional em repouso deverá ser avaliada conforme risco.

## GSF-DP-009

Senhas não deverão ser armazenadas em texto puro.

## GSF-DP-010

Tokens e secrets não deverão ser expostos em logs.

## GSF-DP-011

Consultas deverão retornar somente dados necessários e autorizados.

## GSF-DP-012

O isolamento multi-tenant deverá ser preservado em todas as formas de armazenamento e processamento.

## GSF-DP-013

Interfaces deverão minimizar dados exibidos.

## GSF-DP-014

Cache deverá preservar isolamento e classificação.

## GSF-DP-015

Sessões deverão armazenar somente dados necessários.

## GSF-DP-016

Arquivos privados deverão possuir autorização.

## GSF-DP-017

Exportações deverão respeitar tenant e permissão.

## GSF-DP-018

Dados enviados a integrações deverão ser minimizados.

## GSF-DP-019

Dados reais de produção não deverão ser copiados indiscriminadamente para ambientes não produtivos.

## GSF-DP-020

Backups deverão ser protegidos de acordo com os dados que contêm.

## GSF-DP-021

Retenção indefinida deverá possuir justificativa.

## GSF-DP-022

Exclusão deverá considerar requisitos de auditoria e conformidade.

## GSF-DP-023

Dashboards deverão tratar KPIs confidenciais como dados protegidos.

## GSF-DP-024

Incidentes que afetem confidencialidade, integridade ou disponibilidade deverão seguir o processo oficial.

## GSF-DP-025

Testes de privacidade e exposição deverão fazer parte das funcionalidades que processam dados sensíveis.

---

# 93. Anti-Padrões

São considerados anti-padrões:

```text
Temos o dado
=
vamos mostrar
```

---

```text
Talvez seja útil no futuro
=
vamos coletar
```

---

```text
Usuário acessa o módulo
=
pode visualizar todos os campos
```

---

```text
Dados reais de produção
copiados integralmente
para ambiente de desenvolvimento
```

---

```text
Logar request completo
para facilitar debug
```

---

```text
Exportar todos os campos
porque é mais simples
```

---

```text
Backup fora do banco
=
não precisa proteção
```

---

```text
Arquivo possui link
=
arquivo é público
```

---

```text
Dashboard mostra apenas totais
=
não contém dados sensíveis
```

---

```text
Token temporário
=
pode aparecer em log
```

---

```text
Criptografia própria
implementada sem necessidade
```

---

# 94. Checklist

## Classificação

* [ ] dado identificado;
* [ ] classificação definida;
* [ ] tenant identificado;
* [ ] finalidade definida.

## Coleta

* [ ] campo necessário;
* [ ] minimização;
* [ ] validação;
* [ ] retenção considerada.

## Banco de Dados

* [ ] tipo correto;
* [ ] relacionamento correto;
* [ ] tenant;
* [ ] integridade;
* [ ] constraint avaliada.

## Exibição

* [ ] campos mínimos;
* [ ] permissão;
* [ ] tenant;
* [ ] mascaramento avaliado;
* [ ] dados confidenciais minimizados.

## APIs

* [ ] campos mínimos;
* [ ] tenant;
* [ ] autorização;
* [ ] tokens protegidos.

## Logs

* [ ] sem senha;
* [ ] sem token;
* [ ] sem secret;
* [ ] sem payload completo desnecessário;
* [ ] dados pessoais minimizados.

## Cache

* [ ] tenant;
* [ ] usuário quando necessário;
* [ ] expiração;
* [ ] invalidação;
* [ ] classificação avaliada.

## Arquivos

* [ ] autorização;
* [ ] tenant;
* [ ] classificação;
* [ ] download protegido.

## Exportação

* [ ] usuário autorizado;
* [ ] tenant correto;
* [ ] campos mínimos;
* [ ] auditoria avaliada;
* [ ] arquivo protegido.

## Integrações

* [ ] finalidade;
* [ ] dados mínimos;
* [ ] destino;
* [ ] credenciais;
* [ ] logging;
* [ ] tenant.

## Ambiente

* [ ] produção separada;
* [ ] dados reais minimizados em não produção;
* [ ] secrets separados;
* [ ] backups protegidos.

## Retenção

* [ ] prazo avaliado;
* [ ] finalidade;
* [ ] auditoria;
* [ ] exclusão;
* [ ] backups considerados.

## Testes

* [ ] privacidade;
* [ ] outro tenant;
* [ ] exportação;
* [ ] API;
* [ ] logs;
* [ ] cache;
* [ ] relatório;
* [ ] dashboard.

---

# 95. Documentos Relacionados

## Frameworks

* GSF — GereIgreja Security Framework
* GAF — GereIgreja Authentication Framework
* GQF — GereIgreja Quality Framework
* GDF — GereIgreja Documentation Framework
* GOC — GereIgreja Operations Center

## Segurança

* GSF-01 — Fundamentos de Segurança
* GSF-02 — Classificação e Proteção da Informação
* GSF-03 — Gestão de Identidade
* GSF-04 — Autorização e Controle de Acesso
* GSF-05 — Segurança Multi-Tenant
* GSF-06 — Segurança da Aplicação
* GSF-07 — Segurança das APIs
* GSF-09 — Segurança de Infraestrutura e Segredos
* GSF-10 — Logging, Monitoramento e Auditoria
* GSF-11 — Backup, Continuidade e Recuperação
* GSF-13 — Gestão de Incidentes de Segurança
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
* Tasks
* Cache
* Logging

## Outros

* `docs/deploy/LGPD_IMPLEMENTACAO.md`
* documentação de Financeiro
* documentação de Secretaria
* documentação da Escola Bíblica
* documentação de Comunicação

---

# 96. Princípios Finais

A proteção de dados do GereIgreja deverá ser pensada de ponta a ponta.

Não basta proteger o banco.

O mesmo dado poderá aparecer em:

```text
Banco
↓
Query
↓
View
↓
Template
↓
API
↓
Cache
↓
Log
↓
Export
↓
Backup
↓
Integração
```

Cada uma dessas etapas representa uma superfície de exposição.

A regra deverá ser:

```text
Coletar somente o necessário.

Processar somente o necessário.

Exibir somente o necessário.

Compartilhar somente o necessário.

Reter somente o necessário.
```

Dados pessoais, financeiros e ministeriais deverão permanecer Confidenciais.

Dados de uma igreja deverão permanecer isolados de outra.

Secrets e credenciais deverão possuir proteção reforçada.

Dados reais de produção deverão ser mantidos fora de ambientes não produtivos sempre que possível.

Exports e relatórios deverão ser tratados como dados, e não apenas como arquivos.

Backups deverão possuir a mesma responsabilidade de proteção do banco de origem.

A privacidade deverá fazer parte do desenho da funcionalidade desde o início.

O princípio final é:

```text
Quanto menos dados
a plataforma precisar expor,
menor será a superfície
que precisará defender.
```

---

# 97. Status do Documento

**Pasta**

`docs/seguranca/`

**Arquivo**

`08-Seguranca-de-Dados-e-Privacidade.md`

**Documento**

`GSF-08`

**Código**

`GSF-DATA-PRIVACY`

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

`09-Seguranca-de-Infraestrutura-e-Segredos.md`

**Código do próximo documento**

`GSF-09`

```
```
