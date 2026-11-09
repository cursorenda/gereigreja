Pasta:

docs/api/

Arquivo:

13-Depreciacao-e-Ciclo-de-Vida.md

Documento:

GAPI-13

Código:

GAPI-DEPRECATION-LIFECYCLE

Família:

GAPI --- GereIgreja API Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GSF --- GereIgreja Security
Framework GQF --- GereIgreja Quality Framework GOC --- GereIgreja
Operations Center GDF --- GereIgreja Documentation Framework

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GAPI-13 --- Depreciação e Ciclo de Vida

> "Uma API não termina quando surge uma versão nova. Ela termina quando
> seus consumidores foram identificados, migrados e a retirada ocorreu
> de forma controlada."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com GAPI-07
4.  Princípios
5.  Ciclo de Vida das APIs
6.  Estados Oficiais
7.  Proposta
8.  Experimental
9.  Ativa
10. Estável
11. Depreciada
12. Sunset
13. Removida
14. O que Pode ser Depreciado
15. Motivos para Depreciação
16. Critérios para Iniciar Depreciação
17. Inventário de Consumidores
18. Consumidores Internos
19. Consumidores Externos
20. Integrações
21. Métricas de Uso
22. Plano de Migração
23. Compatibilidade
24. Execução Paralela
25. Comunicação
26. Aviso de Depreciação
27. Documentação
28. Changelog
29. Headers de Depreciação
30. Data de Sunset
31. Prazos
32. Segurança
33. Vulnerabilidades
34. Privacidade e LGPD
35. Mudanças Emergenciais
36. Endpoints sem Uso
37. Versões Antigas
38. Campos e Parâmetros
39. Códigos de Erro
40. Webhooks
41. Integrações Externas
42. Credenciais e Métodos de Autenticação
43. Monitoramento da Migração
44. Critérios para Sunset
45. Processo de Sunset
46. Remoção Técnica
47. Limpeza de Código
48. Banco de Dados
49. Configurações
50. Observabilidade após Remoção
51. Rollback
52. Governança
53. Registro de Decisão
54. Responsabilidades
55. Testes
56. CI/CD
57. Anti-Padrões
58. Fluxo Oficial
59. Exemplo de Depreciação de Versão
60. Exemplo de Depreciação de Campo
61. Checklist
62. Documentos Relacionados
63. Princípios Finais
64. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece o processo oficial de depreciação e ciclo de
vida das APIs do GereIgreja.

Seu objetivo é impedir que:

-   endpoints antigos permaneçam indefinidamente;
-   consumidores sejam quebrados sem aviso;
-   versões obsoletas aumentem a superfície de ataque;
-   código legado permaneça sem proprietário;
-   documentação deixe de refletir o estado real da plataforma.

Toda retirada relevante deverá ser planejada, mensurada e rastreável.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   versões de API;
-   endpoints;
-   métodos;
-   campos;
-   parâmetros;
-   filtros;
-   códigos de erro;
-   webhooks;
-   integrações;
-   mecanismos de autenticação;
-   contratos externos;
-   funcionalidades expostas por API.

------------------------------------------------------------------------

# 3. Relação com GAPI-07

O GAPI-07 define:

``` text
como um contrato evolui
```

O GAPI-13 define:

``` text
como um contrato antigo
deixa de existir
```

Os dois documentos formam o ciclo completo de evolução das APIs.

------------------------------------------------------------------------

# 4. Princípios

A depreciação deverá observar:

-   previsibilidade;
-   comunicação;
-   evidência de uso;
-   migração;
-   segurança;
-   documentação;
-   observabilidade;
-   prazo proporcional ao impacto.

Depreciar não significa remover imediatamente.

------------------------------------------------------------------------

# 5. Ciclo de Vida das APIs

Fluxo conceitual:

``` text
Proposta
   ↓
Experimental
   ↓
Ativa
   ↓
Estável
   ↓
Depreciada
   ↓
Sunset
   ↓
Removida
```

Nem toda API precisará passar por estado experimental.

------------------------------------------------------------------------

# 6. Estados Oficiais

Cada contrato relevante deverá possuir estado compreensível.

Estados:

``` text
PROPOSED
EXPERIMENTAL
ACTIVE
STABLE
DEPRECATED
SUNSET
REMOVED
```

Os nomes concretos utilizados em ferramentas deverão ser padronizados
pela Engenharia.

------------------------------------------------------------------------

# 7. Proposta

Estado anterior à disponibilidade oficial.

Pode existir em:

-   ADR;
-   documentação;
-   especificação;
-   branch de desenvolvimento.

Não deverá ser tratado como contrato suportado.

------------------------------------------------------------------------

# 8. Experimental

Uma API experimental poderá mudar com menor garantia de compatibilidade.

Deverá ser explicitamente marcada.

Não permitir que consumidor externo assuma estabilidade sem comunicação
clara.

------------------------------------------------------------------------

# 9. Ativa

API disponível para uso e desenvolvimento.

Deverá possuir:

-   documentação;
-   testes;
-   proprietário;
-   observabilidade proporcional.

------------------------------------------------------------------------

# 10. Estável

Contrato consolidado com expectativa forte de compatibilidade dentro da
versão.

Mudanças deverão seguir GAPI-07.

------------------------------------------------------------------------

# 11. Depreciada

Uma API depreciada:

``` text
continua funcionando
+
não deve receber novos consumidores
+
possui substituição ou plano de retirada
```

A documentação deverá indicar claramente esse estado.

------------------------------------------------------------------------

# 12. Sunset

Sunset representa a data ou fase de encerramento do suporte.

Após o sunset, a API poderá ser desligada conforme plano aprovado.

------------------------------------------------------------------------

# 13. Removida

Contrato não está mais disponível.

A remoção deverá incluir limpeza técnica e documental adequada.

------------------------------------------------------------------------

# 14. O que Pode ser Depreciado

A depreciação poderá atingir:

-   versão completa;
-   endpoint;
-   método;
-   campo;
-   filtro;
-   parâmetro;
-   enum;
-   webhook;
-   integração;
-   autenticação antiga.

A granularidade deverá ser explicitada.

------------------------------------------------------------------------

# 15. Motivos para Depreciação

Exemplos:

-   nova versão;
-   contrato inadequado;
-   funcionalidade substituída;
-   fornecedor descontinuado;
-   risco de segurança;
-   custo operacional;
-   ausência de uso;
-   simplificação arquitetural.

------------------------------------------------------------------------

# 16. Critérios para Iniciar Depreciação

Antes de depreciar, identificar:

``` text
O que será retirado?
Por quê?
Quem usa?
Qual substituição?
Qual risco?
Qual prazo?
```

Não iniciar depreciação sem responsável.

------------------------------------------------------------------------

# 17. Inventário de Consumidores

Consumidores deverão ser identificados por evidência.

Fontes possíveis:

-   métricas;
-   logs;
-   API keys;
-   integrações cadastradas;
-   frontend;
-   aplicações internas;
-   documentação de clientes.

------------------------------------------------------------------------

# 18. Consumidores Internos

Mapear:

-   frontend;
-   serviços;
-   jobs;
-   scripts;
-   operações;
-   relatórios;
-   automações.

"É interno" não significa "ninguém depende".

------------------------------------------------------------------------

# 19. Consumidores Externos

Consumidores externos exigem comunicação mais formal.

Registrar quando possível:

-   organização;
-   integração;
-   versão;
-   contato técnico;
-   volume.

------------------------------------------------------------------------

# 20. Integrações

Integrações deverão possuir inventário suficiente para saber qual
contrato utilizam.

Isso é essencial antes de remover:

-   endpoint;
-   webhook;
-   autenticação;
-   versão.

------------------------------------------------------------------------

# 21. Métricas de Uso

Antes do sunset, acompanhar:

``` text
requests por versão
consumidores únicos
erros
último uso
volume
```

Evitar remoção baseada apenas em percepção.

------------------------------------------------------------------------

# 22. Plano de Migração

Toda depreciação relevante deverá indicar o caminho recomendado.

Exemplo:

``` text
v1 /membros/
        ↓
migrar para
        ↓
v2 /membros/
```

Quando necessário, documentar diferenças.

------------------------------------------------------------------------

# 23. Compatibilidade

Durante a janela de migração, a versão antiga deverá permanecer
compatível dentro do que foi oficialmente suportado, exceto correções
urgentes de segurança.

------------------------------------------------------------------------

# 24. Execução Paralela

Versões poderão coexistir:

``` text
/api/v1/
/api/v2/
```

O período paralelo deverá possuir objetivo de migração, não virar estado
permanente por omissão.

------------------------------------------------------------------------

# 25. Comunicação

Comunicação deverá ser proporcional ao consumidor.

Poderá incluir:

-   documentação;
-   changelog;
-   aviso interno;
-   contato direto;
-   release notes;
-   aviso na área administrativa quando aplicável.

------------------------------------------------------------------------

# 26. Aviso de Depreciação

O aviso deverá informar:

-   contrato afetado;
-   estado;
-   substituição;
-   impacto;
-   ação necessária;
-   prazo;
-   sunset quando definido.

------------------------------------------------------------------------

# 27. Documentação

Documentação de API depreciada deverá permanecer acessível durante a
janela de suporte.

Deverá exibir destaque:

``` text
DEPRECATED
```

e apontar para a alternativa.

------------------------------------------------------------------------

# 28. Changelog

Registrar:

``` text
Deprecated
→ início da depreciação

Removed
→ retirada efetiva
```

A data deverá ser explícita.

------------------------------------------------------------------------

# 29. Headers de Depreciação

Quando apropriado e compatível com a estratégia da plataforma, respostas
poderão incluir sinalização de depreciação via headers padronizados.

A adoção deverá ser uniforme, não improvisada por endpoint.

------------------------------------------------------------------------

# 30. Data de Sunset

Quando definida, a data deverá ser clara.

Exemplo conceitual:

``` text
Deprecated: 2026-09-01
Sunset: 2026-12-01
```

Datas reais deverão considerar risco e consumidores.

------------------------------------------------------------------------

# 31. Prazos

Não existe um único prazo adequado para todos os contratos.

Avaliar:

-   criticidade;
-   consumidores;
-   segurança;
-   esforço de migração;
-   dependências externas;
-   frequência de uso.

------------------------------------------------------------------------

# 32. Segurança

Nenhuma política de depreciação deverá obrigar a manter vulnerabilidade
explorável.

``` text
Segurança
>
janela de compatibilidade
```

Quando possível, oferecer mitigação e migração acelerada.

------------------------------------------------------------------------

# 33. Vulnerabilidades

Se a API antiga possuir vulnerabilidade:

``` text
avaliar risco
   ↓
mitigar
   ↓
corrigir
   ↓
acelerar migração
   ↓
retirar se necessário
```

O GSF-12 e GSF-13 deverão orientar a resposta.

------------------------------------------------------------------------

# 34. Privacidade e LGPD

Contratos antigos que exponham dados excessivos deverão ser corrigidos
ou retirados conforme risco.

Compatibilidade não justifica exposição desnecessária de dados pessoais.

------------------------------------------------------------------------

# 35. Mudanças Emergenciais

Uma retirada emergencial poderá ocorrer quando houver:

-   exploração ativa;
-   vazamento;
-   risco crítico;
-   obrigação legal;
-   comprometimento de fornecedor.

A decisão deverá ser registrada após estabilização, mesmo quando não
houver tempo para o fluxo normal.

------------------------------------------------------------------------

# 36. Endpoints sem Uso

Endpoints sem uso deverão ser candidatos a remoção.

Antes:

-   confirmar por métricas;
-   buscar consumidores ocultos;
-   verificar jobs/scripts;
-   revisar documentação.

------------------------------------------------------------------------

# 37. Versões Antigas

Versões antigas aumentam:

-   custo de testes;
-   código;
-   documentação;
-   superfície de ataque;
-   complexidade operacional.

O GereIgreja não deverá manter versões indefinidamente sem
justificativa.

------------------------------------------------------------------------

# 38. Campos e Parâmetros

Campos poderão ser depreciados antes da remoção.

Exemplo:

``` json
{
  "nome": "Exemplo",
  "nome_completo": "Exemplo"
}
```

Durante transição, ambos poderão coexistir quando seguro e tecnicamente
adequado.

------------------------------------------------------------------------

# 39. Códigos de Erro

Códigos programáticos também são contrato.

Sua retirada deverá considerar consumidores que os utilizam em lógica.

------------------------------------------------------------------------

# 40. Webhooks

Depreciação de webhook deverá considerar:

-   schema;
-   event name;
-   assinatura;
-   endpoint de destino;
-   consumidores ativos.

Eventos antigos não deverão ser interrompidos sem identificar
assinantes.

------------------------------------------------------------------------

# 41. Integrações Externas

Quando fornecedor descontinuar contrato utilizado pelo GereIgreja, criar
plano interno de migração.

Registrar:

-   prazo do fornecedor;
-   componentes afetados;
-   tenants afetados;
-   testes;
-   rollout.

------------------------------------------------------------------------

# 42. Credenciais e Métodos de Autenticação

Métodos antigos de autenticação deverão ser retirados quando inseguros
ou obsoletos.

Exemplo:

``` text
método legado
→ deprecated
→ migração
→ revogação
```

Credenciais antigas deverão ser revogadas após conclusão.

------------------------------------------------------------------------

# 43. Monitoramento da Migração

Durante a depreciação, criar visão operacional:

``` text
Uso v1
██████████

Uso v2
████
```

O objetivo é acompanhar a redução do legado.

------------------------------------------------------------------------

# 44. Critérios para Sunset

Antes do desligamento, verificar:

-   prazo cumprido;
-   consumidores notificados;
-   uso residual conhecido;
-   substituição funcional;
-   testes concluídos;
-   rollback avaliado;
-   suporte preparado.

------------------------------------------------------------------------

# 45. Processo de Sunset

Fluxo recomendado:

``` text
Confirmar data
    ↓
Revalidar consumidores
    ↓
Comunicação final
    ↓
Congelar novos consumidores
    ↓
Desligar contrato
    ↓
Monitorar erros
    ↓
Confirmar estabilidade
```

------------------------------------------------------------------------

# 46. Remoção Técnica

Após sunset:

-   remover rotas;
-   remover serializers obsoletos;
-   remover adapters;
-   remover flags;
-   remover permissões sem uso;
-   remover configurações;
-   atualizar testes.

A remoção deverá ser controlada.

------------------------------------------------------------------------

# 47. Limpeza de Código

Não manter indefinidamente:

``` text
if api_version == "v1":
    ...
else:
    ...
```

após a retirada oficial de v1.

Código morto aumenta risco.

------------------------------------------------------------------------

# 48. Banco de Dados

Não remover imediatamente coluna/tabela apenas porque endpoint foi
retirado.

Verificar:

-   outros módulos;
-   histórico;
-   auditoria;
-   migrações;
-   rollback;
-   retenção.

Ciclo de vida de API e ciclo de vida de dados não são idênticos.

------------------------------------------------------------------------

# 49. Configurações

Após remoção, revisar:

-   secrets;
-   API keys;
-   feature flags;
-   endpoints externos;
-   variáveis de ambiente;
-   jobs.

Configurações obsoletas também devem ser eliminadas.

------------------------------------------------------------------------

# 50. Observabilidade após Remoção

Após sunset, monitorar:

-   404/410 relacionados;
-   tentativas de uso antigo;
-   falhas de clientes;
-   tickets;
-   integrações quebradas.

Isso confirma se o inventário estava correto.

------------------------------------------------------------------------

# 51. Rollback

A retirada deverá possuir estratégia de rollback quando tecnicamente e
operacionalmente apropriado.

Não significa manter o legado para sempre.

Significa permitir recuperação de uma retirada mal avaliada.

------------------------------------------------------------------------

# 52. Governança

Depreciações relevantes deverão possuir aprovação proporcional ao
impacto.

Mudanças de grande alcance deverão envolver arquitetura, segurança,
operações e responsáveis de produto/domínio quando aplicável.

------------------------------------------------------------------------

# 53. Registro de Decisão

Registrar decisões importantes:

``` text
motivo
escopo
consumidores
alternativa
data de depreciação
sunset
riscos
responsável
```

ADR poderá ser utilizado quando a decisão for arquiteturalmente
significativa.

------------------------------------------------------------------------

# 54. Responsabilidades

A depreciação deverá possuir owner.

Responsabilidades incluem:

-   inventário;
-   comunicação;
-   migração;
-   métricas;
-   documentação;
-   remoção.

Sem owner, contratos tendem a permanecer indefinidamente.

------------------------------------------------------------------------

# 55. Testes

Durante coexistência:

-   testar versão antiga;
-   testar versão nova;
-   testar migração;
-   testar diferenças intencionais.

Após remoção:

-   remover testes obsoletos;
-   preservar testes relevantes da nova versão.

------------------------------------------------------------------------

# 56. CI/CD

Pipelines deverão impedir reintrodução acidental de contratos removidos
quando isso puder ser automatizado.

Documentação e schemas deverão permanecer sincronizados.

------------------------------------------------------------------------

# 57. Anti-Padrões

Evitar:

``` text
ninguém reclamou
→ pode apagar
```

------------------------------------------------------------------------

``` text
v2 existe
→ desligar v1 amanhã
```

------------------------------------------------------------------------

``` text
deprecated
sem data, owner ou alternativa
```

------------------------------------------------------------------------

``` text
manter todas as versões
para sempre
```

------------------------------------------------------------------------

``` text
apagar documentação de v1
antes do sunset
```

------------------------------------------------------------------------

``` text
preservar vulnerabilidade
até terminar prazo comercial
```

------------------------------------------------------------------------

``` text
remover endpoint
mas manter código morto
indefinidamente
```

------------------------------------------------------------------------

``` text
sem métricas
→ assumir que não há consumidores
```

------------------------------------------------------------------------

# 58. Fluxo Oficial

``` text
Identificar contrato legado
          ↓
      Avaliar risco
          ↓
Mapear consumidores
          ↓
Definir substituição
          ↓
Publicar depreciação
          ↓
Comunicar
          ↓
Medir migração
          ↓
Revalidar consumidores
          ↓
Sunset
          ↓
Remover
          ↓
Monitorar
          ↓
Limpar código/configuração
```

------------------------------------------------------------------------

# 59. Exemplo de Depreciação de Versão

``` text
/api/v1/
Status: STABLE
        ↓
v2 publicada
        ↓
/api/v1/
Status: DEPRECATED
Sunset planejado
        ↓
consumidores migram
        ↓
uso residual → 0 ou exceções resolvidas
        ↓
SUNSET
        ↓
REMOVED
```

------------------------------------------------------------------------

# 60. Exemplo de Depreciação de Campo

Contrato original:

``` json
{
  "nome": "Pessoa Exemplo"
}
```

Transição:

``` json
{
  "nome": "Pessoa Exemplo",
  "nome_completo": "Pessoa Exemplo"
}
```

Documentação:

``` text
nome
DEPRECATED
usar nome_completo
```

Após a janela aprovada, o campo antigo poderá ser removido em contexto
compatível com a política de versionamento.

------------------------------------------------------------------------

# 61. Checklist

## Planejamento

-   [ ] contrato identificado;
-   [ ] motivo registrado;
-   [ ] owner definido;
-   [ ] risco avaliado;
-   [ ] substituição definida.

## Consumidores

-   [ ] frontend verificado;
-   [ ] serviços internos verificados;
-   [ ] jobs/scripts verificados;
-   [ ] integrações verificadas;
-   [ ] consumidores externos identificados;
-   [ ] métricas disponíveis.

## Migração

-   [ ] documentação;
-   [ ] diferenças descritas;
-   [ ] testes;
-   [ ] execução paralela avaliada;
-   [ ] suporte preparado.

## Comunicação

-   [ ] changelog;
-   [ ] aviso de depreciação;
-   [ ] data de sunset quando aplicável;
-   [ ] consumidores notificados.

## Segurança

-   [ ] vulnerabilidades avaliadas;
-   [ ] privacidade avaliada;
-   [ ] autenticação antiga avaliada;
-   [ ] prazo não mantém risco crítico.

## Sunset

-   [ ] uso residual revisado;
-   [ ] comunicação final;
-   [ ] rollback avaliado;
-   [ ] monitoramento preparado.

## Remoção

-   [ ] rota removida;
-   [ ] código morto removido;
-   [ ] testes atualizados;
-   [ ] documentação atualizada;
-   [ ] secrets/configurações revistos;
-   [ ] observabilidade pós-sunset acompanhada.

------------------------------------------------------------------------

# 62. Documentos Relacionados

## API Engineering

-   GAPI-01 --- Arquitetura das APIs
-   GAPI-02 --- Padrões de Endpoints
-   GAPI-03 --- Autenticação, Autorização e Tenant
-   GAPI-04 --- Requests, Payloads e Validação
-   GAPI-05 --- Responses, Serialização e Erros
-   GAPI-06 --- Filtros, Busca, Ordenação e Paginação
-   GAPI-07 --- Versionamento e Compatibilidade
-   GAPI-08 --- Webhooks e Integrações
-   GAPI-09 --- Idempotência e Rate Limiting
-   GAPI-10 --- Segurança e Privacidade
-   GAPI-11 --- Logging, Monitoramento e Auditoria
-   GAPI-12 --- Testes de APIs
-   GAPI-13 --- Depreciação e Ciclo de Vida
-   GAPI-14 --- Mapa e Índice das APIs

## Segurança

-   GSF-07 --- Segurança das APIs
-   GSF-08 --- Segurança de Dados e Privacidade
-   GSF-12 --- Gestão de Vulnerabilidades
-   GSF-13 --- Gestão de Incidentes de Segurança
-   GSF-15 --- Secure Development Lifecycle

## Operações e Qualidade

-   GOC --- GereIgreja Operations Center
-   GQF --- GereIgreja Quality Framework

## Documentação e Arquitetura

-   GDF --- GereIgreja Documentation Framework
-   GEA --- GereIgreja Enterprise Architecture

------------------------------------------------------------------------

# 63. Princípios Finais

Uma API possui início, evolução e fim.

``` text
Criar
  ↓
Operar
  ↓
Evoluir
  ↓
Depreciar
  ↓
Migrar
  ↓
Remover
```

O princípio central é:

``` text
Depreciação
não é abandono.

É uma fase ativa
de migração e governança.
```

E:

``` text
Compatibilidade
não significa
manter legado eternamente.
```

No GereIgreja, contratos antigos deverão permanecer apenas enquanto
houver justificativa técnica, operacional, de segurança ou de migração.
A retirada deverá ser tão disciplinada quanto a criação da API,
preservando consumidores legítimos sem transformar compatibilidade em
dívida permanente.

------------------------------------------------------------------------

# 64. Status do Documento

**Pasta**

`docs/api/`

**Arquivo**

`13-Depreciacao-e-Ciclo-de-Vida.md`

**Documento**

`GAPI-13`

**Código**

`GAPI-DEPRECATION-LIFECYCLE`

**Família**

`GAPI — GereIgreja API Engineering`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Responsável**

`Equipe de Engenharia`

**Última atualização**

`Agosto de 2026`

**Documento anterior**

`GAPI-12 — Testes de APIs`

**Próximo documento recomendado**

`14-Mapa-e-Indice-das-APIs.md`
