Pasta:

docs/seguranca/

Arquivo:

09-Seguranca-de-Infraestrutura-e-Segredos.md

Documento:

GSF-09

Código:

GSF-INFRA-SECRETS

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

# GSF-09 — Segurança de Infraestrutura e Segredos

> "A segurança do GereIgreja não termina no código. Infraestrutura, ambientes, credenciais, serviços externos, variáveis de ambiente e segredos também fazem parte da superfície de proteção da plataforma."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Relação com os Demais Documentos
5. Princípios
6. Infraestrutura como Camada de Segurança
7. Ambientes
8. Produção
9. Homologação
10. Desenvolvimento
11. Separação entre Ambientes
12. Configurações por Ambiente
13. Segredos
14. Classificação de Segredos
15. `SECRET_KEY`
16. Credenciais de Banco
17. API Keys
18. Tokens de Integração
19. Credenciais de Serviços Externos
20. Senhas Administrativas
21. Variáveis de Ambiente
22. Arquivos `.env`
23. Repositório de Código
24. Git e Histórico
25. Exposição Acidental de Segredos
26. Rotação de Segredos
27. Revogação de Segredos
28. Expiração
29. Princípio do Menor Privilégio
30. Segregação de Credenciais
31. Credenciais por Serviço
32. Credenciais por Ambiente
33. Credenciais Pessoais
34. Contas Técnicas
35. Infraestrutura de Deploy
36. Render e Ambiente de Produção
37. HTTPS
38. TLS
39. Domínios
40. Headers e Proxy
41. Firewall
42. Acesso Administrativo
43. Django Admin
44. Banco de Dados
45. Acesso ao Banco
46. Backups
47. Armazenamento de Backups
48. Serviços Externos
49. Integrações
50. WhatsApp e Comunicação
51. E-mail
52. Webhooks
53. Cron Jobs
54. Tasks
55. Automação
56. Logs de Infraestrutura
57. Monitoramento
58. Alertas
59. Disponibilidade
60. Atualizações
61. Sistema Operacional e Plataforma
62. Dependências de Infraestrutura
63. Pacotes e Imagens
64. Vulnerabilidades
65. Configuração Segura do Django
66. `DEBUG`
67. `ALLOWED_HOSTS`
68. Cookies
69. CSRF
70. Sessões
71. CORS
72. Arquivos Estáticos
73. Arquivos de Mídia
74. Uploads
75. Proteção de Dados em Infraestrutura
76. Multi-Tenant
77. Cache
78. Serviços de Cache
79. Banco em Não Produção
80. Dados de Produção em Desenvolvimento
81. Acessos Emergenciais
82. Break Glass
83. Auditoria de Acessos
84. Incidentes de Infraestrutura
85. Vazamento de Segredos
86. Comprometimento de Credenciais
87. Indisponibilidade
88. Recuperação
89. Evidências
90. Testes e Verificações
91. Revisão de Configuração
92. Revisão de Secrets
93. Revisão de Dependências
94. Revisão de Deploy
95. Evidências Arquiteturais
96. Especificações Oficiais
97. Anti-Padrões
98. Checklist
99. Documentos Relacionados
100. Princípios Finais
101. Status do Documento

---

# 1. Objetivo

Este documento estabelece os padrões oficiais de segurança de infraestrutura e gestão de segredos do GereIgreja.

Seu objetivo é garantir que os ambientes, credenciais, serviços, configurações e componentes operacionais da plataforma sejam protegidos de forma compatível com:

- criticidade;
- sensibilidade;
- finalidade;
- ambiente;
- menor privilégio;
- rastreabilidade;
- continuidade.

A segurança da aplicação dependerá diretamente da segurança da infraestrutura que a executa.

---

# 2. Escopo

Este documento aplica-se a:

- ambiente de produção;
- homologação;
- desenvolvimento;
- serviços de deploy;
- banco de dados;
- serviços externos;
- credenciais;
- secrets;
- variáveis de ambiente;
- domínios;
- HTTPS;
- backups;
- cron jobs;
- tasks;
- automações;
- integrações;
- monitoramento;
- logs de infraestrutura.

Também se aplica aos processos técnicos utilizados para implantar, operar e manter o GereIgreja.

---

# 3. Papel deste Documento

O GSF-09 complementa:

```text
GSF-06
Segurança da Aplicação
        ↓
GSF-08
Segurança de Dados
        ↓
GSF-09
Infraestrutura e Segredos
````

O GSF-06 protege o software.

O GSF-08 protege os dados.

O GSF-09 protege o ambiente em que software e dados operam.

---

# 4. Relação com os Demais Documentos

Este documento deverá ser utilizado em conjunto com:

```text
GSF-01
→ fundamentos

GSF-05
→ isolamento multi-tenant

GSF-08
→ proteção dos dados

GSF-10
→ monitoramento e auditoria

GSF-11
→ backup e continuidade

GSF-12
→ vulnerabilidades

GSF-13
→ incidentes
```

---

# 5. Princípios

A segurança de infraestrutura deverá seguir:

* menor privilégio;
* segregação de ambientes;
* segredo fora do código;
* credenciais individualizadas;
* proteção em profundidade;
* rotação;
* revogação;
* rastreabilidade;
* configuração segura por padrão;
* atualização contínua.

---

# 6. Infraestrutura como Camada de Segurança

A arquitetura conceitual permanece:

```text
Internet
    ↓
HTTPS
    ↓
Infraestrutura
    ↓
Aplicação Django
    ↓
Autenticação
    ↓
Autorização
    ↓
Tenant
    ↓
Banco
    ↓
Backup
```

Comprometer uma camada de infraestrutura poderá reduzir ou eliminar controles da aplicação.

Por isso, a infraestrutura deverá ser tratada como parte da arquitetura de segurança.

---

# 7. Ambientes

O GereIgreja deverá manter distinção clara entre ambientes.

Exemplo:

```text
Desenvolvimento
      ↓
Homologação
      ↓
Produção
```

Cada ambiente deverá possuir configurações e credenciais próprias.

---

# 8. Produção

Produção deverá utilizar configuração restritiva.

Deverão ser priorizados:

* HTTPS;
* `DEBUG=False`;
* credenciais exclusivas;
* banco próprio;
* secrets próprios;
* monitoramento;
* backups;
* restrição de acessos administrativos.

---

# 9. Homologação

Homologação não deverá utilizar indiscriminadamente os mesmos segredos de produção.

Dados reais deverão ser evitados quando não forem necessários.

---

# 10. Desenvolvimento

Desenvolvimento deverá utilizar credenciais próprias.

O ambiente local não deverá depender de segredos de produção para funcionar normalmente.

---

# 11. Separação entre Ambientes

A separação deverá impedir que:

```text
Desenvolvimento
        ↓
altere produção
```

ou:

```text
Homologação
        ↓
consuma credencial crítica de produção
```

sem decisão explícita e controlada.

---

# 12. Configurações por Ambiente

Configurações poderão variar conforme:

* DEBUG;
* banco;
* hosts;
* cookies;
* endpoints;
* serviços;
* logging;
* integrações;
* secrets.

As diferenças deverão ser intencionais e documentadas.

---

# 13. Segredos

Segredo é qualquer informação cuja exposição permita acesso ou amplie risco.

Exemplos:

```text
SECRET_KEY
senha de banco
API key
token
credencial SMTP
credencial de integração
chave privada
```

Segredos deverão ser tratados como Confidenciais.

---

# 14. Classificação de Segredos

Todo segredo deverá ser considerado:

```text
CONFIDENCIAL
```

independentemente de sua finalidade.

Não deverá existir secret "pouco importante" apenas porque pertence a ambiente interno.

---

# 15. `SECRET_KEY`

A `SECRET_KEY` do Django deverá:

* ser exclusiva por ambiente;
* permanecer fora do repositório;
* possuir valor forte;
* ser rotacionada em caso de exposição.

Ela não deverá ser reutilizada entre ambientes sem justificativa.

---

# 16. Credenciais de Banco

Credenciais de banco deverão:

* possuir acesso mínimo;
* pertencer ao ambiente correto;
* permanecer fora do código;
* ser revogáveis;
* ser protegidas em logs.

A aplicação não deverá utilizar credencial administrativa global se uma credencial de aplicação mais restrita for suficiente.

---

# 17. API Keys

API Keys deverão ser protegidas como segredos.

Nunca deverão ser:

* expostas no frontend;
* commitadas;
* colocadas em documentação pública;
* registradas integralmente em logs.

---

# 18. Tokens de Integração

Tokens deverão possuir, quando disponível:

* escopo mínimo;
* validade;
* revogação;
* rotação;
* responsável.

---

# 19. Credenciais de Serviços Externos

Serviços externos poderão incluir:

* comunicação;
* e-mail;
* APIs;
* storage;
* monitoramento;
* automação.

Cada serviço deverá possuir credenciais específicas.

---

# 20. Senhas Administrativas

Senhas administrativas não deverão ser compartilhadas informalmente.

Contas humanas deverão ser individualizadas.

---

# 21. Variáveis de Ambiente

Variáveis de ambiente poderão ser utilizadas para configuração sensível.

Exemplos conceituais:

```text
DJANGO_SECRET_KEY
DATABASE_URL
API_TOKEN
SMTP_PASSWORD
```

O nome real deverá seguir a implementação atual.

---

# 22. Arquivos `.env`

Arquivos `.env` locais poderão armazenar configurações de desenvolvimento.

Eles não deverão ser versionados quando contiverem segredos.

Um arquivo de exemplo poderá existir sem valores reais.

Exemplo:

```text
.env.example
```

---

# 23. Repositório de Código

O repositório não deverá conter:

* secrets;
* tokens;
* senhas;
* credenciais;
* arquivos privados;
* dumps de banco contendo dados reais.

---

# 24. Git e Histórico

Remover um segredo do arquivo atual não o remove automaticamente do histórico Git.

Se um segredo for commitado, deverá ser considerado comprometido e rotacionado.

---

# 25. Exposição Acidental de Segredos

Se um segredo for exposto em:

* commit;
* log;
* screenshot;
* relatório;
* issue;
* chat;
* arquivo público;

deverá ser tratado como possível comprometimento.

Fluxo:

```text
Detectar
   ↓
Revogar
   ↓
Rotacionar
   ↓
Investigar
   ↓
Corrigir origem
```

---

# 26. Rotação de Segredos

Segredos deverão ser rotacionados:

* periodicamente quando necessário;
* após exposição;
* após comprometimento;
* após mudança de fornecedor;
* após desligamento técnico relevante.

---

# 27. Revogação de Segredos

Todo segredo utilizado por integração ou serviço deverá possuir mecanismo de revogação quando tecnicamente disponível.

---

# 28. Expiração

Tokens temporários deverão possuir expiração quando o mecanismo suportar essa propriedade.

---

# 29. Princípio do Menor Privilégio

Credenciais técnicas deverão possuir somente o acesso necessário.

Exemplo inadequado:

```text
Integração precisa enviar mensagens
        ↓
token recebe acesso administrativo completo
```

---

# 30. Segregação de Credenciais

Credenciais deverão ser separadas por finalidade.

Preferir:

```text
credencial banco
credencial e-mail
credencial WhatsApp
credencial API
```

em vez de uma credencial universal.

---

# 31. Credenciais por Serviço

Cada serviço deverá possuir credencial independente quando possível.

Isso limita impacto de comprometimento.

---

# 32. Credenciais por Ambiente

Produção, homologação e desenvolvimento deverão utilizar credenciais distintas.

---

# 33. Credenciais Pessoais

Credenciais pessoais de desenvolvedores não deverão ser utilizadas como dependência permanente de produção.

---

# 34. Contas Técnicas

Contas técnicas deverão seguir o GSF-03.

Deverão possuir:

* finalidade;
* responsável;
* acesso mínimo;
* revogação;
* rastreabilidade.

---

# 35. Infraestrutura de Deploy

O processo de deploy deverá preservar:

* secrets;
* configuração;
* dependências;
* banco;
* migrations;
* rollback quando aplicável.

Deploy não deverá imprimir segredos nos logs.

---

# 36. Render e Ambiente de Produção

A documentação existente do GereIgreja indica uso de infraestrutura de deploy baseada em Render em fluxos específicos.

Configurações de produção nesse ambiente deverão seguir:

* variáveis de ambiente protegidas;
* serviços corretamente segregados;
* cron jobs controlados;
* credenciais próprias;
* logs revisados;
* HTTPS.

Mudanças de provedor não alteram os princípios deste documento.

---

# 37. HTTPS

Produção deverá utilizar HTTPS.

HTTP inseguro não deverá ser utilizado para autenticação, sessão ou transmissão de dados protegidos.

---

# 38. TLS

Configuração TLS deverá seguir as capacidades seguras da infraestrutura adotada.

Protocolos ou configurações obsoletas deverão ser evitados.

---

# 39. Domínios

Domínios e subdomínios deverão possuir configuração controlada.

Mudanças deverão considerar:

* HTTPS;
* cookies;
* CORS;
* CSRF;
* redirects;
* integrações.

---

# 40. Headers e Proxy

Quando houver proxy reverso ou infraestrutura gerenciada, headers encaminhados deverão ser tratados conforme a confiança configurada.

Não confiar arbitrariamente em headers de origem.

---

# 41. Firewall

Quando disponível, controles de firewall deverão limitar exposição desnecessária de serviços.

Banco de dados e serviços internos não deverão ser publicamente expostos sem necessidade.

---

# 42. Acesso Administrativo

Acesso à infraestrutura deverá ser restrito a pessoas autorizadas.

Deverá ser possível revogar acessos individualmente.

---

# 43. Django Admin

O Django Admin possui capacidade elevada.

Deverá ser protegido por:

* autenticação;
* autorização;
* acesso restrito;
* configuração segura.

Acesso técnico administrativo não deverá ser amplamente distribuído.

---

# 44. Banco de Dados

O banco deverá ser acessível apenas pelos serviços e pessoas que realmente necessitam.

---

# 45. Acesso ao Banco

Acesso manual ao banco de produção deverá ser controlado.

Sempre que possível, preferir operações pela aplicação ou ferramentas administradas e auditáveis.

---

# 46. Backups

Backups deverão ser protegidos de acordo com os dados que contêm.

Como o GereIgreja processa dados Confidenciais, backups poderão conter informações de alta sensibilidade.

---

# 47. Armazenamento de Backups

O armazenamento deverá considerar:

* acesso;
* retenção;
* segregação;
* disponibilidade;
* restauração.

---

# 48. Serviços Externos

Todo serviço externo amplia a superfície de confiança.

Antes da adoção deverá ser avaliado:

```text
Quais dados recebe?

Qual credencial utiliza?

Como revogar?

Como monitora?

Qual dependência cria?
```

---

# 49. Integrações

Integrações deverão utilizar:

* HTTPS;
* credencial própria;
* escopo mínimo;
* tratamento de timeout;
* logs seguros;
* revogação.

---

# 50. WhatsApp e Comunicação

A documentação do GereIgreja possui fluxos específicos de WhatsApp e automações.

Credenciais utilizadas nesses fluxos deverão:

* permanecer fora do código;
* possuir segregação por ambiente;
* ser revogáveis;
* não aparecer em logs.

Automação de comunicação não deverá compartilhar segredos de forma indevida entre tenants.

---

# 51. E-mail

Credenciais SMTP ou de fornecedores de e-mail deverão ser protegidas como segredos.

Não deverão ser armazenadas em templates, scripts frontend ou documentação pública.

---

# 52. Webhooks

Endpoints de webhook deverão utilizar HTTPS.

Secrets de assinatura deverão ser armazenados com proteção adequada.

---

# 53. Cron Jobs

Cron jobs deverão executar com:

* configuração correta;
* segredo mínimo;
* tenant correto;
* logging seguro.

A documentação existente de cron para automações deverá seguir estes princípios.

---

# 54. Tasks

Workers e tasks deverão receber somente os segredos necessários à sua operação.

---

# 55. Automação

Processos automáticos deverão ser tratados como sujeitos técnicos.

Eles deverão possuir:

* identidade;
* finalidade;
* credenciais;
* limites;
* logs.

---

# 56. Logs de Infraestrutura

Logs poderão conter:

* endpoints;
* erros;
* eventos;
* métricas.

Não deverão conter indiscriminadamente:

* secrets;
* tokens;
* senhas;
* variáveis confidenciais.

---

# 57. Monitoramento

Monitoramento deverá observar:

* disponibilidade;
* erros;
* recursos;
* falhas de integração;
* falhas de cron;
* falhas de banco;
* eventos críticos.

---

# 58. Alertas

Alertas deverão ser acionáveis.

Exemplo:

```text
Banco indisponível
```

é mais útil do que:

```text
Algo falhou
```

Alertas não deverão incluir segredos.

---

# 59. Disponibilidade

Infraestrutura deverá suportar continuidade da plataforma.

Controles de disponibilidade incluem:

* monitoramento;
* backups;
* recuperação;
* capacidade adequada;
* dependências saudáveis.

---

# 60. Atualizações

Serviços e plataformas deverão receber atualizações de segurança conforme criticidade e compatibilidade.

---

# 61. Sistema Operacional e Plataforma

Quando a infraestrutura abstrair o sistema operacional, a responsabilidade será compartilhada com o provedor.

Quando o GereIgreja administrar diretamente a camada, atualizações deverão ser controladas.

---

# 62. Dependências de Infraestrutura

Dependências operacionais também deverão ser acompanhadas.

Exemplos:

* banco;
* runtime;
* serviços externos;
* ferramentas de deploy;
* imagens de container, quando utilizadas.

---

# 63. Pacotes e Imagens

Pacotes e imagens deverão ter origem confiável.

Não utilizar artefatos desconhecidos apenas por conveniência.

---

# 64. Vulnerabilidades

Vulnerabilidades de infraestrutura deverão seguir o GSF-12.

---

# 65. Configuração Segura do Django

Configurações críticas deverão ser revisadas por ambiente.

Incluem:

* DEBUG;
* SECRET_KEY;
* ALLOWED_HOSTS;
* cookies;
* CSRF;
* HTTPS;
* headers.

---

# 66. `DEBUG`

Produção deverá utilizar:

```python
DEBUG = False
```

O modo debug poderá revelar informações sensíveis.

---

# 67. `ALLOWED_HOSTS`

`ALLOWED_HOSTS` deverá refletir os hosts realmente utilizados.

Configurações excessivamente abertas deverão ser evitadas sem justificativa.

---

# 68. Cookies

Cookies de sessão e segurança deverão utilizar atributos apropriados conforme o ambiente.

Avaliar:

* Secure;
* HttpOnly;
* SameSite.

---

# 69. CSRF

Configurações relacionadas a CSRF deverão permanecer compatíveis com os domínios confiáveis.

Não ampliar origens confiáveis indiscriminadamente.

---

# 70. Sessões

Configuração de sessão deverá preservar proteção das identidades autenticadas.

---

# 71. CORS

CORS deverá ser restritivo.

A liberação de novas origens deverá possuir finalidade clara.

---

# 72. Arquivos Estáticos

Arquivos estáticos não deverão conter:

* secrets;
* credenciais;
* configurações privadas.

Todo conteúdo entregue ao navegador deve ser considerado publicamente acessível ao usuário que recebe a página.

---

# 73. Arquivos de Mídia

Mídias privadas deverão possuir estratégia de acesso compatível com sua classificação.

O simples fato de estarem armazenadas fora do banco não elimina a necessidade de autorização.

---

# 74. Uploads

Uploads deverão ser armazenados de forma que arquivos de tenants diferentes não sejam confundidos.

---

# 75. Proteção de Dados em Infraestrutura

A infraestrutura deverá preservar a classificação definida no GSF-02 e a proteção definida no GSF-08.

---

# 76. Multi-Tenant

Recursos de infraestrutura compartilhados deverão preservar isolamento lógico.

Exemplos:

```text
cache
storage
tasks
logs
backups
```

Compartilhar infraestrutura não deverá implicar mistura de dados.

---

# 77. Cache

Serviços de cache deverão utilizar chaves compatíveis com tenant e usuário quando necessário.

---

# 78. Serviços de Cache

Credenciais de cache deverão ser protegidas.

O serviço não deverá ficar exposto publicamente sem necessidade.

---

# 79. Banco em Não Produção

Ambientes não produtivos deverão utilizar banco próprio.

---

# 80. Dados de Produção em Desenvolvimento

Dados reais não deverão ser copiados integralmente para ambientes locais sem necessidade e controle.

Preferir dados:

* sintéticos;
* anonimizados;
* reduzidos.

---

# 81. Acessos Emergenciais

Situações emergenciais poderão exigir acesso ampliado.

Isso deverá ocorrer de maneira controlada.

---

# 82. Break Glass

Quando existir mecanismo de acesso emergencial, deverá possuir:

* finalidade clara;
* uso excepcional;
* rastreabilidade;
* revogação;
* revisão posterior.

Não deverá se tornar conta administrativa de uso cotidiano.

---

# 83. Auditoria de Acessos

Acessos administrativos relevantes à infraestrutura deverão ser rastreáveis quando a plataforma ou provedor permitir.

---

# 84. Incidentes de Infraestrutura

Exemplos:

```text
secret exposto
banco acessado indevidamente
serviço comprometido
produção indisponível
backup perdido
```

deverão seguir o GSF-13.

---

# 85. Vazamento de Segredos

Se houver suspeita de vazamento:

```text
Revogar
   ↓
Rotacionar
   ↓
Identificar impacto
   ↓
Buscar uso indevido
   ↓
Corrigir origem
```

Não aguardar confirmação de exploração para rotacionar um segredo claramente exposto.

---

# 86. Comprometimento de Credenciais

Credenciais comprometidas deverão ser tratadas como inválidas.

---

# 87. Indisponibilidade

Indisponibilidade crítica deverá acionar o processo operacional e de continuidade.

---

# 88. Recuperação

A recuperação deverá preservar segurança.

Não restaurar produção utilizando configurações temporárias inseguras sem controle.

---

# 89. Evidências

Durante incidentes, deverão ser preservadas:

* logs;
* horários;
* alterações;
* eventos;
* configurações relevantes.

Evitar destruir evidências durante correção.

---

# 90. Testes e Verificações

A infraestrutura deverá ser periodicamente revisada.

---

# 91. Revisão de Configuração

Verificar:

* DEBUG;
* hosts;
* cookies;
* CSRF;
* HTTPS;
* CORS;
* serviços;
* banco;
* storage.

---

# 92. Revisão de Secrets

Verificar:

* secrets no código;
* secrets em histórico;
* secrets em logs;
* credenciais obsoletas;
* credenciais sem responsável.

---

# 93. Revisão de Dependências

Avaliar:

* runtime;
* Django;
* banco;
* serviços externos;
* ferramentas.

---

# 94. Revisão de Deploy

Validar:

* configuração;
* migrations;
* variáveis;
* secrets;
* logs;
* cron jobs;
* health checks quando aplicáveis.

---

# 95. Evidências Arquiteturais

## EA-GSF-INFRA-001

O GSF estabelece segurança da infraestrutura como camada oficial de proteção.

## EA-GSF-INFRA-002

O GSF determina gestão segura de segredos e ambientes separados.

## EA-GSF-INFRA-003

O GSF estabelece HTTPS como requisito.

## EA-GSF-INFRA-004

O GSF prevê monitoramento, firewall e acesso administrativo restrito.

## EA-GSF-INFRA-005

O projeto possui documentação específica de deploy.

## EA-GSF-INFRA-006

O projeto possui documentação específica relacionada ao Render.

## EA-GSF-INFRA-007

O projeto possui documentação de cron relacionada a automações do WhatsApp.

## EA-GSF-INFRA-008

O backend possui documentação de Logging, Tasks, Cache e Performance.

## EA-GSF-INFRA-009

O GereIgreja possui arquitetura multi-tenant.

## EA-GSF-INFRA-010

O projeto possui documentação específica de LGPD e operação.

---

# 96. Especificações Oficiais

## GSF-INFRA-001

Produção, homologação e desenvolvimento deverão possuir segregação adequada.

## GSF-INFRA-002

Segredos não deverão ser armazenados diretamente no código-fonte.

## GSF-INFRA-003

Segredos deverão ser tratados como Confidenciais.

## GSF-INFRA-004

A `SECRET_KEY` deverá ser protegida e separada por ambiente.

## GSF-INFRA-005

Credenciais de banco deverão possuir acesso mínimo.

## GSF-INFRA-006

API Keys não deverão ser expostas no frontend.

## GSF-INFRA-007

Credenciais de serviços externos deverão ser segregadas por finalidade quando possível.

## GSF-INFRA-008

Produção não deverá depender de credenciais pessoais de desenvolvedores.

## GSF-INFRA-009

Arquivos `.env` com segredos não deverão ser versionados.

## GSF-INFRA-010

Segredo commitado deverá ser considerado comprometido.

## GSF-INFRA-011

Segredos expostos deverão ser revogados ou rotacionados imediatamente conforme o caso.

## GSF-INFRA-012

Credenciais deverão possuir menor privilégio.

## GSF-INFRA-013

Produção deverá utilizar HTTPS.

## GSF-INFRA-014

`DEBUG` deverá permanecer desabilitado em produção.

## GSF-INFRA-015

`ALLOWED_HOSTS` deverá possuir configuração controlada.

## GSF-INFRA-016

Cookies de segurança deverão possuir configuração apropriada ao ambiente.

## GSF-INFRA-017

CORS deverá ser restritivo.

## GSF-INFRA-018

CSRF não deverá ser enfraquecido indiscriminadamente por configuração.

## GSF-INFRA-019

Acesso administrativo à infraestrutura deverá ser restrito.

## GSF-INFRA-020

Banco de produção não deverá ficar publicamente exposto sem necessidade arquitetural.

## GSF-INFRA-021

Backups deverão possuir proteção compatível com os dados armazenados.

## GSF-INFRA-022

Integrações deverão utilizar credenciais protegidas.

## GSF-INFRA-023

Cron jobs e tasks deverão possuir configuração segura.

## GSF-INFRA-024

Logs de infraestrutura não deverão conter secrets.

## GSF-INFRA-025

Atualizações críticas de segurança deverão possuir prioridade.

## GSF-INFRA-026

Arquivos estáticos não deverão conter dados confidenciais ou segredos.

## GSF-INFRA-027

Dados reais de produção não deverão ser copiados indiscriminadamente para ambientes não produtivos.

## GSF-INFRA-028

Infraestrutura compartilhada deverá preservar isolamento multi-tenant.

## GSF-INFRA-029

Acessos emergenciais deverão ser excepcionais e rastreáveis.

## GSF-INFRA-030

Incidentes de infraestrutura deverão seguir o processo oficial de resposta.

---

# 97. Anti-Padrões

São considerados anti-padrões:

```text
SECRET_KEY = "minha-chave"
```

versionada no código.

---

```text
DATABASE_PASSWORD
em arquivo público
```

---

```text
API Key
dentro do JavaScript
```

---

```text
Produção e desenvolvimento
usando a mesma credencial
```

---

```text
Credencial pessoal do desenvolvedor
usada por serviço de produção
```

---

```text
DEBUG=True
em produção
```

---

```text
CORS_ALLOW_ALL_ORIGINS = True
```

sem justificativa.

---

```text
ALLOWED_HOSTS = ["*"]
```

sem necessidade avaliada.

---

```text
Secret removido do arquivo
=
secret deixou de estar comprometido
```

---

```text
.env
commitado no Git
```

---

```text
Dump de produção
no notebook local
```

---

```text
Token completo
em log de deploy
```

---

```text
Conta "admin"
compartilhada pela equipe
```

---

```text
Acesso emergencial
usado diariamente
```

---

# 98. Checklist

## Ambientes

* [ ] produção segregada;
* [ ] homologação segregada;
* [ ] desenvolvimento segregado;
* [ ] credenciais distintas;
* [ ] bancos distintos.

## Secrets

* [ ] fora do código;
* [ ] fora do Git;
* [ ] fora de logs;
* [ ] fora de arquivos estáticos;
* [ ] rotação prevista;
* [ ] revogação possível;
* [ ] responsável definido.

## Django

* [ ] `DEBUG=False`;
* [ ] `SECRET_KEY` protegida;
* [ ] `ALLOWED_HOSTS` revisado;
* [ ] CSRF revisado;
* [ ] cookies revisados;
* [ ] HTTPS;
* [ ] CORS revisado.

## Banco

* [ ] acesso restrito;
* [ ] credencial própria;
* [ ] menor privilégio;
* [ ] conexão segura;
* [ ] backups protegidos.

## Deploy

* [ ] secrets carregados com segurança;
* [ ] migrations revisadas;
* [ ] logs sem secrets;
* [ ] cron jobs revisados;
* [ ] serviços corretos por ambiente.

## Integrações

* [ ] credencial própria;
* [ ] escopo mínimo;
* [ ] HTTPS;
* [ ] timeout;
* [ ] revogação;
* [ ] logging seguro.

## WhatsApp e Comunicação

* [ ] credenciais protegidas;
* [ ] automações segregadas;
* [ ] tenants preservados;
* [ ] logs revisados.

## Cache

* [ ] acesso protegido;
* [ ] tenant em chaves quando necessário;
* [ ] secrets protegidos;
* [ ] exposição pública evitada.

## Dados

* [ ] produção não copiada indiscriminadamente;
* [ ] arquivos privados protegidos;
* [ ] backups classificados;
* [ ] storage revisado.

## Administração

* [ ] contas individuais;
* [ ] Django Admin restrito;
* [ ] acessos de infraestrutura restritos;
* [ ] break glass controlado.

## Monitoramento

* [ ] disponibilidade;
* [ ] erros;
* [ ] banco;
* [ ] cron;
* [ ] integrações;
* [ ] alertas acionáveis.

## Incidentes

* [ ] processo de revogação conhecido;
* [ ] rotação possível;
* [ ] logs disponíveis;
* [ ] evidências preserváveis.

---

# 99. Documentos Relacionados

## Frameworks

* GSF — GereIgreja Security Framework
* GAF — GereIgreja Authentication Framework
* GQF — GereIgreja Quality Framework
* GOC — GereIgreja Operations Center

## Segurança

* GSF-01 — Fundamentos de Segurança
* GSF-02 — Classificação e Proteção da Informação
* GSF-05 — Segurança Multi-Tenant
* GSF-06 — Segurança da Aplicação
* GSF-07 — Segurança das APIs
* GSF-08 — Segurança de Dados e Privacidade
* GSF-10 — Logging, Monitoramento e Auditoria
* GSF-11 — Backup, Continuidade e Recuperação
* GSF-12 — Gestão de Vulnerabilidades
* GSF-13 — Gestão de Incidentes de Segurança

## Arquitetura

* GEA-07 — Arquitetura da Segurança
* GEA-08 — Arquitetura Multi-Tenant

## Backend

* Middlewares
* Tasks
* Cache
* Logging
* Performance

## Deploy e Operações

* documentação existente em `docs/deploy/`
* documentação existente em `docs/operacoes/`
* documentação existente de cron do WhatsApp
* documentação existente de releases e deploy

---

# 100. Princípios Finais

A segurança de infraestrutura deverá partir da regra:

```text
Código seguro
+
infraestrutura insegura
=
plataforma insegura
```

Segredos deverão permanecer secretos.

Ambientes deverão permanecer segregados.

Credenciais deverão possuir escopo mínimo.

Acesso administrativo deverá ser restrito.

Produção deverá utilizar configuração segura.

Backups deverão ser protegidos.

Integrações deverão possuir credenciais próprias.

Cron jobs e automações deverão respeitar tenant e segurança.

Logs não deverão vazar os próprios mecanismos utilizados para proteger a plataforma.

A regra operacional deverá ser:

```text
Não versionar segredos.

Não compartilhar credenciais.

Não reutilizar credenciais sem necessidade.

Não confiar em configuração padrão sem revisar.

Não manter acesso depois que ele deixou de ser necessário.
```

Quando um segredo for exposto:

```text
não discutir primeiro
se alguém o utilizou.

Revogar primeiro.
```

O objetivo final é garantir que a infraestrutura do GereIgreja preserve:

```text
Confidencialidade
+
Integridade
+
Disponibilidade
+
Rastreabilidade
+
Isolamento
+
Recuperação
```

---

# 101. Status do Documento

**Pasta**

`docs/seguranca/`

**Arquivo**

`09-Seguranca-de-Infraestrutura-e-Segredos.md`

**Documento**

`GSF-09`

**Código**

`GSF-INFRA-SECRETS`

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

`10-Logging-Monitoramento-e-Auditoria.md`

**Código do próximo documento**

`GSF-10`

```
```
