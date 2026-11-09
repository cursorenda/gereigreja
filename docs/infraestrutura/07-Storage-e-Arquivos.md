Pasta:

docs/infraestrutura/

Arquivo:

07-Storage-e-Arquivos.md

Documento:

GINF-07

Código:

GINF-STORAGE-FILES

Família:

GINF --- GereIgreja Infrastructure Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GSF --- GereIgreja Security
Framework GOC --- GereIgreja Operations Center GQF --- GereIgreja
Quality Framework GAPI --- GereIgreja API Engineering GereIgreja Backend
Engineering

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GINF-07 --- Storage e Arquivos

> "Arquivos são dados da plataforma. Devem possuir proprietário, tenant,
> classificação, ciclo de vida, autorização e estratégia de
> recuperação."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com a Arquitetura
4.  Princípios Fundamentais
5.  Tipos de Arquivos
6.  Storage de Objetos
7.  Disco Local
8.  Ambientes
9.  Isolamento entre Ambientes
10. Buckets e Containers
11. Namespaces
12. Multi-Tenant
13. Identificação do Tenant
14. Convenção de Chaves
15. Nomes Originais
16. Metadados
17. Banco de Dados e Storage
18. Fonte de Verdade
19. Uploads
20. Validação de Upload
21. Tipos Permitidos
22. Extensão e MIME Type
23. Tamanho Máximo
24. Conteúdo Malicioso
25. Upload Direto
26. URLs Assinadas
27. Downloads
28. Arquivos Públicos
29. Arquivos Privados
30. Autorização
31. Exposição de URLs
32. Expiração
33. Cache e CDN
34. CORS
35. Processamento de Arquivos
36. Imagens
37. Documentos
38. Exportações
39. Importações
40. Arquivos Temporários
41. Limpeza
42. Versionamento
43. Substituição
44. Exclusão
45. Soft Delete
46. Retenção
47. LGPD
48. Criptografia em Trânsito
49. Criptografia em Repouso
50. Secrets e Credenciais
51. Menor Privilégio
52. Políticas de Acesso
53. Auditoria
54. Logging
55. Observabilidade
56. Métricas
57. Alertas
58. Capacidade
59. Custos
60. Lifecycle Policies
61. Classes de Storage
62. Backup
63. Replicação
64. Recuperação
65. Integridade
66. Checksums
67. Consistência
68. Falhas de Upload
69. Falhas de Download
70. Arquivos Órfãos
71. Reconciliação
72. Migração de Storage
73. Desenvolvimento
74. Staging
75. Produção
76. Testes
77. Segurança
78. Anti-Padrões
79. Arquitetura de Referência
80. Checklist
81. Documentos Relacionados
82. Princípios Finais
83. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece o padrão oficial para armazenamento e
manipulação de arquivos no GereIgreja.

Seu objetivo é garantir:

-   isolamento entre igrejas;
-   autorização;
-   segurança;
-   integridade;
-   rastreabilidade;
-   retenção;
-   escalabilidade;
-   recuperação;
-   controle de custos.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   uploads de usuários;
-   documentos;
-   imagens;
-   anexos;
-   relatórios;
-   exportações;
-   importações;
-   arquivos temporários;
-   storage de objetos;
-   arquivos privados;
-   arquivos públicos controlados.

Assets estáticos da aplicação poderão possuir estratégia própria de
build/deploy.

------------------------------------------------------------------------

# 3. Relação com a Arquitetura

``` text
Cliente
   │
   ▼
Django / API
   │
   ├────► PostgreSQL
   │       metadados
   │
   └────► Object Storage
           conteúdo
```

Quando upload direto for adotado:

``` text
Cliente
   │
   ├──► API solicita autorização
   │
   ▼
URL temporária
   │
   ▼
Object Storage
```

------------------------------------------------------------------------

# 4. Princípios Fundamentais

Todo arquivo deverá possuir contexto suficiente para responder:

``` text
quem é o proprietário?
a qual tenant pertence?
qual sua finalidade?
quem pode acessar?
por quanto tempo deve existir?
como será excluído?
```

Princípios:

-   privado por padrão;
-   tenant explícito;
-   nomes internos não previsíveis quando necessário;
-   validação;
-   mínimo acesso;
-   expiração para temporários;
-   metadados persistentes;
-   rastreabilidade.

------------------------------------------------------------------------

# 5. Tipos de Arquivos

Categorias conceituais:

``` text
uploads
documents
images
imports
exports
temporary
public-assets
```

A classificação deverá acompanhar o domínio real.

------------------------------------------------------------------------

# 6. Storage de Objetos

Storage de objetos deverá ser preferido para arquivos persistentes
quando a infraestrutura de produção assim exigir.

Benefícios:

-   durabilidade;
-   escalabilidade;
-   lifecycle;
-   acesso controlado;
-   independência das instâncias web.

------------------------------------------------------------------------

# 7. Disco Local

Disco local de container/instância não deverá ser considerado
persistência permanente.

Pode ser utilizado para processamento temporário quando controlado.

``` text
container reinicia
→ arquivo local pode desaparecer
```

------------------------------------------------------------------------

# 8. Ambientes

Cada ambiente deverá possuir storage isolado.

``` text
development
≠
staging
≠
production
```

------------------------------------------------------------------------

# 9. Isolamento entre Ambientes

Credenciais e buckets/containers deverão impedir que development escreva
em production.

------------------------------------------------------------------------

# 10. Buckets e Containers

A organização poderá utilizar:

-   bucket por ambiente;
-   bucket por finalidade;
-   combinação controlada.

A estratégia deverá permanecer simples e documentada.

------------------------------------------------------------------------

# 11. Namespaces

Dentro do storage, utilizar namespaces previsíveis.

Exemplo conceitual:

``` text
tenant/<tenant_id>/<category>/<object_id>/<file>
```

------------------------------------------------------------------------

# 12. Multi-Tenant

O tenant deverá participar da autorização e organização lógica.

A existência do tenant no path não substitui autorização da aplicação.

------------------------------------------------------------------------

# 13. Identificação do Tenant

Nunca confiar em tenant fornecido pelo cliente sem validação.

Fluxo:

``` text
usuário autenticado
→ tenant autorizado
→ recurso validado
→ chave de storage construída
```

------------------------------------------------------------------------

# 14. Convenção de Chaves

Chaves deverão evitar colisões.

Preferir identificadores internos.

Exemplo:

``` text
tenant/42/member/9/avatar/550e8400...
```

------------------------------------------------------------------------

# 15. Nomes Originais

O nome original poderá ser preservado como metadado para apresentação.

Não deverá necessariamente ser utilizado como chave física.

------------------------------------------------------------------------

# 16. Metadados

Metadados úteis:

-   tenant;
-   owner/resource;
-   nome original;
-   content type;
-   tamanho;
-   checksum;
-   data de criação;
-   status;
-   classificação;
-   storage key.

------------------------------------------------------------------------

# 17. Banco de Dados e Storage

O banco deverá manter os metadados de negócio necessários.

O storage mantém os bytes.

``` text
PostgreSQL
→ identidade e contexto

Storage
→ conteúdo
```

------------------------------------------------------------------------

# 18. Fonte de Verdade

A plataforma deverá saber qual camada define a existência lógica do
arquivo.

Um objeto existente no bucket sem registro válido poderá ser considerado
órfão.

------------------------------------------------------------------------

# 19. Uploads

Upload deverá seguir fluxo controlado:

``` text
autenticar
→ autorizar
→ validar
→ receber
→ armazenar
→ registrar
→ auditar quando necessário
```

------------------------------------------------------------------------

# 20. Validação de Upload

Validar:

-   tamanho;
-   tipo;
-   contexto;
-   autorização;
-   quantidade quando aplicável.

------------------------------------------------------------------------

# 21. Tipos Permitidos

Cada funcionalidade deverá definir tipos aceitos.

Não permitir qualquer formato por padrão.

------------------------------------------------------------------------

# 22. Extensão e MIME Type

Extensão e MIME fornecidos pelo cliente não são prova suficiente do
conteúdo.

Validação deverá considerar o risco e a finalidade.

------------------------------------------------------------------------

# 23. Tamanho Máximo

Toda superfície de upload deverá possuir limite.

Limites poderão existir em:

``` text
proxy
API
aplicação
storage
```

e deverão ser coerentes.

------------------------------------------------------------------------

# 24. Conteúdo Malicioso

Uploads são entrada não confiável.

Quando o risco justificar, poderão ser adotados:

-   scanner antimalware;
-   quarentena;
-   validação de conteúdo;
-   processamento isolado.

------------------------------------------------------------------------

# 25. Upload Direto

Uploads grandes poderão futuramente utilizar URL assinada para envio
direto ao storage.

A aplicação deverá continuar controlando:

-   tenant;
-   chave;
-   tamanho;
-   tipo;
-   expiração;
-   confirmação.

------------------------------------------------------------------------

# 26. URLs Assinadas

URLs assinadas deverão:

-   expirar;
-   possuir escopo mínimo;
-   apontar para objeto específico;
-   evitar permissões amplas.

------------------------------------------------------------------------

# 27. Downloads

Download de arquivo privado deverá validar autorização antes de conceder
acesso.

------------------------------------------------------------------------

# 28. Arquivos Públicos

Arquivo público deverá ser uma decisão explícita.

Exemplos possíveis:

-   logotipo público autorizado;
-   assets públicos.

Dados ministeriais, pessoais ou financeiros não deverão ser públicos por
padrão.

------------------------------------------------------------------------

# 29. Arquivos Privados

Arquivos de usuários e igrejas deverão ser privados por padrão.

------------------------------------------------------------------------

# 30. Autorização

Autorização deverá considerar:

``` text
usuário
+
tenant
+
recurso
+
permissão
```

Nunca apenas "possui a URL".

------------------------------------------------------------------------

# 31. Exposição de URLs

Evitar URLs permanentes públicas para arquivos privados.

Preferir acesso intermediado ou URL temporária assinada.

------------------------------------------------------------------------

# 32. Expiração

URLs temporárias deverão possuir janela adequada ao uso.

Não gerar URL privada com validade excessiva sem necessidade.

------------------------------------------------------------------------

# 33. Cache e CDN

CDN poderá ser utilizada para conteúdo apropriado.

Arquivos privados exigem política compatível com autenticação e cache.

Nunca cachear conteúdo confidencial publicamente.

------------------------------------------------------------------------

# 34. CORS

CORS do storage deverá permitir apenas origens e métodos necessários
quando upload/download direto for adotado.

------------------------------------------------------------------------

# 35. Processamento de Arquivos

Processamentos pesados deverão preferir workers.

``` text
upload
→ registrar
→ enfileirar
→ processar
→ atualizar status
```

------------------------------------------------------------------------

# 36. Imagens

Imagens poderão exigir:

-   resize;
-   thumbnail;
-   otimização;
-   remoção de metadados sensíveis quando aplicável.

Original e derivados deverão possuir relação conhecida.

------------------------------------------------------------------------

# 37. Documentos

Documentos poderão exigir controles adicionais conforme classificação.

Nunca executar conteúdo enviado pelo usuário diretamente no runtime da
aplicação.

------------------------------------------------------------------------

# 38. Exportações

Exportações grandes deverão seguir processamento assíncrono.

O arquivo gerado deverá possuir:

-   tenant;
-   owner;
-   expiração;
-   autorização.

------------------------------------------------------------------------

# 39. Importações

Importações deverão passar por validação antes de alterar dados.

Arquivo recebido não deverá ser considerado confiável.

------------------------------------------------------------------------

# 40. Arquivos Temporários

Temporários deverão possuir TTL/lifecycle.

Não depender de limpeza manual.

------------------------------------------------------------------------

# 41. Limpeza

Deverão existir rotinas para remover:

-   temporários expirados;
-   exports vencidos;
-   uploads abortados;
-   objetos órfãos confirmados.

------------------------------------------------------------------------

# 42. Versionamento

Versionamento do storage poderá ser utilizado conforme necessidade de
recuperação e custo.

Não confundir versionamento técnico com histórico de negócio.

------------------------------------------------------------------------

# 43. Substituição

Ao substituir um arquivo, definir:

-   nova chave ou mesma chave;
-   invalidação de cache;
-   retenção da versão anterior;
-   atualização dos metadados.

------------------------------------------------------------------------

# 44. Exclusão

Exclusão deverá ocorrer de forma coordenada entre banco e storage.

Evitar:

``` text
registro removido
+
arquivo esquecido para sempre
```

------------------------------------------------------------------------

# 45. Soft Delete

Quando o domínio utilizar soft delete, o comportamento do arquivo deverá
ser explicitamente definido.

O objeto poderá permanecer até fim da retenção.

------------------------------------------------------------------------

# 46. Retenção

Retenção deverá considerar:

-   finalidade;
-   contrato;
-   auditoria;
-   LGPD;
-   recuperação;
-   custo.

------------------------------------------------------------------------

# 47. LGPD

Arquivos podem conter dados pessoais e sensíveis.

Aplicar:

-   minimização;
-   classificação;
-   acesso;
-   retenção;
-   eliminação;
-   rastreabilidade.

------------------------------------------------------------------------

# 48. Criptografia em Trânsito

Uploads e downloads deverão utilizar HTTPS/TLS.

------------------------------------------------------------------------

# 49. Criptografia em Repouso

Storage de produção deverá utilizar criptografia em repouso quando
suportada e adequada à arquitetura.

Proteção adicional poderá ser exigida para categorias específicas.

------------------------------------------------------------------------

# 50. Secrets e Credenciais

Credenciais de storage deverão seguir GSF-09.

Nunca embutir credenciais administrativas em frontend.

------------------------------------------------------------------------

# 51. Menor Privilégio

Aplicação deverá possuir somente operações necessárias.

Exemplo:

``` text
app de uploads
→ escrever/ler objetos do escopo necessário

não:
→ administrar toda a conta de storage
```

------------------------------------------------------------------------

# 52. Políticas de Acesso

Políticas deverão ser revisáveis e explícitas.

Evitar bucket público por conveniência.

------------------------------------------------------------------------

# 53. Auditoria

Eventos relevantes poderão incluir:

-   upload;
-   download sensível;
-   exclusão;
-   exportação;
-   mudança de visibilidade.

A obrigatoriedade depende da classificação e do domínio.

------------------------------------------------------------------------

# 54. Logging

Logs deverão registrar metadados operacionais sem copiar conteúdo
sensível.

Campos úteis:

``` text
request_id
tenant_id
file_id
operation
result
duration
```

------------------------------------------------------------------------

# 55. Observabilidade

Storage deverá ser tratado como dependência crítica quando necessário ao
funcionamento da plataforma.

------------------------------------------------------------------------

# 56. Métricas

Monitorar:

-   uploads;
-   downloads;
-   erros;
-   latência;
-   bytes;
-   quantidade de objetos;
-   falhas de autorização;
-   storage utilizado.

------------------------------------------------------------------------

# 57. Alertas

Alertar para:

-   indisponibilidade;
-   taxa elevada de erro;
-   falha de lifecycle;
-   crescimento inesperado;
-   credencial inválida;
-   problemas de replicação quando adotada.

------------------------------------------------------------------------

# 58. Capacidade

Planejar:

``` text
volume atual
+
crescimento
+
derivados
+
exports
+
retenção
+
versionamento
```

------------------------------------------------------------------------

# 59. Custos

Custos podem incluir:

-   armazenamento;
-   requests;
-   transferência;
-   CDN;
-   recuperação;
-   versões antigas.

O desenho deverá considerar custo operacional sem comprometer segurança.

------------------------------------------------------------------------

# 60. Lifecycle Policies

Lifecycle poderá automatizar:

-   expiração;
-   transição de classe;
-   remoção de versões;
-   limpeza de uploads incompletos.

------------------------------------------------------------------------

# 61. Classes de Storage

Classes frias poderão ser utilizadas para dados raramente acessados
quando o tempo de recuperação for aceitável.

Não mover arquivos ativos apenas para reduzir custo sem avaliar
experiência.

------------------------------------------------------------------------

# 62. Backup

A necessidade de backup depende das capacidades do storage:

-   durabilidade;
-   versionamento;
-   replicação;
-   exclusão acidental.

Durabilidade do provedor não é sinônimo automático de proteção contra
exclusão lógica.

------------------------------------------------------------------------

# 63. Replicação

Replicação poderá ser adotada conforme requisitos de continuidade.

Deverá considerar custo e consistência.

------------------------------------------------------------------------

# 64. Recuperação

O plano deverá responder:

``` text
como recuperar arquivo excluído?
como recuperar bucket?
como reconstruir metadados?
como reconciliar banco e storage?
```

------------------------------------------------------------------------

# 65. Integridade

Arquivos críticos poderão utilizar checksum para validar integridade.

------------------------------------------------------------------------

# 66. Checksums

Checksum poderá ser calculado no upload e utilizado para:

-   integridade;
-   deduplicação controlada;
-   validação de transferência.

Deduplicação entre tenants exige análise de privacidade e autorização.

------------------------------------------------------------------------

# 67. Consistência

Banco e storage não compartilham transação ACID.

Fluxos deverão tolerar falha parcial.

Exemplo:

``` text
upload concluído
→ registro no banco falha
→ objeto órfão
→ reconciliação/cleanup
```

------------------------------------------------------------------------

# 68. Falhas de Upload

Uploads incompletos deverão:

-   expirar;
-   ser canceláveis;
-   não aparecer como arquivos válidos.

------------------------------------------------------------------------

# 69. Falhas de Download

Falha de storage deverá produzir erro controlado e observável.

Não expor detalhes internos do provedor ao usuário.

------------------------------------------------------------------------

# 70. Arquivos Órfãos

Objeto sem referência válida deverá ser identificado antes da exclusão.

Nunca remover automaticamente apenas porque uma consulta pontual não
encontrou registro, sem estratégia segura.

------------------------------------------------------------------------

# 71. Reconciliação

Jobs periódicos poderão comparar:

``` text
metadados do banco
↔
objetos do storage
```

para detectar inconsistências.

------------------------------------------------------------------------

# 72. Migração de Storage

Migrações entre provedores/buckets deverão possuir:

-   cópia;
-   verificação;
-   compatibilidade;
-   cutover;
-   rollback;
-   reconciliação.

------------------------------------------------------------------------

# 73. Desenvolvimento

Development deverá utilizar storage local ou serviço isolado compatível
com o fluxo.

Nunca exigir credenciais de production.

------------------------------------------------------------------------

# 74. Staging

Staging deverá testar:

-   uploads;
-   downloads;
-   URLs assinadas;
-   lifecycle;
-   permissões;
-   workers;
-   CORS quando aplicável.

------------------------------------------------------------------------

# 75. Produção

Produção deverá possuir:

-   storage isolado;
-   acesso privado por padrão;
-   criptografia;
-   lifecycle;
-   observabilidade;
-   owner;
-   recuperação documentada.

------------------------------------------------------------------------

# 76. Testes

Testar:

-   tenant;
-   autorização;
-   tipos;
-   tamanho;
-   upload;
-   download;
-   exclusão;
-   expiração;
-   falha parcial;
-   arquivos órfãos.

------------------------------------------------------------------------

# 77. Segurança

Uploads deverão ser considerados conteúdo não confiável.

Princípio:

``` text
armazenar
não significa
confiar
```

Arquivos não deverão ser executados ou interpretados de forma insegura.

------------------------------------------------------------------------

# 78. Anti-Padrões

Evitar:

``` text
MEDIA_ROOT local
como persistência única
em produção distribuída
```

------------------------------------------------------------------------

``` text
bucket inteiro
público
```

------------------------------------------------------------------------

``` text
URL privada
sem expiração
```

------------------------------------------------------------------------

``` text
storage key
sem tenant
em conteúdo multi-tenant
```

------------------------------------------------------------------------

``` text
nome enviado pelo usuário
usado diretamente como path
```

------------------------------------------------------------------------

``` text
arquivo temporário
sem limpeza
```

------------------------------------------------------------------------

``` text
credencial administrativa
no frontend
```

------------------------------------------------------------------------

``` text
excluir registro
e esquecer o objeto
```

------------------------------------------------------------------------

``` text
confiar apenas
na extensão do arquivo
```

------------------------------------------------------------------------

# 79. Arquitetura de Referência

``` text
                      CLIENTE
                         │
                         ▼
                   DJANGO / API
                    │         │
                    │         └──────► autorização
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     POSTGRESQL          OBJECT STORAGE
      metadata               bytes
          │                   │
          │                   ├── private objects
          │                   ├── temporary exports
          │                   └── public controlled assets
          │
          └──────────┬────────┘
                     ▼
                WORKERS
          processing / cleanup
          reconciliation

Observabilidade e auditoria
atravessam todo o fluxo.
```

------------------------------------------------------------------------

# 80. Checklist

## Storage

-   [ ] ambiente isolado;
-   [ ] bucket/container definido;
-   [ ] privado por padrão;
-   [ ] criptografia;
-   [ ] lifecycle.

## Multi-Tenant

-   [ ] tenant na autorização;
-   [ ] tenant no namespace quando necessário;
-   [ ] testes cross-tenant;
-   [ ] nenhuma URL concede acesso por si só.

## Upload

-   [ ] autenticação;
-   [ ] autorização;
-   [ ] tamanho máximo;
-   [ ] tipos permitidos;
-   [ ] validação;
-   [ ] tratamento de conteúdo não confiável.

## Arquivos

-   [ ] metadados no banco;
-   [ ] chave interna;
-   [ ] nome original separado;
-   [ ] temporários expiram;
-   [ ] exclusão coordenada.

## Segurança

-   [ ] HTTPS;
-   [ ] credenciais protegidas;
-   [ ] menor privilégio;
-   [ ] URLs assinadas expiram;
-   [ ] bucket não público indevidamente.

## Operação

-   [ ] métricas;
-   [ ] alertas;
-   [ ] capacidade;
-   [ ] custos;
-   [ ] recuperação;
-   [ ] reconciliação.

------------------------------------------------------------------------

# 81. Documentos Relacionados

-   GINF-01 --- Arquitetura da Infraestrutura
-   GINF-02 --- Ambientes e Configuração
-   GINF-03 --- Rede, DNS, Proxy e TLS
-   GINF-04 --- Runtime Django e Workers
-   GINF-05 --- Banco de Dados e Persistência
-   GINF-06 --- Redis, Cache e Filas
-   GSF-05 --- Segurança Multi-Tenant
-   GSF-08 --- Segurança de Dados e Privacidade
-   GSF-09 --- Gestão de Segredos e Criptografia
-   GSF-10 --- Logging, Monitoramento e Auditoria
-   GSF-14 --- Conformidade e LGPD
-   GAPI-08 --- Webhooks e Integrações
-   GAPI-10 --- Segurança e Privacidade
-   GAPI-11 --- Logging, Monitoramento e Auditoria
-   GOC --- GereIgreja Operations Center
-   GQF --- GereIgreja Quality Framework
-   GereIgreja Backend Engineering

------------------------------------------------------------------------

# 82. Princípios Finais

No GereIgreja:

``` text
arquivo
≠
apenas um path
```

Um arquivo é um recurso da plataforma com:

``` text
Tenant
+
Proprietário
+
Classificação
+
Autorização
+
Ciclo de vida
+
Persistência
```

A regra central é:

``` text
Privado por padrão.
Temporário com expiração.
Persistente com metadados.
Multi-tenant com isolamento.
```

E nenhuma instância web deverá ser tratada como local permanente de
arquivos de produção.

------------------------------------------------------------------------

# 83. Status do Documento

**Pasta**

`docs/infraestrutura/`

**Arquivo**

`07-Storage-e-Arquivos.md`

**Documento**

`GINF-07`

**Código**

`GINF-STORAGE-FILES`

**Família**

`GINF — GereIgreja Infrastructure Engineering`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Responsável**

`Equipe de Engenharia`

**Última atualização**

`Agosto de 2026`

**Documento anterior**

`GINF-06 — Redis, Cache e Filas`

**Próximo documento recomendado**

`08-Containers-Imagens-e-Registry.md`
