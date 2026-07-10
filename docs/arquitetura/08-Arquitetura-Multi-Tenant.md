Pasta:
docs/arquitetura/

Arquivo:
08-Arquitetura-Multi-Tenant.md

Documento:
GEA-08

Framework:
GEA — GereIgreja Engineering Architecture

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 08 - Arquitetura Multi-Tenant

> "Uma única plataforma. Milhares de igrejas. Cada uma completamente isolada das demais."

---

# Sumário

1. Objetivo
2. O Conceito de Multi-Tenant
3. Filosofia da Arquitetura
4. Modelo Adotado
5. Identificação da Organização
6. Isolamento dos Dados
7. Fluxo das Requisições
8. Escopos da Aplicação
9. Compartilhamento de Recursos
10. Permissões entre Tenants
11. Segurança
12. Performance
13. Escalabilidade
14. Backup e Recuperação
15. Monitoramento
16. Evolução da Arquitetura
17. Documentos Relacionados
18. Princípios Finais

---

# 1. Objetivo

Este documento define a arquitetura Multi-Tenant oficial do GereIgreja.

Seu objetivo é garantir que múltiplas igrejas utilizem a mesma plataforma com total isolamento de dados, segurança e escalabilidade.

A arquitetura deverá permitir crescimento contínuo sem comprometer desempenho, organização ou privacidade.

---

# 2. O Conceito de Multi-Tenant

O GereIgreja é uma plataforma SaaS.

Todas as igrejas utilizam a mesma aplicação.

Cada igreja constitui um Tenant independente.

Cada Tenant possui:

- membros;
- financeiro;
- eventos;
- permissões;
- documentos;
- configurações;
- relatórios.

Nenhuma informação poderá ser compartilhada automaticamente entre Tenants.

---

# 3. Filosofia da Arquitetura

O modelo adotado privilegia:

- simplicidade;
- segurança;
- baixo custo operacional;
- facilidade de manutenção;
- alta escalabilidade.

O isolamento lógico deverá ser suficiente para garantir privacidade entre organizações.

---

# 4. Modelo Adotado

O GereIgreja utiliza:

**Shared Database + Shared Schema + Tenant ID**

Toda entidade pertencente à igreja deverá possuir referência ao Tenant.

Exemplo:

```text
Igreja
    │
    ▼
Tenant
    │
    ▼
Membros
Financeiro
Eventos
EBD
Agenda
Comunicação
```

Este modelo reduz custos operacionais e facilita manutenção.

---

# 5. Identificação da Organização

Toda requisição deverá identificar a igreja responsável.

A identificação poderá ocorrer por:

- usuário autenticado;
- subdomínio (futuro);
- domínio personalizado (futuro);
- token da API.

Após identificada, todas as consultas deverão permanecer restritas ao Tenant correspondente.

---

# 6. Isolamento dos Dados

Toda consulta deverá respeitar o Tenant ativo.

Nunca será permitido:

- listar dados de outra igreja;
- editar informações externas;
- executar consultas globais sem autorização.

O isolamento dos dados é um princípio fundamental da plataforma.

---

# 7. Fluxo das Requisições

Toda operação seguirá o fluxo abaixo.

```text
Usuário
   │
   ▼
Autenticação
   │
   ▼
Identificação do Tenant
   │
   ▼
Permissões
   │
   ▼
Services
   │
   ▼
Models Filtrados pelo Tenant
   │
   ▼
Banco de Dados
```

Nenhuma consulta deverá ignorar esse fluxo.

---

# 8. Escopos da Aplicação

A plataforma possuirá dois escopos principais.

## Escopo Global

Utilizado exclusivamente pela administração do SaaS.

Exemplos:

- planos;
- clientes;
- faturamento;
- suporte;
- monitoramento.

---

## Escopo da Igreja

Utilizado pelas igrejas.

Exemplos:

- membros;
- financeiro;
- congregações;
- patrimônio;
- eventos;
- departamentos.

Os dois escopos deverão permanecer claramente separados.

---

# 9. Compartilhamento de Recursos

Alguns recursos poderão ser compartilhados entre todos os Tenants.

Exemplos:

- tabelas auxiliares;
- estados;
- cidades;
- países;
- versões do sistema;
- componentes visuais.

Esses recursos não contêm informações específicas das igrejas.

---

# 10. Permissões entre Tenants

Nenhum usuário poderá acessar outro Tenant.

Nem mesmo administradores locais.

Somente usuários do escopo SaaS poderão executar operações globais.

Todas essas operações deverão ser auditadas.

---

# 11. Segurança

A arquitetura Multi-Tenant deverá garantir:

- isolamento lógico;
- autenticação obrigatória;
- autorização por Tenant;
- auditoria;
- criptografia em trânsito;
- proteção contra vazamento de dados.

Toda consulta deverá validar automaticamente o Tenant ativo.

---

# 12. Performance

Mesmo atendendo milhares de igrejas, a plataforma deverá manter desempenho consistente.

Boas práticas:

- índices por Tenant;
- consultas filtradas;
- paginação;
- cache;
- otimização de consultas.

Performance faz parte da arquitetura.

---

# 13. Escalabilidade

A arquitetura deverá permitir crescimento contínuo.

A expansão poderá ocorrer por:

- aumento da infraestrutura;
- balanceamento de carga;
- replicação;
- cache distribuído;
- processamento assíncrono.

Nenhuma decisão atual deverá limitar o crescimento futuro.

---

# 14. Backup e Recuperação

Os backups deverão considerar:

- integridade dos dados;
- restauração segura;
- retenção;
- recuperação em caso de desastre.

Sempre que possível, deverá existir possibilidade de recuperação por Tenant.

---

# 15. Monitoramento

A plataforma deverá acompanhar:

- utilização por Tenant;
- consumo de recursos;
- erros;
- disponibilidade;
- crescimento.

Essas informações apoiarão decisões técnicas e operacionais.

---

# 16. Evolução da Arquitetura

A arquitetura deverá permitir futuras evoluções, como:

- subdomínios automáticos;
- domínios personalizados;
- múltiplos bancos de dados;
- isolamento físico por Tenant;
- replicação geográfica;
- alta disponibilidade.

As evoluções deverão preservar compatibilidade com a arquitetura existente.

---

# 17. Documentos Relacionados

- GEA-02 — Arquitetura da Plataforma
- GEA-03 — Arquitetura dos Módulos
- GEA-04 — Arquitetura do Backend
- GEA-06 — Arquitetura das APIs
- GEA-07 — Arquitetura da Segurança
- GAF — Framework de Autenticação e Permissões
- GSF — Framework de Segurança

---

# 18. Princípios Finais

A arquitetura Multi-Tenant do GereIgreja é um dos pilares da plataforma SaaS.

Seu objetivo é permitir que milhares de igrejas compartilhem a mesma infraestrutura sem comprometer segurança, desempenho ou privacidade.

Toda evolução futura deverá preservar o isolamento entre organizações, garantir escalabilidade e manter a simplicidade operacional que caracteriza a arquitetura do GereIgreja.

