# 10 - Padrões de Permissões

> "Autenticar identifica o usuário. Autorizar define o que ele pode fazer."

---

# Sumário

1. Objetivo
2. Filosofia das Permissões
3. Princípios Gerais
4. Arquitetura das Permissões
5. Organização dos Arquivos
6. Tipos de Permissões
7. Permissões por Módulo
8. Permissões nas Views
9. Permissões nos Templates
10. Permissões no Django Admin
11. Auditoria
12. Segurança
13. Performance
14. Testes
15. Checklist
16. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para implementação das permissões do GereIgreja.

Seu objetivo é garantir que todas as operações da plataforma respeitem regras consistentes de autorização, protegendo dados, funcionalidades e recursos do sistema.

Toda funcionalidade deverá seguir estes padrões.

---

# 2. Filosofia das Permissões

A autenticação responde:

> Quem é o usuário?

A autorização responde:

> O que este usuário pode fazer?

Esses dois conceitos deverão permanecer separados.

Nenhuma funcionalidade deverá confiar apenas na interface para restringir acesso.

Toda autorização deverá ocorrer no servidor.

---

# 3. Princípios Gerais

O sistema de permissões deverá seguir os seguintes princípios:

- menor privilégio possível;
- responsabilidade única;
- reutilização;
- previsibilidade;
- segurança;
- facilidade de auditoria.

Permissões deverão ser concedidas explicitamente.

Nunca implicitamente.

---

# 4. Arquitetura das Permissões

A arquitetura oficial deverá seguir o fluxo:

```text
Usuário

↓

Autenticação

↓

Permissão

↓

View

↓

Service

↓

Resposta
```

Nenhuma operação crítica deverá ignorar esta etapa.

---

# 5. Organização dos Arquivos

Cada módulo poderá possuir seu próprio arquivo:

```text
permissions.py
```

Quando necessário:

```text
permissions/

├── __init__.py
├── membros.py
├── financeiro.py
├── eventos.py
└── administrativos.py
```

As permissões deverão permanecer organizadas por domínio.

---

# 6. Tipos de Permissões

O GereIgreja poderá utilizar diferentes níveis de autorização.

Exemplos:

- visualizar;
- criar;
- editar;
- excluir;
- exportar;
- importar;
- aprovar;
- administrar.

Esses níveis deverão permanecer consistentes em todos os módulos.

---

# 7. Permissões por Módulo

Cada módulo deverá definir claramente suas regras.

Exemplo:

Financeiro

- visualizar lançamentos;
- criar lançamentos;
- editar lançamentos;
- excluir lançamentos;
- fechar caixa.

Secretaria

- visualizar membros;
- cadastrar membros;
- editar membros;
- excluir membros.

Cada domínio deverá controlar apenas suas próprias permissões.

---

# 8. Permissões nas Views

Toda View deverá validar permissões antes de executar operações.

Preferencialmente utilizar:

- LoginRequiredMixin;
- PermissionRequiredMixin;
- UserPassesTestMixin;
- decorators oficiais.

Nunca depender apenas da navegação da interface.

---

# 9. Permissões nos Templates

Os Templates poderão ocultar funcionalidades não autorizadas.

Exemplo:

```django
{% if perms.financeiro.add_lancamento %}
```

Entretanto, isso representa apenas uma melhoria na experiência do usuário.

A validação definitiva continuará sendo responsabilidade da View.

---

# 10. Permissões no Django Admin

O Django Admin deverá respeitar integralmente o sistema oficial de permissões.

Cada ModelAdmin deverá restringir:

- visualização;
- inclusão;
- alteração;
- exclusão;
- ações administrativas.

O Admin jamais deverá ignorar as regras da plataforma.

---

# 11. Auditoria

Toda operação crítica deverá ser registrada.

Exemplos:

- alteração de permissões;
- criação de usuários;
- exclusão de registros;
- acesso administrativo;
- mudanças de configuração.

Esses registros fortalecem a rastreabilidade da plataforma.

---

# 12. Segurança

Boas práticas:

- nunca confiar em parâmetros enviados pelo navegador;
- validar permissões em todas as operações críticas;
- evitar privilégios excessivos;
- revisar permissões periodicamente;
- registrar eventos relevantes.

A segurança deverá ser considerada em todas as etapas do desenvolvimento.

---

# 13. Performance

As verificações de permissão deverão ser eficientes.

Sempre que possível:

- reutilizar consultas;
- evitar verificações duplicadas;
- utilizar cache quando apropriado;
- centralizar regras reutilizáveis.

Segurança não deverá comprometer desnecessariamente o desempenho.

---

# 14. Testes

Toda regra de autorização deverá possuir testes.

Priorizar:

- usuários autorizados;
- usuários sem permissão;
- acesso anônimo;
- operações proibidas;
- mensagens de erro.

Os testes garantem que futuras alterações não comprometam a segurança.

---

# 15. Checklist

Antes da publicação verificar:

- permissões implementadas;
- Views protegidas;
- Admin protegido;
- Templates revisados;
- auditoria prevista;
- documentação atualizada;
- testes implementados.

---

# 16. Princípios Finais

As permissões representam um dos pilares da segurança do GereIgreja.

Uma arquitetura consistente de autorização protege os dados das igrejas, fortalece a confiabilidade da plataforma e reduz riscos operacionais.

Toda nova funcionalidade deverá respeitar os padrões definidos pela GereIgreja Engineering Architecture (GEA).