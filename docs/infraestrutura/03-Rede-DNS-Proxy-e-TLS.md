Pasta:

docs/infraestrutura/

Arquivo:

03-Rede-DNS-Proxy-e-TLS.md

Documento:

GINF-03

Código:

GINF-NETWORK-DNS-PROXY-TLS

Família:

GINF --- GereIgreja Infrastructure Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GSF --- GereIgreja Security
Framework GOC --- GereIgreja Operations Center GAPI --- GereIgreja API
Engineering GQF --- GereIgreja Quality Framework

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GINF-03 --- Rede, DNS, Proxy e TLS

> "A borda da plataforma deve expor somente o necessário, encaminhar
> somente o esperado e proteger todo tráfego sensível antes que ele
> alcance a aplicação."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com GINF-01 e GINF-02
4.  Princípios
5.  Visão Geral
6.  Zonas de Rede
7.  Rede Pública
8.  Rede Privada
9.  Serviços Internos
10. Exposição de Portas
11. Firewall
12. Regras de Entrada
13. Regras de Saída
14. DNS
15. Domínios
16. Subdomínios
17. Registros DNS
18. TTL
19. Mudanças de DNS
20. Proxy Reverso
21. Responsabilidades do Proxy
22. Encaminhamento
23. Headers de Proxy
24. IP do Cliente
25. Host
26. HTTPS
27. TLS
28. Certificados
29. Renovação de Certificados
30. Protocolos e Cifras
31. Redirecionamento HTTP para HTTPS
32. HSTS
33. Cookies Seguros
34. CSRF e Origens Confiáveis
35. CORS
36. APIs
37. Webhooks
38. Rate Limiting na Borda
39. Limites de Request
40. Uploads
41. Timeouts
42. Keep-Alive
43. Compressão
44. Cache na Borda
45. Health Checks
46. Load Balancing
47. Alta Disponibilidade
48. WebSockets e Conexões Persistentes
49. Serviços de Banco
50. Redis e Filas
51. Storage
52. Acesso Administrativo
53. VPN, Bastion e Acesso Privado
54. IPv4 e IPv6
55. Observabilidade
56. Logs de Acesso
57. Métricas
58. Alertas
59. Segurança
60. Proteção contra Abuso
61. DDoS
62. WAF
63. Gestão de Certificados e Chaves
64. Ambientes
65. Staging
66. Produção
67. Falhas de DNS
68. Falhas de TLS
69. Falhas de Proxy
70. Rollback
71. Testes
72. Anti-Padrões
73. Arquitetura de Referência
74. Checklist
75. Documentos Relacionados
76. Princípios Finais
77. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece os padrões oficiais de rede, DNS, proxy
reverso e TLS do GereIgreja.

Seu objetivo é garantir que a entrada e a saída de tráfego da plataforma
ocorram de forma:

-   controlada;
-   segura;
-   rastreável;
-   previsível;
-   compatível com a arquitetura multi-tenant;
-   preparada para operação e recuperação.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   DNS;
-   domínios;
-   subdomínios;
-   rede pública;
-   rede privada;
-   firewalls;
-   reverse proxies;
-   load balancers;
-   TLS;
-   certificados;
-   headers;
-   health checks;
-   tráfego HTTP/HTTPS;
-   APIs;
-   webhooks;
-   acessos administrativos.

------------------------------------------------------------------------

# 3. Relação com GINF-01 e GINF-02

GINF-01 define a arquitetura geral.

GINF-02 define ambientes e configuração.

GINF-03 detalha a borda e a conectividade.

``` text
GINF-01
Arquitetura
    ↓
GINF-02
Ambientes
    ↓
GINF-03
Rede e Borda
```

------------------------------------------------------------------------

# 4. Princípios

Toda configuração deverá observar:

-   deny by default;
-   menor exposição;
-   TLS por padrão;
-   menor privilégio;
-   separação de ambientes;
-   rastreabilidade;
-   automação;
-   defesa em profundidade.

------------------------------------------------------------------------

# 5. Visão Geral

Fluxo conceitual:

``` text
Internet
   │
   ▼
DNS
   │
   ▼
Proteção de Borda
   │
   ▼
HTTPS / TLS
   │
   ▼
Proxy / Load Balancer
   │
   ▼
Django / API
   │
   ├──► Banco
   ├──► Redis
   ├──► Filas
   └──► Storage
```

Banco, Redis e filas não deverão ser expostos diretamente à Internet por
padrão.

------------------------------------------------------------------------

# 6. Zonas de Rede

A infraestrutura deverá distinguir conceitualmente:

``` text
PUBLIC
PRIVATE
MANAGEMENT
```

A implementação concreta dependerá do provedor adotado.

------------------------------------------------------------------------

# 7. Rede Pública

Deverá conter apenas componentes que necessitam receber tráfego externo.

Exemplos:

-   load balancer;
-   proxy;
-   gateway;
-   serviços de borda.

------------------------------------------------------------------------

# 8. Rede Privada

Componentes internos deverão permanecer privados sempre que possível.

Exemplos:

-   banco;
-   Redis;
-   broker;
-   serviços internos;
-   interfaces administrativas.

------------------------------------------------------------------------

# 9. Serviços Internos

Serviços internos deverão ser acessíveis somente por componentes
autorizados.

``` text
Web
→ Database

Worker
→ Database

Internet
X Database
```

------------------------------------------------------------------------

# 10. Exposição de Portas

Toda porta exposta deverá possuir justificativa.

Inventariar:

``` text
porta
protocolo
origem
destino
finalidade
owner
```

------------------------------------------------------------------------

# 11. Firewall

Firewalls deverão utilizar regras mínimas.

Preferir allowlist.

Não manter regras temporárias indefinidamente.

------------------------------------------------------------------------

# 12. Regras de Entrada

Inbound deverá permitir apenas tráfego necessário.

Exemplo conceitual:

``` text
Internet
→ 443
→ Edge

Edge
→ porta interna da aplicação
```

------------------------------------------------------------------------

# 13. Regras de Saída

Egress também deverá ser considerado.

Aplicações não deverão possuir acesso irrestrito a destinos externos
quando o risco justificar controle mais forte.

------------------------------------------------------------------------

# 14. DNS

DNS é componente crítico.

Deverá possuir:

-   gestão controlada;
-   owner;
-   histórico;
-   proteção da conta;
-   documentação.

------------------------------------------------------------------------

# 15. Domínios

Domínios oficiais deverão possuir inventário.

Registrar:

-   finalidade;
-   ambiente;
-   serviço;
-   responsável;
-   certificado.

------------------------------------------------------------------------

# 16. Subdomínios

Subdomínios deverão seguir nomenclatura previsível.

Exemplos conceituais:

``` text
app
api
staging
assets
```

Os nomes reais dependerão da arquitetura oficial.

------------------------------------------------------------------------

# 17. Registros DNS

Utilizar tipos apropriados:

-   A;
-   AAAA;
-   CNAME;
-   MX;
-   TXT;
-   CAA quando adotado.

Mudanças deverão ser revisadas conforme impacto.

------------------------------------------------------------------------

# 18. TTL

TTL deverá equilibrar:

-   estabilidade;
-   propagação;
-   capacidade de mudança.

Antes de migrações críticas, poderá ser reduzido de forma planejada.

------------------------------------------------------------------------

# 19. Mudanças de DNS

Fluxo recomendado:

``` text
Planejar
  ↓
Validar destino
  ↓
Avaliar TTL
  ↓
Alterar
  ↓
Monitorar
  ↓
Confirmar propagação
```

------------------------------------------------------------------------

# 20. Proxy Reverso

O proxy reverso deverá funcionar como fronteira controlada entre
Internet e aplicação.

Não deverá conter regras de negócio do GereIgreja.

------------------------------------------------------------------------

# 21. Responsabilidades do Proxy

Poderá realizar:

-   terminação TLS;
-   roteamento;
-   redirecionamento;
-   limites de request;
-   compressão;
-   health checks;
-   headers;
-   proteção básica.

------------------------------------------------------------------------

# 22. Encaminhamento

O encaminhamento deverá ser explícito.

Evitar proxies genéricos que permitam atingir serviços arbitrários.

------------------------------------------------------------------------

# 23. Headers de Proxy

A aplicação deverá confiar em headers de proxy apenas quando estes forem
inseridos por infraestrutura confiável.

Headers enviados diretamente pelo cliente não deverão permitir spoofing
de contexto de segurança.

------------------------------------------------------------------------

# 24. IP do Cliente

Quando o IP original for necessário para:

-   segurança;
-   rate limiting;
-   auditoria;
-   investigação;

a cadeia de proxies confiáveis deverá ser configurada corretamente.

------------------------------------------------------------------------

# 25. Host

O host recebido deverá ser validado.

Aplicar configuração adequada de `ALLOWED_HOSTS` e controles
equivalentes.

------------------------------------------------------------------------

# 26. HTTPS

Produção deverá utilizar HTTPS em toda interface autenticada ou que
processe dados do GereIgreja.

Preferencialmente, toda superfície web pública deverá utilizar HTTPS.

------------------------------------------------------------------------

# 27. TLS

TLS deverá utilizar configurações modernas e suportadas.

Protocolos obsoletos não deverão ser mantidos sem justificativa
excepcional.

------------------------------------------------------------------------

# 28. Certificados

Certificados deverão:

-   corresponder aos domínios;
-   possuir cadeia válida;
-   ser emitidos por autoridade confiável;
-   ter renovação controlada.

------------------------------------------------------------------------

# 29. Renovação de Certificados

Renovação deverá ser automatizada sempre que possível.

Alertar antes de expiração.

``` text
Certificado expirado
=
indisponibilidade evitável
```

------------------------------------------------------------------------

# 30. Protocolos e Cifras

A seleção deverá acompanhar boas práticas atuais da infraestrutura
adotada.

Evitar hardcode documental de listas que envelhecem rapidamente.

A configuração efetiva deverá ser revisada periodicamente.

------------------------------------------------------------------------

# 31. Redirecionamento HTTP para HTTPS

Quando porta HTTP existir apenas para compatibilidade, deverá
redirecionar para HTTPS.

Não processar autenticação em HTTP.

------------------------------------------------------------------------

# 32. HSTS

HSTS deverá ser avaliado para produção.

Sua ativação exige cuidado porque instrui navegadores a exigir HTTPS por
período definido.

Subdomínios somente deverão ser incluídos quando todos estiverem
preparados.

------------------------------------------------------------------------

# 33. Cookies Seguros

Cookies de autenticação deverão utilizar configurações seguras
compatíveis com Django e GSF.

Exemplos:

-   Secure;
-   HttpOnly;
-   SameSite adequado.

------------------------------------------------------------------------

# 34. CSRF e Origens Confiáveis

Origens confiáveis deverão ser explicitamente configuradas.

Não utilizar wildcard amplo apenas para resolver erro de configuração.

------------------------------------------------------------------------

# 35. CORS

CORS deverá seguir GAPI-10.

Não é mecanismo de autenticação.

Permitir somente origens necessárias.

------------------------------------------------------------------------

# 36. APIs

APIs deverão ser expostas por HTTPS e seguir:

-   GAPI-03;
-   GAPI-09;
-   GAPI-10;
-   GAPI-11.

------------------------------------------------------------------------

# 37. Webhooks

Endpoints de webhook poderão ser públicos, mas deverão possuir segurança
própria.

Exemplos:

-   assinatura;
-   secret;
-   timestamp;
-   idempotência;
-   rate limiting.

------------------------------------------------------------------------

# 38. Rate Limiting na Borda

A borda poderá aplicar limites complementares.

Isso não substitui limites de aplicação quando estes dependem de:

-   usuário;
-   tenant;
-   operação;
-   regra de negócio.

------------------------------------------------------------------------

# 39. Limites de Request

Definir limites para reduzir abuso e consumo indevido.

Exemplos:

-   body;
-   headers;
-   upload;
-   tempo.

Os valores deverão considerar funcionalidades reais.

------------------------------------------------------------------------

# 40. Uploads

Uploads exigem atenção especial.

Fluxo poderá ser:

``` text
Cliente
  ↓
Edge
  ↓
Aplicação
  ↓
Storage
```

ou upload direto controlado ao storage quando arquitetura futura o
exigir.

------------------------------------------------------------------------

# 41. Timeouts

Timeouts deverão existir em todas as fronteiras relevantes.

Evitar conexões indefinidas.

Considerar:

-   client timeout;
-   proxy timeout;
-   application timeout;
-   integration timeout.

------------------------------------------------------------------------

# 42. Keep-Alive

Keep-alive poderá melhorar eficiência, mas deverá ser configurado de
forma compatível com:

-   proxy;
-   aplicação;
-   capacidade;
-   upstreams.

------------------------------------------------------------------------

# 43. Compressão

Compressão poderá ser aplicada a respostas adequadas.

Evitar compressão de conteúdo já comprimido ou cenários em que haja
risco de segurança específico.

------------------------------------------------------------------------

# 44. Cache na Borda

Cache somente deverá ser aplicado quando o conteúdo puder ser
compartilhado com segurança.

Nunca armazenar inadvertidamente respostas:

-   personalizadas;
-   autenticadas;
-   específicas de tenant;
-   confidenciais.

------------------------------------------------------------------------

# 45. Health Checks

Proxy/load balancer deverá utilizar health checks adequados.

O endpoint não deverá revelar detalhes internos desnecessários.

------------------------------------------------------------------------

# 46. Load Balancing

Quando houver múltiplas instâncias:

``` text
Edge
  │
  ├── Web 1
  ├── Web 2
  └── Web N
```

A aplicação deverá evitar dependência de estado local de uma instância.

------------------------------------------------------------------------

# 47. Alta Disponibilidade

Alta disponibilidade deverá ser aplicada proporcionalmente à
criticidade.

Não criar complexidade sem necessidade, mas evitar pontos únicos de
falha em componentes críticos quando o risco justificar.

------------------------------------------------------------------------

# 48. WebSockets e Conexões Persistentes

Se adotados futuramente, deverão possuir configuração específica de:

-   proxy;
-   timeout;
-   autenticação;
-   capacidade;
-   observabilidade.

Não assumir que configuração HTTP padrão é suficiente.

------------------------------------------------------------------------

# 49. Serviços de Banco

Banco deverá permanecer em rede privada sempre que possível.

Acesso:

``` text
Application
→ Database

Authorized Admin
→ controlled path
→ Database
```

------------------------------------------------------------------------

# 50. Redis e Filas

Redis e brokers não deverão ser expostos publicamente.

Credenciais e rede deverão restringir acesso aos componentes
necessários.

------------------------------------------------------------------------

# 51. Storage

Storage deverá possuir políticas de acesso explícitas.

Buckets públicos deverão ser exceção deliberada.

Arquivos privados não deverão se tornar públicos por configuração
padrão.

------------------------------------------------------------------------

# 52. Acesso Administrativo

Acesso a serviços internos deverá utilizar caminho administrativo
controlado.

Nunca abrir banco ou Redis à Internet apenas para facilitar manutenção.

------------------------------------------------------------------------

# 53. VPN, Bastion e Acesso Privado

Quando necessário, poderão ser adotados:

-   VPN;
-   bastion;
-   túnel seguro;
-   acesso privado do provedor.

A solução concreta deverá ser documentada após escolha da
infraestrutura.

------------------------------------------------------------------------

# 54. IPv4 e IPv6

Suporte deverá ser planejado conforme provedor e necessidade.

Se IPv6 estiver habilitado, regras de segurança deverão cobrir IPv6
também.

Não proteger apenas IPv4.

------------------------------------------------------------------------

# 55. Observabilidade

A borda deverá produzir sinais suficientes para investigar tráfego e
falhas.

------------------------------------------------------------------------

# 56. Logs de Acesso

Logs poderão registrar:

-   timestamp;
-   método;
-   rota;
-   status;
-   latência;
-   request ID;
-   IP conforme política;
-   user agent quando necessário.

Não registrar payloads sensíveis por padrão.

------------------------------------------------------------------------

# 57. Métricas

Métricas úteis:

-   requests;
-   status;
-   latência;
-   conexões;
-   TLS errors;
-   upstream errors;
-   timeouts;
-   volume.

------------------------------------------------------------------------

# 58. Alertas

Alertar para:

-   indisponibilidade;
-   erro TLS;
-   certificado próximo da expiração;
-   aumento de 5xx;
-   saturação;
-   upstream indisponível;
-   anomalias relevantes.

------------------------------------------------------------------------

# 59. Segurança

Aplicar defesa em profundidade.

``` text
DNS seguro
+
TLS
+
Firewall
+
Proxy
+
Aplicação segura
+
Observabilidade
```

Nenhuma camada substitui as demais.

------------------------------------------------------------------------

# 60. Proteção contra Abuso

A borda poderá ajudar a bloquear:

-   scanners;
-   floods;
-   padrões maliciosos;
-   excesso de requests.

Bloqueios deverão ser observáveis para evitar impacto silencioso em
usuários legítimos.

------------------------------------------------------------------------

# 61. DDoS

Proteção DDoS deverá utilizar capacidades do provedor ou serviço de
borda quando necessário.

A aplicação isoladamente não deverá ser considerada defesa suficiente
contra ataques volumétricos.

------------------------------------------------------------------------

# 62. WAF

WAF poderá ser adotado como camada adicional.

Não substitui:

-   validação;
-   autorização;
-   patching;
-   secure coding.

------------------------------------------------------------------------

# 63. Gestão de Certificados e Chaves

Chaves privadas TLS são secrets.

Deverão possuir:

-   armazenamento protegido;
-   acesso restrito;
-   rotação;
-   renovação;
-   revogação quando necessária.

------------------------------------------------------------------------

# 64. Ambientes

Cada ambiente deverá possuir configuração independente de rede e DNS
quando necessário.

Não permitir que staging seja roteado acidentalmente para produção.

------------------------------------------------------------------------

# 65. Staging

Staging deverá permitir testar:

-   TLS;
-   proxy;
-   headers;
-   redirects;
-   integrações;
-   regras de roteamento.

------------------------------------------------------------------------

# 66. Produção

Mudanças de borda em produção deverão possuir controle reforçado.

Especialmente:

-   DNS;
-   TLS;
-   firewall;
-   proxy;
-   load balancer.

------------------------------------------------------------------------

# 67. Falhas de DNS

Cenários:

-   registro incorreto;
-   propagação;
-   domínio expirado;
-   nameserver incorreto.

Deverão existir responsáveis e procedimento de recuperação.

------------------------------------------------------------------------

# 68. Falhas de TLS

Cenários:

-   certificado expirado;
-   hostname incorreto;
-   cadeia inválida;
-   renovação falha.

Monitoramento deverá detectar antes do usuário sempre que possível.

------------------------------------------------------------------------

# 69. Falhas de Proxy

Cenários:

-   upstream indisponível;
-   timeout;
-   rota incorreta;
-   header incorreto;
-   limite inadequado.

Logs e métricas deverão permitir distinguir falha de proxy de falha da
aplicação.

------------------------------------------------------------------------

# 70. Rollback

Mudanças de DNS/proxy deverão avaliar rollback.

Antes de alteração crítica, registrar configuração anterior ou mantê-la
versionada.

------------------------------------------------------------------------

# 71. Testes

Testar periodicamente:

-   HTTPS;
-   redirect;
-   certificado;
-   host;
-   headers;
-   health;
-   firewall;
-   acesso privado;
-   rate limits críticos;
-   uploads.

------------------------------------------------------------------------

# 72. Anti-Padrões

Evitar:

``` text
0.0.0.0/0
→ banco de dados
```

------------------------------------------------------------------------

``` text
Redis público
```

------------------------------------------------------------------------

``` text
TLS expirando
sem alerta
```

------------------------------------------------------------------------

``` text
CORS *
para resolver integração
```

------------------------------------------------------------------------

``` text
confiar em X-Forwarded-For
de qualquer origem
```

------------------------------------------------------------------------

``` text
cachear resposta
de usuário/tenant
na borda
sem política segura
```

------------------------------------------------------------------------

``` text
firewall temporário
que vira permanente
```

------------------------------------------------------------------------

``` text
alteração de DNS
sem plano de rollback
```

------------------------------------------------------------------------

# 73. Arquitetura de Referência

``` text
                         INTERNET
                            │
                            ▼
                     ┌─────────────┐
                     │     DNS     │
                     └──────┬──────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ EDGE / DDoS / WAF*   │
                └───────────┬───────────┘
                            │
                         HTTPS/TLS
                            │
                            ▼
                ┌───────────────────────┐
                │ PROXY / LOAD BALANCER │
                └───────────┬───────────┘
                            │
                       PRIVATE PATH
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
             WEB 1                    WEB N
                │                       │
                └───────────┬───────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
      DATABASE            REDIS             QUEUE
      PRIVATE             PRIVATE           PRIVATE

* quando adotado/necessário
```

------------------------------------------------------------------------

# 74. Checklist

## DNS

-   [ ] domínios inventariados;
-   [ ] owner definido;
-   [ ] registros documentados;
-   [ ] TTL adequado;
-   [ ] mudanças rastreáveis.

## Rede

-   [ ] serviços internos privados;
-   [ ] portas mínimas;
-   [ ] firewall;
-   [ ] inbound revisado;
-   [ ] egress avaliado.

## Proxy

-   [ ] upstream explícito;
-   [ ] headers seguros;
-   [ ] IP do cliente configurado corretamente;
-   [ ] timeouts;
-   [ ] health checks;
-   [ ] limites de request.

## TLS

-   [ ] HTTPS obrigatório;
-   [ ] certificado válido;
-   [ ] renovação automática;
-   [ ] alerta de expiração;
-   [ ] protocolos modernos;
-   [ ] redirect HTTP → HTTPS.

## Django/API

-   [ ] `ALLOWED_HOSTS`;
-   [ ] CSRF trusted origins;
-   [ ] CORS restrito;
-   [ ] cookies seguros;
-   [ ] webhooks protegidos.

## Dados

-   [ ] banco privado;
-   [ ] Redis privado;
-   [ ] filas privadas;
-   [ ] storage com política explícita.

## Operação

-   [ ] access logs;
-   [ ] métricas;
-   [ ] alertas;
-   [ ] rollback;
-   [ ] testes periódicos.

------------------------------------------------------------------------

# 75. Documentos Relacionados

-   GINF-01 --- Arquitetura da Infraestrutura
-   GINF-02 --- Ambientes e Configuração
-   GSF-03 --- GereIgreja Security Framework
-   GSF-07 --- Segurança das APIs
-   GSF-09 --- Gestão de Segredos e Criptografia
-   GSF-10 --- Logging, Monitoramento e Auditoria
-   GSF-12 --- Gestão de Vulnerabilidades
-   GSF-13 --- Gestão de Incidentes de Segurança
-   GAPI-03 --- Autenticação, Autorização e Tenant
-   GAPI-09 --- Idempotência e Rate Limiting
-   GAPI-10 --- Segurança e Privacidade
-   GAPI-11 --- Logging, Monitoramento e Auditoria
-   GOC --- GereIgreja Operations Center
-   GQF --- GereIgreja Quality Framework

------------------------------------------------------------------------

# 76. Princípios Finais

A borda da plataforma é parte da arquitetura de segurança.

``` text
Internet
não deve enxergar
a infraestrutura interna.
```

O GereIgreja deverá expor somente os pontos necessários para cumprir
suas funções.

O princípio central é:

``` text
Público por necessidade.
Privado por padrão.
Criptografado em trânsito.
Observável em operação.
```

DNS, rede, proxy e TLS deverão ser tratados como componentes críticos,
versionáveis e recuperáveis, e não como configurações ocasionais
realizadas apenas no momento do deploy.

------------------------------------------------------------------------

# 77. Status do Documento

**Pasta**

`docs/infraestrutura/`

**Arquivo**

`03-Rede-DNS-Proxy-e-TLS.md`

**Documento**

`GINF-03`

**Código**

`GINF-NETWORK-DNS-PROXY-TLS`

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

`GINF-02 — Ambientes e Configuração`

**Próximo documento recomendado**

`04-Runtime-Django-e-Workers.md`
