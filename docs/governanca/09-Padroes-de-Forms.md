# 09 - Padrões de Forms

> "Os Forms são a primeira linha de defesa da integridade dos dados da plataforma."

---

# Sumário

1. Objetivo
2. Filosofia dos Forms
3. Responsabilidades
4. Organização dos Arquivos
5. ModelForms
6. Forms Comuns
7. Validações
8. Layout e Experiência do Usuário
9. Integração com Services
10. Segurança
11. Mensagens de Erro
12. Performance
13. Testes
14. Checklist
15. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para desenvolvimento dos Forms do GereIgreja.

Seu objetivo é garantir consistência, reutilização, validação adequada dos dados e integração harmoniosa com a arquitetura da plataforma.

Todos os formulários deverão seguir estas diretrizes.

---

# 2. Filosofia dos Forms

Os Forms representam a camada responsável pela entrada de dados do usuário.

Seu papel é validar informações antes que elas sejam processadas pelas regras de negócio.

Os Forms não deverão implementar lógica de negócio.

Toda regra complexa deverá permanecer nos Services.

---

# 3. Responsabilidades

Um Form poderá ser responsável por:

- validar dados;
- normalizar informações;
- exibir mensagens de erro;
- preparar dados para processamento;
- definir widgets e atributos visuais.

Um Form não deverá:

- alterar múltiplos modelos;
- executar integrações externas;
- implementar regras de negócio;
- realizar consultas complexas.

---

# 4. Organização dos Arquivos

Cada módulo deverá possuir seu próprio arquivo `forms.py`.

Quando houver grande quantidade de formulários, recomenda-se utilizar um pacote.

Exemplo:

```text
forms/

├── __init__.py
├── membros.py
├── financeiro.py
├── eventos.py
├── filtros.py
└── compartilhados.py
```

A organização deverá acompanhar o crescimento do módulo.

---

# 5. ModelForms

Sempre que houver correspondência direta entre um formulário e um Model, deverá ser utilizado `ModelForm`.

Exemplo:

```python
class MembroForm(forms.ModelForm):
    ...
```

O uso de `ModelForm` reduz duplicação e facilita manutenção.

---

# 6. Forms Comuns

Forms independentes poderão ser utilizados para:

- filtros;
- pesquisas;
- login;
- recuperação de senha;
- importações;
- exportações;
- configurações temporárias.

Esses formulários não precisam estar vinculados a um Model.

---

# 7. Validações

Toda validação deverá ocorrer no menor nível possível.

Prioridade recomendada:

1. Validações nativas do Django;
2. Validators reutilizáveis;
3. Métodos `clean_<campo>()`;
4. Método `clean()`;
5. Services (quando envolver regra de negócio).

Evitar duplicação de validações.

---

# 8. Layout e Experiência do Usuário

Os Forms deverão seguir integralmente o GereIgreja Design System (GDS).

Boas práticas:

- labels claras;
- campos agrupados;
- ajuda contextual;
- destaque para campos obrigatórios;
- mensagens objetivas;
- foco automático quando apropriado.

A experiência do usuário deverá ser consistente em toda a plataforma.

---

# 9. Integração com Services

Após a validação, os dados deverão ser encaminhados para os Services responsáveis pelo processamento.

Fluxo recomendado:

```text
Usuário
   │
   ▼
Form
   │
   ▼
Service
   │
   ▼
Model
```

Essa separação facilita testes e manutenção.

---

# 10. Segurança

Nunca confiar exclusivamente nas validações do navegador.

Toda informação deverá ser validada novamente no servidor.

Sempre considerar:

- permissões;
- autenticação;
- proteção contra CSRF;
- sanitização de dados;
- validação de arquivos enviados.

---

# 11. Mensagens de Erro

As mensagens deverão ser:

- claras;
- objetivas;
- amigáveis;
- consistentes.

Evitar mensagens técnicas voltadas ao usuário final.

Exemplo inadequado:

> IntegrityError.

Exemplo recomendado:

> Já existe um membro cadastrado com este CPF.

---

# 12. Performance

Os Forms deverão evitar:

- consultas repetidas;
- carregamento desnecessário de opções;
- processamento pesado durante a validação.

Quando necessário, utilizar carregamento assíncrono ou campos com autocomplete.

---

# 13. Testes

Os Forms críticos deverão possuir testes automatizados.

Priorizar:

- validações obrigatórias;
- mensagens de erro;
- campos opcionais;
- regras de limpeza (`clean`);
- comportamento em casos inválidos.

---

# 14. Checklist

Antes da publicação verificar:

- Form organizado;
- validações implementadas;
- integração com Services;
- mensagens revisadas;
- GDS aplicado;
- segurança validada;
- documentação atualizada;
- testes previstos.

---

# 15. Princípios Finais

Os Forms representam a porta de entrada dos dados na plataforma.

Sua responsabilidade é garantir que apenas informações válidas e consistentes avancem para as demais camadas da arquitetura.

Um Form bem estruturado reduz erros, melhora a experiência do usuário e fortalece a qualidade geral do GereIgreja.

Todo novo formulário deverá seguir os padrões definidos pela GereIgreja Engineering Architecture (GEA).