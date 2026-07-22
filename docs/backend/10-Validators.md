Pasta:
docs/backend/

Arquivo:
10-Validators.md

Documento:
GBE-10

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

# 10 - Validators

> *"Validar dados não é apenas impedir erros; é garantir que as regras de negócio sejam respeitadas antes que elas alcancem o domínio da aplicação."*

---

# Sumário

1. Objetivo
2. Filosofia dos Validators
3. O Papel dos Validators no GereIgreja
4. Fluxo Oficial de Validação
5. Tipos de Validators
6. Organização dos Validators
7. Validators Reutilizáveis
8. Validators de Domínio
9. Integração com Forms
10. Integração com Models
11. Integração com Services
12. Integração com APIs e Serializers
13. Boas Práticas
14. Anti-patterns
15. Checklist
16. Documentos Relacionados
17. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para criação, organização e utilização de Validators no Backend do GereIgreja.

Seu propósito é garantir que todas as validações sejam consistentes, reutilizáveis e centralizadas, reduzindo duplicação de código e aumentando a confiabilidade da plataforma.

---

# 2. Filosofia dos Validators

No GereIgreja, um Validator possui uma única responsabilidade:

**validar dados**.

Ele não deve:

- salvar informações;
- alterar registros;
- enviar e-mails;
- realizar consultas complexas;
- executar regras de negócio completas.

Essas responsabilidades pertencem a outras camadas da arquitetura.

Um Validator responde apenas à pergunta:

> "Este dado é válido para prosseguir?"

---

# 3. O Papel dos Validators no GereIgreja

Os Validators atuam como uma barreira de proteção antes que os dados avancem para as camadas de negócio.

Eles são utilizados para:

- validar formatos;
- verificar consistência;
- garantir integridade dos dados;
- impedir entradas inválidas;
- padronizar regras reutilizáveis.

Sempre que possível, uma regra de validação deve existir em apenas um lugar.

---

# 4. Fluxo Oficial de Validação

Todo dado recebido deverá seguir um fluxo semelhante ao seguinte:

```text
Usuário
    │
    ▼
Form / Serializer
    │
    ▼
Validator
    │
    ▼
Service
    │
    ▼
Model
    │
    ▼
Banco de Dados
```

Os Validators atuam antes da execução das regras de negócio.

---

# 5. Tipos de Validators

O GereIgreja adota quatro categorias principais.

## Validators de Formato

Responsáveis por validar:

- CPF;
- CNPJ;
- CEP;
- telefone;
- e-mail;
- datas;
- documentos.

---

## Validators de Consistência

Validam relações entre informações.

Exemplos:

- data inicial menor que data final;
- idade mínima;
- duplicidade.

---

## Validators de Domínio

Representam regras específicas do negócio.

Exemplos:

- membro não pode ser batizado duas vezes;
- tesoureiro precisa possuir permissão adequada;
- congregação deve pertencer ao ministério ativo.

---

## Validators de Infraestrutura

Relacionados ao ambiente técnico.

Exemplos:

- tamanho máximo de upload;
- tipo de arquivo permitido;
- extensão válida;
- formato de imagem.

---

# 6. Organização dos Validators

Sempre que houver quantidade significativa de validações reutilizáveis, criar uma estrutura dedicada.

Exemplo:

```text
validators/

__init__.py

cpf.py

cnpj.py

telefone.py

arquivo.py

financeiro.py

membros.py
```

Validators pequenos podem permanecer próximos ao domínio ao qual pertencem.

---

# 7. Validators Reutilizáveis

Uma validação utilizada em mais de um módulo deve ser reutilizada.

Nunca copiar código entre aplicações.

Criar um Validator compartilhado reduz manutenção e evita divergências.

---

# 8. Validators de Domínio

Nem toda regra deve ser um Validator.

Utilize Validators apenas quando a responsabilidade for validar um dado.

Quando houver processamento, decisões ou efeitos colaterais, a implementação deverá permanecer nos Services.

---

# 9. Integração com Forms

Forms são responsáveis pela interação com o usuário.

Validators são responsáveis pelas validações reutilizáveis.

Os Forms devem delegar validações complexas aos Validators sempre que possível.

---

# 10. Integração com Models

Os Models podem utilizar Validators para proteger campos específicos.

Entretanto, regras de negócio completas não devem ser implementadas diretamente nos Models.

---

# 11. Integração com Services

Services presumem que os dados já passaram pelas validações básicas.

Quando necessário, podem executar validações adicionais relacionadas ao fluxo de negócio.

Validators e Services são complementares, nunca concorrentes.

---

# 12. Integração com APIs e Serializers

Serializers devem reutilizar Validators existentes.

Evitar duplicação entre:

- Forms;
- APIs;
- Painel Administrativo.

A mesma regra deve produzir o mesmo comportamento em qualquer interface.

---

# 13. Boas Práticas

- responsabilidade única;
- reutilização;
- mensagens claras;
- baixo acoplamento;
- independência de interface;
- testes automatizados;
- documentação das validações críticas.

---

# 14. Anti-patterns

Evitar:

- consultas pesadas dentro de Validators;
- acesso direto à interface;
- gravação no banco;
- envio de notificações;
- dependência entre Validators;
- duplicação de lógica.

Validators não substituem Services.

---

# 15. Checklist

Antes de criar um Validator verificar:

- realmente é uma validação?
- poderá ser reutilizado?
- está independente da interface?
- possui responsabilidade única?
- evita duplicação?
- está documentado?
- possui testes previstos?

---

# 16. Documentos Relacionados

- GBE-04 — Models
- GBE-05 — Services
- GBE-08 — Views
- GBE-09 — Forms
- GEA-03 — Arquitetura do Backend
- GQF — GereIgreja Quality Framework

---

# 17. Princípios Finais

Validators representam a primeira linha de defesa da qualidade dos dados do GereIgreja.

Eles devem permanecer simples, reutilizáveis e previsíveis, garantindo que informações inválidas sejam bloqueadas antes de alcançar o domínio da aplicação.

Uma validação consistente reduz erros, melhora a experiência do usuário e fortalece toda a arquitetura do sistema.

---

## ✅ Status

**Pasta:** `docs/backend/`

**Arquivo:** `10-Validators.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento estabelece o padrão oficial para implementação e utilização de Validators no Backend do GereIgreja.

