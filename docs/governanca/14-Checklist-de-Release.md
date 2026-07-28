# 14 - Checklist de Release

> "Uma release bem-sucedida é resultado de um processo consistente, não de sorte."

---

# Sumário

1. Objetivo
2. Filosofia de Release
3. Tipos de Release
4. Preparação
5. Checklist de Código
6. Checklist de Banco de Dados
7. Checklist de Segurança
8. Checklist de Performance
9. Checklist de Interface
10. Checklist de SEO
11. Checklist de Testes
12. Checklist de Documentação
13. Deploy
14. Pós-Deploy
15. Rollback
16. Princípios Finais

---

# 1. Objetivo

Este documento estabelece o procedimento oficial para publicação de novas versões do GereIgreja.

Seu objetivo é reduzir riscos, aumentar a previsibilidade das implantações e garantir que cada release seja executada de forma segura e organizada.

---

# 2. Filosofia de Release

Nenhuma publicação deverá ocorrer sem validação prévia.

Uma release representa a entrega de valor aos usuários e deve preservar a estabilidade da plataforma.

Todo deploy deverá seguir um processo padronizado.

---

# 3. Tipos de Release

O GereIgreja poderá realizar diferentes tipos de publicação:

- Correção de Bugs (Hotfix)
- Atualização Corretiva
- Atualização Evolutiva
- Nova Funcionalidade
- Grande Versão (Major Release)

Cada tipo deverá possuir planejamento compatível com seu impacto.

---

# 4. Preparação

Antes da publicação verificar:

- branch correta;
- código revisado;
- merge concluído;
- conflitos resolvidos;
- ambiente atualizado.

---

# 5. Checklist de Código

Confirmar que:

- código revisado;
- padrões da engenharia respeitados;
- lint executado;
- documentação atualizada;
- comentários temporários removidos;
- código morto eliminado.
- artefatos de build não versionados (ex.: `staticfiles_production/`, gerado por `collectstatic`).

---

# 6. Checklist de Banco de Dados

Verificar:

- migrations criadas;
- migrations testadas;
- backup realizado;
- rollback possível;
- índices revisados.

Nunca executar alterações estruturais sem backup.

---

# 7. Checklist de Segurança

Confirmar:

- permissões revisadas;
- autenticação validada;
- CSRF funcionando;
- variáveis sensíveis protegidas;
- logs ativos.

---

# 8. Checklist de Performance

Verificar:

- consultas otimizadas;
- cache funcionando;
- páginas críticas testadas;
- consumo de memória;
- tempo de resposta.

---

# 9. Checklist de Interface

Confirmar:

- responsividade;
- acessibilidade;
- GDS respeitado;
- componentes consistentes;
- navegação validada.

---

# 10. Checklist de SEO

Para áreas públicas verificar:

- sitemap;
- robots.txt;
- meta tags;
- Open Graph;
- URLs amigáveis;
- Schema.org;
- Canonical URLs.

---

# 11. Checklist de Testes

Executar:

- testes unitários;
- testes de integração;
- testes funcionais;
- smoke tests;
- testes manuais das funcionalidades críticas.

---

# 12. Checklist de Documentação

Verificar:

- documentação técnica;
- documentação funcional;
- changelog;
- roadmap;
- manuais atualizados.

---

# 13. Deploy

Durante o deploy:

- monitorar logs;
- validar migrations;
- acompanhar serviços;
- verificar disponibilidade.

Toda publicação deverá ser acompanhada.

---

# 14. Pós-Deploy

Após a publicação validar:

- login;
- dashboard;
- módulos críticos;
- banco;
- filas;
- backups;
- monitoramento.

Somente após essas verificações a release poderá ser considerada concluída.

---

# 15. Rollback

Toda release deverá possuir estratégia de retorno.

O plano deverá prever:

- restauração do banco;
- reversão do código;
- recuperação de arquivos;
- comunicação aos responsáveis.

Rollback faz parte da estratégia de release.

---

# 16. Princípios Finais

Toda publicação do GereIgreja deverá seguir este checklist.

Processos consistentes reduzem falhas, aumentam a confiabilidade da plataforma e preservam a experiência das igrejas que utilizam o sistema.

