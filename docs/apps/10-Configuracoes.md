Pasta:
docs/apps/

Arquivo:
10-Configuracoes.md

Documento:
APP-10

Família:
Apps — Documentação Funcional

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Setembro de 2026

# 10 — Configurações

> O domínio Configurações concentra parâmetros institucionais e operacionais que alteram o comportamento dos demais módulos, preservando escopo por ministério, igreja e contexto funcional.

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Princípios do Domínio
5. Ministério e Igreja
6. Configuração Local da Igreja
7. Fallback e Herança
8. Configurações da EBD
9. Programações Padrão
10. Configurações que Afetam Eventos
11. Dados Institucionais da Igreja
12. CNPJ e Dados Documentais
13. Configuração Financeira
14. Departamentos e Estrutura Organizacional
15. Multi-Tenancy
16. Permissões
17. Validação e Integridade
18. Cache e Propagação
19. Auditoria
20. Segurança e Privacidade
21. Testes e Qualidade
22. Compatibilidade e Rollout
23. Limites do Domínio
24. Pontos a Validar
25. Documentos Relacionados
26. Princípios Finais
27. Status

---

# 1. Objetivo

Este documento consolida a visão funcional canônica do domínio Configurações do GereIgreja.

Seu objetivo é registrar:

- quais tipos de configuração pertencem ao domínio;
- como configurações ministeriais e locais se relacionam;
- como outros módulos consomem essas definições;
- como fallback, override e herança devem funcionar;
- quais alterações possuem impacto operacional amplo;
- quais regras são de negócio e quais pertencem à implementação técnica.

Este documento não substitui Models, Forms, Services, Signals, Backend, Segurança ou documentação específica de cada módulo consumidor.

---

# 2. Escopo

O domínio Configurações cobre, conforme as fontes auditadas:

- dados institucionais da igreja;
- configuração ministerial;
- configuração local da igreja;
- parâmetros da EBD;
- programação padrão da igreja;
- recorrência;
- horários;
- parâmetros utilizados por Agenda e Eventos;
- referências financeiras da igreja;
- estruturas organizacionais e departamentais;
- catálogos e dados auxiliares;
- preferências ou parâmetros operacionais compartilhados.

Nem toda configuração técnica do projeto pertence a este domínio funcional.

---

# 3. Papel deste Documento

Este é o documento funcional canônico de Configurações em `docs/apps/`.

A relação esperada é:

```text
docs/apps/10-Configuracoes.md
        ↓
Política funcional de configuração
        ↓
configuracao/
docs/apps/03-Financeiro.md
docs/apps/06-EBD.md
docs/apps/07-Eventos.md
docs/apps/09-Usuarios.md
        ↓
Consumo das configurações por domínio
```

Cada módulo consumidor continua responsável por documentar o comportamento específico decorrente dessas configurações.

---

# 4. Princípios do Domínio

Configuração deve representar política explícita, não regra escondida em código.

Princípios:

- configuração deve possuir escopo definido;
- valores locais devem prevalecer apenas quando houver override legítimo;
- fallback deve ser previsível;
- mudança de configuração não deve atravessar tenants;
- configuração não deve substituir autorização;
- alterações relevantes devem ser rastreáveis;
- defaults devem ser seguros e documentados.

---

# 5. Ministério e Igreja

A documentação atual mostra dois níveis recorrentes de configuração:

```text
Ministério
↓
governança e padrão global

Igreja local
↓
override operacional quando permitido
```

Essa separação aparece claramente na evolução da EBD e também em outras áreas da plataforma.

O princípio funcional é:

- o Ministério pode fornecer padrão;
- a igreja pode possuir configuração própria quando o domínio permitir;
- o sistema deve saber qual fonte está vigente.

---

# 6. Configuração Local da Igreja

A configuração local permite adaptar comportamento operacional sem alterar a política global para todas as igrejas.

A EBD é o exemplo mais bem documentado desse padrão.

A documentação registra campos locais na igreja para:

- `ebd_periodo`;
- `ebd_dia_semana`;
- `ebd_horario`.

Esse modelo deve ser utilizado apenas quando o domínio realmente exigir autonomia local.

---

# 7. Fallback e Herança

A estratégia documentada para EBD é:

```text
Existe configuração local válida?
   ├── Sim → usar valor da igreja
   └── Não → usar configuração ministerial
```

Esse padrão é descrito como **dual-source com prioridade local** durante rollout.

Fallback deve ser:

- explícito;
- determinístico;
- testável;
- visível para suporte quando necessário.

Não deve existir escolha ambígua entre múltiplas fontes.

---

# 8. Configurações da EBD

A configuração da EBD controla:

- tipo de período;
- dia da semana;
- horário.

Esses valores influenciam diretamente:

- geração de períodos;
- lições;
- cronograma;
- chamada;
- frequência;
- agenda;
- preparação anual.

Mudanças nesses parâmetros podem alterar comportamento operacional relevante.

Por isso, não devem ser tratadas como simples preferências visuais.

---

# 9. Programações Padrão

A documentação de Eventos registra a evolução de Programações padrão da igreja.

Capacidades documentadas incluem:

- recorrência;
- frequência avançada;
- hora de término;
- cálculo de duração;
- validações condicionais;
- resumo da configuração.

Programações padrão são configurações que geram comportamento repetitivo em Eventos e Agenda.

---

# 10. Configurações que Afetam Eventos

Programações configuradas podem gerar ou orientar eventos.

A documentação atual registra:

- integração entre Configurações e Eventos;
- proteção contra conflitos com EBD;
- consolidação do Evento como modelo funcional principal.

Portanto, Configurações define política de recorrência; Eventos executa o ciclo de vida do evento.

---

# 11. Dados Institucionais da Igreja

A configuração da igreja contém dados institucionais utilizados por vários módulos.

Exemplos encontrados nas fontes:

- dados cadastrais;
- CNPJ;
- parâmetros EBD;
- referências financeiras;
- dados operacionais usados por documentos e fluxos.

Esses dados devem possuir fonte de verdade clara.

---

# 12. CNPJ e Dados Documentais

A documentação para usuário final registra comportamento de CNPJ com opção de utilizar o CNPJ do Ministério.

O comportamento documentado é:

```text
Usar CNPJ do Ministério
→ valor herdado e não editável localmente

Usar CNPJ próprio
→ igreja informa seu próprio valor
```

Também é documentada atualização automática quando o CNPJ ministerial muda para igrejas que utilizam essa opção.

Esse é outro exemplo de herança controlada entre Ministério e igreja.

---

# 13. Configuração Financeira

As fontes recentes indicam que a configuração da igreja também participa de definições financeiras, como referência a conta padrão de eventos.

O domínio Configurações deve apenas armazenar e governar essas escolhas.

As regras de movimentação, autorização e contabilização continuam pertencendo ao Financeiro.

---

# 14. Departamentos e Estrutura Organizacional

A documentação recente indica evolução da relação entre:

- Ministério;
- igreja;
- departamentos;
- Financeiro.

Configurações pode fornecer estrutura e parâmetros, mas não deve assumir as regras funcionais dos departamentos.

A autoridade funcional sobre departamentos permanece em `docs/apps/05-Departamentos.md`.

---

# 15. Multi-Tenancy

Toda configuração local deve estar vinculada ao tenant correto.

É obrigatório impedir:

- edição de configuração de outra igreja;
- aplicação de override de outro tenant;
- cache compartilhado incorretamente;
- leitura de parâmetros fora do escopo;
- propagação indevida de dados institucionais.

Configuração ministerial pode possuir escopo mais amplo, mas isso deve estar explicitamente previsto.

---

# 16. Permissões

Nem todo usuário pode alterar configuração.

A autorização deve considerar:

- usuário;
- igreja ativa;
- nível hierárquico;
- regra da página;
- tipo de configuração;
- escopo da alteração.

Visualizar um valor não implica permissão para modificá-lo.

Configurações de alto impacto devem possuir controle de acesso mais restritivo.

---

# 17. Validação e Integridade

Configurações devem ser validadas antes de persistir.

Exemplos:

- dia da semana válido;
- período EBD válido;
- horário coerente;
- recorrência consistente;
- relações pertencentes à mesma igreja;
- CNPJ e documentos no formato esperado;
- referências financeiras do tenant correto.

Validação deve existir no backend, não apenas no frontend.

---

# 18. Cache e Propagação

A documentação da EBD registra que a chave de cache do auto-sync passou a considerar a igreja ativa.

Isso demonstra um princípio geral:

```text
configuração por tenant
→ cache também deve ser por tenant
```

Alterações relevantes também podem exigir propagação para automações, sinais ou dados derivados.

A forma técnica de propagação pertence ao Backend.

---

# 19. Auditoria

Mudanças críticas de configuração devem ser rastreáveis quando aplicável.

Exemplos:

- alteração de parâmetros EBD;
- troca de CNPJ próprio/herdado;
- mudança de conta padrão;
- alteração de recorrência;
- alteração de parâmetros que afetam módulos inteiros.

A auditoria deve registrar contexto suficiente para explicar mudanças de comportamento.

---

# 20. Segurança e Privacidade

O domínio pode manipular dados institucionais e parâmetros sensíveis.

Deve seguir:

- GSF;
- menor privilégio;
- isolamento multi-tenant;
- proteção de dados;
- auditoria.

Segredos técnicos, credenciais e chaves privadas não devem ser tratados como configuração funcional comum.

Esses itens pertencem à gestão segura de segredos e infraestrutura.

---

# 21. Testes e Qualidade

Devem ser testados:

- override local;
- fallback ministerial;
- ausência de configuração;
- troca de fonte;
- isolamento por igreja;
- alteração de parâmetros;
- recorrência;
- conflitos com EBD;
- permissões;
- cache por tenant;
- propagação de mudanças.

Testes específicos permanecem no GQF e na documentação técnica correspondente.

---

# 22. Compatibilidade e Rollout

A evolução da EBD documenta uma estratégia segura de rollout:

- adicionar campos locais;
- realizar backfill;
- manter configuração ministerial;
- priorizar local quando preenchido;
- permitir migração gradual.

Esse padrão é preferível a uma quebra abrupta quando a plataforma muda de configuração global para local.

---

# 23. Limites do Domínio

Não pertencem automaticamente a Configurações:

- regras de negócio de Financeiro;
- autorização de Usuários;
- calendário interno da EBD;
- ciclo de vida de Eventos;
- segredos de infraestrutura;
- variáveis de ambiente;
- configurações de deploy;
- feature flags sem relação funcional clara.

O domínio deve evitar se tornar um repositório genérico de qualquer parâmetro do sistema.

---

# 24. Pontos a Validar

A auditoria não encontrou uma especificação funcional única e completa de Configurações.

Antes de ampliar este documento, devem ser validados no código atual:

1. todas as seções da tela de edição da igreja;
2. quais parâmetros ainda permanecem apenas ministeriais;
3. quais possuem override local;
4. política de Programações padrão atual;
5. conta padrão de eventos;
6. configurações de departamentos;
7. catálogos mantidos pelo app;
8. permissões por seção;
9. auditoria de alterações;
10. regras de exclusão ou desativação de configurações;
11. feature flags mantidas neste app, se houver;
12. quais caches dependem das configurações.

---

# 25. Documentos Relacionados

- `docs/apps/README.md`
- `docs/apps/03-Financeiro.md`
- `docs/apps/05-Departamentos.md`
- `docs/apps/06-EBD.md`
- `docs/apps/07-Eventos.md`
- `docs/apps/09-Usuarios.md`
- `docs/sistema/ESCOLA_DOMINICAL_CONFIG_LOCAL_IGREJA.md`
- `docs/sistema/ESCOLA_DOMINICAL_GOVERNANCA_PERIODO.md`
- `docs/usuario/README_IGREJA_USER.md`
- `docs/seguranca/05-Seguranca-Multi-Tenant.md`
- `docs/backend/README.md`

---

# 26. Princípios Finais

Configuração deve responder sempre:

```text
Quem define?
Para qual escopo?
Qual valor está vigente?
Existe fallback?
Quem pode alterar?
Quais módulos serão afetados?
```

Se essas respostas não estiverem claras, a configuração não está suficientemente governada.

---

# 27. Status

**Pasta:** `docs/apps/`

**Arquivo:** `10-Configuracoes.md`

**Documento:** `APP-10`

**Versão:** `1.0`

**Status:** **OFICIAL**

A lacuna documental foi confirmada em `docs/apps/`.

Este documento consolida as regras funcionais comprovadas de Configurações, preservando como pendentes os pontos que ainda exigem validação contra o código atual.
