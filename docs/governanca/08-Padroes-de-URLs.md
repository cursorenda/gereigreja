# 08 - Padrões de URLs

> "Uma URL bem construída é parte da experiência do usuário e da arquitetura da aplicação."

---

# Sumário

1. Objetivo
2. Filosofia das URLs
3. Estrutura das Rotas
4. Convenções de Nomenclatura
5. Organização dos Arquivos
6. Versionamento
7. Namespaces
8. URLs Públicas
9. URLs Administrativas
10. URLs de API
11. SEO e URLs
12. Segurança
13. Checklist
14. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para criação e organização das URLs do GereIgreja.

Seu objetivo é garantir consistência, legibilidade, facilidade de manutenção e compatibilidade com as boas práticas do Django e de SEO.

Todas as rotas da plataforma deverão seguir estas diretrizes.

---

# 2. Filosofia das URLs

As URLs representam a porta de entrada da aplicação.

Uma boa URL deve ser:

- simples;
- previsível;
- legível;
- estável;
- orientada ao domínio.

O usuário deve conseguir compreender o conteúdo de uma página apenas observando sua URL.

---

# 3. Estrutura das Rotas

Cada módulo deverá possuir seu próprio arquivo `urls.py`.

Exemplo:

```text
apps/

├── membros/
│   └── urls.py
├── financeiro/
│   └── urls.py
├── eventos/
│   └── urls.py
└── blog/
    └── urls.py
```

O arquivo principal de URLs deverá apenas incluir as rotas dos módulos.

---

# 4. Convenções de Nomenclatura

As URLs deverão utilizar:

- letras minúsculas;
- palavras separadas por hífen quando necessário;
- nomes descritivos;
- caminhos curtos.

Exemplos:

```text
/membros/

/membros/novo/

/membros/123/

/financeiro/lancamentos/

/eventos/calendario/

/blog/
```

Evitar:

- abreviações;
- nomes técnicos;
- parâmetros desnecessários.

---

# 5. Organização dos Arquivos

Cada módulo deverá centralizar suas rotas.

Exemplo:

```python
app_name = "membros"

urlpatterns = [
    ...
]
```

A utilização de `app_name` será obrigatória para permitir namespaces.

---

# 6. Versionamento

As URLs da aplicação principal não deverão ser alteradas sem necessidade.

Quando houver APIs públicas, utilizar versionamento.

Exemplo:

```text
/api/v1/

/api/v2/
```

O versionamento evita quebra de compatibilidade.

---

# 7. Namespaces

Todos os módulos deverão utilizar namespaces.

Exemplo:

```python
app_name = "financeiro"
```

Chamadas deverão utilizar:

```python
reverse("financeiro:listar")
```

ou

```django
{% url 'financeiro:listar' %}
```

Isso evita conflitos entre módulos.

---

# 8. URLs Públicas

As páginas públicas deverão possuir URLs amigáveis.

Exemplos:

```text
/blog/

/blog/como-organizar-o-caixa-da-igreja/

/funcionalidades/

/planos/

/contato/
```

Sempre priorizar URLs compreensíveis para usuários e mecanismos de busca.

---

# 9. URLs Administrativas

As rotas administrativas deverão permanecer separadas das rotas públicas.

Exemplos:

```text
/dashboard/

/painel/

/admin/
```

A organização deverá facilitar a navegação e reforçar a segurança.

---

# 10. URLs de API

As APIs deverão seguir padrão REST.

Exemplos:

```text
GET    /api/v1/membros/

POST   /api/v1/membros/

PUT    /api/v1/membros/15/

DELETE /api/v1/membros/15/
```

As URLs não deverão conter verbos.

As ações são definidas pelo método HTTP.

---

# 11. SEO e URLs

As URLs públicas deverão seguir as diretrizes definidas na documentação de SEO do GereIgreja.

Boas práticas:

- URLs permanentes;
- sem parâmetros desnecessários;
- uso de slug;
- palavras-chave relevantes;
- sem caracteres especiais.

Evitar URLs como:

```text
/post?id=25
```

Preferir:

```text
/blog/como-fazer-prestacao-de-contas-na-igreja/
```

---

# 12. Segurança

Nunca expor informações sensíveis na URL.

Evitar:

- tokens;
- senhas;
- informações pessoais;
- dados internos da plataforma.

Toda validação deverá ocorrer na View e nas permissões.

---

# 13. Checklist

Antes da publicação verificar:

- URL organizada;
- namespace definido;
- nome consistente;
- SEO considerado;
- permissões implementadas;
- documentação atualizada;
- testes previstos.

---

# 14. Princípios Finais

As URLs representam parte da arquitetura da plataforma.

Elas devem permanecer simples, previsíveis e consistentes.

Uma estrutura de URLs bem planejada melhora a experiência do usuário, facilita a manutenção do código e contribui para a qualidade do SEO.

Toda nova rota deverá seguir os padrões definidos pela GereIgreja Engineering Architecture (GEA).