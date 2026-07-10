Pasta:
docs/backend/

Arquivo:
09-Forms.md

Documento:
GBE-09

Seção:
Backend

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 09 - Forms

> "Um formulário deve coletar dados. A inteligência para processá-los pertence aos Services."

---

# Sumário

1. Objetivo
2. Filosofia dos Forms
3. Papel dos Forms na Arquitetura
4. Responsabilidades
5. O que NÃO pertence aos Forms
6. Estrutura Oficial
7. Organização dos Forms
8. Form vs ModelForm
9. Comunicação com Views
10. Comunicação com Services
11. Comunicação com Models
12. Comunicação com Templates
13. Boas Práticas
14. Documentos Relacionados
15. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para criação e utilização de Forms no GereIgreja.

Seu objetivo é garantir formulários consistentes, reutilizáveis, seguros e totalmente integrados à arquitetura oficial da plataforma.

Os Forms deverão ser responsáveis apenas pela entrada e validação estrutural dos dados.

---

# 2. Filosofia dos Forms

Os Forms representam a camada responsável por receber informações fornecidas pelo usuário.

Eles não executam regras de negócio.

Eles não realizam integrações.

Eles não modificam diretamente o domínio da aplicação.

No GereIgreja seguimos o seguinte princípio:

> **Forms validam dados. Services executam operações.**

Essa separação reduz acoplamento e facilita testes.

---

# 3. Papel dos Forms na Arquitetura

Fluxo oficial:

```text
Usuário

↓

Template

↓

Form

↓

View

↓

Service

↓

Selector

↓

Model

↓

Banco de Dados
```

O Form atua como intermediário entre a interface e a camada de serviços.

---

# 4. Responsabilidades

Os Forms poderão ser responsáveis por:

- receber dados do usuário;
- validar tipos;
- validar formatos;
- validar obrigatoriedade;
- normalizar entradas;
- converter tipos;
- apresentar mensagens de erro;
- disponibilizar dados limpos através de `cleaned_data`.

---

# 5. O que NÃO pertence aos Forms

Os Forms não deverão conter:

- regras de negócio;
- gravação direta em Models;
- cálculos financeiros;
- envio de e-mails;
- integrações externas;
- auditoria;
- geração de arquivos;
- consultas complexas;
- controle de permissões.

Essas responsabilidades pertencem às camadas apropriadas.

---

# 6. Estrutura Oficial

Cada App deverá possuir seu próprio diretório de Forms.

Exemplo:

```text
forms/

__init__.py

membro_form.py

familia_form.py

evento_form.py

financeiro_form.py

filtros.py

importacao.py
```

Cada arquivo deverá representar um domínio específico.

---

# 7. Organização dos Forms

Separar os formulários por finalidade.

Exemplo:

```text
forms/

cadastro/

filtros/

importacao/

relatorios/

configuracoes/
```

Essa organização facilita manutenção à medida que o sistema cresce.

---

# 8. Form vs ModelForm

Preferencialmente utilizar:

### Form

Quando:

- não houver Model correspondente;
- houver múltiplos Models envolvidos;
- tratar filtros;
- login;
- autenticação;
- pesquisas;
- importações.

---

### ModelForm

Utilizar quando representar diretamente um único Model.

Mesmo utilizando ModelForm, a gravação deverá ocorrer preferencialmente através dos Services quando existirem regras de negócio.

---

# 9. Comunicação com Views

As Views deverão instanciar e validar os Forms.

Exemplo:

```python
form = MembroForm(request.POST)

if form.is_valid():

    MembroService.criar(
        igreja=request.igreja,
        dados=form.cleaned_data,
        usuario=request.user
    )
```

A View coordena.

O Form valida.

O Service executa.

---

# 10. Comunicação com Services

Os Services deverão receber apenas dados já validados.

Exemplo:

```python
MembroService.criar(
    dados=form.cleaned_data
)
```

Isso reduz duplicação de validações.

---

# 11. Comunicação com Models

Forms não deverão alterar Models diretamente quando houver lógica de negócio.

Evitar:

```python
form.save()
```

Preferir:

```python
MembroService.criar(
    dados=form.cleaned_data
)
```

Essa abordagem centraliza a lógica da aplicação.

---

# 12. Comunicação com Templates

Os Templates deverão utilizar os Forms para renderização dos campos.

A apresentação visual deverá seguir o GereIgreja Design System (GDS).

Os Templates não deverão conter lógica de validação.

---

# 13. Boas Práticas

Os Forms deverão:

- possuir responsabilidade única;
- ser reutilizáveis;
- possuir nomes descritivos;
- apresentar mensagens claras;
- validar apenas estrutura dos dados;
- utilizar widgets padronizados.

---

# 14. Documentos Relacionados

- GBE-08 — Views
- GBE-10 — Validators
- GBE-05 — Services
- GDS — GereIgreja Design System
- GQF — Framework de Qualidade

---

# 15. Princípios Finais

Os Forms representam a camada oficial de entrada de dados do GereIgreja.

Sua missão é garantir que informações recebidas estejam corretamente estruturadas antes de serem processadas pelos Services.

Ao limitar suas responsabilidades à validação estrutural e apresentação de erros, preservamos uma arquitetura limpa, reutilizável e preparada para crescer.

