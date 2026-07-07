# 04 - Padrões do Django Admin

> "O Django Admin do GereIgreja não é apenas um painel administrativo. Ele é o Centro de Operações da Plataforma."

---

# Sumário
1. Objetivo
2. Filosofia do Admin
3. O Papel do Django Admin
4. Estrutura Geral
5. Organização dos Menus
6. Dashboards
7. ModelAdmin
8. Formulários Administrativos
9. Pesquisa
10. Ações em Massa
11. Segurança
12. Auditoria
13. Performance
14. UX do Administrador
15. Checklist
16. Princípios Finais
---

# 1. Objetivo

Este documento estabelece os padrões oficiais para desenvolvimento do Django Admin do GereIgreja.

Seu objetivo é garantir que todas as telas administrativas mantenham consistência visual, organização funcional e elevada produtividade para os administradores da plataforma.

O Django Admin é considerado um componente estratégico do GereIgreja.

---

# 2. Filosofia do Admin

O painel administrativo existe para administrar a plataforma.

Ele não substitui o sistema utilizado pelas igrejas.

Seu público é composto por:

- Desenvolvedores;
- Equipe de suporte;
- Administradores do SaaS;
- Operadores internos.

Toda funcionalidade do Admin deverá contribuir para facilitar a administração técnica da plataforma.

---

# 3. O Papel do Django Admin

O Admin possui cinco responsabilidades principais.

## Administração

Gerenciar informações globais da plataforma.

## Monitoramento

Acompanhar indicadores técnicos e operacionais.

## Auditoria

Registrar e analisar eventos importantes do sistema.

## Engenharia

Disponibilizar ferramentas que auxiliem manutenção e evolução da plataforma.

## Suporte

Facilitar o atendimento às igrejas através de informações administrativas centralizadas.

---

# 4. Estrutura Geral

O Django Admin deverá ser organizado em grandes áreas funcionais.

Exemplo:

- Operação Diária
- Monitoramento
- Engenharia
- Configuração
- Autenticação
- Comunicação
- Blog
- Financeiro
- Auditoria

Cada grupo deverá reunir funcionalidades relacionadas ao mesmo domínio.

---

# 5. Organização dos Menus

Todos os menus deverão seguir critérios consistentes.

Prioridades:

- frequência de utilização;
- importância operacional;
- agrupamento lógico;
- facilidade de localização.

Itens utilizados diariamente deverão permanecer nas primeiras posições.

---

# 6. Dashboards

O Dashboard do Admin deverá apresentar informações relevantes para tomada de decisão.

Exemplos:

- Igrejas cadastradas;
- Usuários ativos;
- Backups;
- Saúde do servidor;
- Fila de processamento;
- Deploys;
- Auditoria;
- Crescimento da plataforma;
- Conversão de clientes;
- Indicadores financeiros.

O Dashboard deverá priorizar clareza em vez de excesso de informações.

---

# 7. ModelAdmin

Todo ModelAdmin deverá seguir padrões comuns.

Sempre que possível utilizar uma BaseAdmin compartilhada.

Cada tela deverá conter:

- list_display;
- list_filter;
- search_fields;
- ordering;
- readonly_fields;
- fieldsets;
- autocomplete_fields;
- paginação.

A experiência do administrador deverá ser consistente em todos os módulos.

---

# 8. Formulários Administrativos

Os formulários deverão priorizar simplicidade.

Sempre que possível:

- agrupar campos relacionados;
- utilizar ajuda contextual;
- evitar excesso de informações;
- destacar campos obrigatórios;
- reduzir rolagem desnecessária.

---

# 9. Pesquisa

Todas as entidades relevantes deverão possuir pesquisa eficiente.

A busca deverá considerar:

- nome;
- código;
- e-mail;
- telefone;
- identificadores;
- informações relevantes do domínio.

A pesquisa é um dos principais recursos do Admin.

---

# 10. Ações em Massa

Sempre que uma operação puder ser aplicada simultaneamente a vários registros, deverá ser implementada como uma ação administrativa.

Exemplos:

- ativar registros;
- desativar registros;
- alterar status;
- exportar dados;
- gerar relatórios;
- sincronizar informações;
- enviar notificações.

Ações destrutivas deverão exigir confirmação explícita do operador.

Sempre registrar as operações relevantes na auditoria.

---

# 11. Segurança

Toda funcionalidade administrativa deverá respeitar o sistema oficial de permissões.

Nenhum operador deverá visualizar informações sem autorização.

Operações críticas deverão possuir níveis adicionais de proteção quando necessário.

---

# 12. Auditoria

Toda alteração relevante realizada pelo Admin deverá ser registrada.

Exemplos:

- criação;
- alteração;
- exclusão;
- permissões;
- configurações;
- ações administrativas.

A rastreabilidade faz parte da segurança da plataforma.

---

# 13. Performance

Listagens administrativas deverão permanecer rápidas mesmo com grandes volumes de dados.

Boas práticas:

- paginação;
- select_related();
- prefetch_related();
- índices;
- consultas otimizadas.

A performance do painel administrativo deverá receber a mesma atenção dedicada ao sistema utilizado pelas igrejas.

---

# 14. UX do Administrador

A interface administrativa deverá ser:

- clara;
- objetiva;
- responsiva;
- previsível;
- consistente.

A produtividade do operador deve ser prioridade.

Toda nova tela deverá seguir o padrão visual estabelecido pelo GereIgreja Design System (GDS).

---

# 15. Checklist

Antes da publicação de uma nova tela administrativa verificar:

- permissões implementadas;
- pesquisa configurada;
- filtros definidos;
- paginação ativa;
- auditoria integrada;
- documentação atualizada;
- testes realizados.

---

# 16. Princípios Finais

O Django Admin do GereIgreja é parte integrante da arquitetura da plataforma.

Sua qualidade impacta diretamente a produtividade da equipe técnica, do suporte e da administração do sistema.

Toda evolução deverá preservar organização, segurança, desempenho e facilidade de utilização.

O painel administrativo deverá crescer mantendo a mesma identidade arquitetural definida para toda a plataforma.

O Django Admin constitui oficialmente o **GOC — GereIgreja Operations Center**, sendo o centro operacional responsável pela administração, monitoramento, engenharia, auditoria e suporte da plataforma.