# 📚 Documentação Oficial do GereIgreja

> "A documentação é a memória viva da plataforma."

---

# Bem-vindo

Esta pasta reúne toda a documentação oficial do GereIgreja.

Ela foi organizada para servir como base de conhecimento da plataforma, apoiando desenvolvedores, administradores, colaboradores e futuros mantenedores.

Toda decisão importante da engenharia deverá possuir documentação correspondente.

---

# Objetivos

A documentação possui cinco objetivos principais.

- Preservar conhecimento.
- Padronizar processos.
- Facilitar manutenção.
- Apoiar novos colaboradores.
- Sustentar a evolução da plataforma.

---

# Estrutura da Documentação

A documentação está organizada por áreas de conhecimento.

```text
docs/

README.md

INDEX.md

arquitetura/

backend/

frontend/

apps/

frameworks/

operacoes/

qualidade/

api/

seo/

marketing/

deploy/

contribuicao/

adr/
```

## Estrutura Definitiva (Regra de Governança)

A organização oficial de `docs/` passa a seguir esta regra:

- `docs/backend/`: padrões de engenharia (como construir);
- `docs/apps/`: catálogo por módulo (o que existe em cada app);
- `docs/arquitetura/`: decisões e visão sistêmica;
- `docs/operacoes/`: execução operacional e runbooks;
- `docs/qualidade/`: critérios, gates e checklists de validação.

Princípio obrigatório: documentos de `docs/apps/` não duplicam conteúdo normativo de `docs/backend/`; apenas referenciam os padrões quando necessário.

## Regra de Leitura (Obrigatória)

Backend
↓
Como construir.

Apps
↓
O que foi construído.

INDEX
↓
O mapa.

README
↓
A apresentação.

---

# Ordem Recomendada de Leitura

Para novos colaboradores recomendamos a seguinte sequência.

1. README Principal do Projeto

2. docs/README.md

3. docs/arquitetura/README.md

4. docs/backend/README.md

5. docs/apps/README.md

6. docs/operacoes/README.md

7. docs/qualidade/README.md

---

# Frameworks da Plataforma

A engenharia do GereIgreja utiliza frameworks conceituais próprios.

• GEA — GereIgreja Engineering Architecture

• GDS — GereIgreja Design System

• GAF — GereIgreja Authorization Framework

• GSF — GereIgreja Security Framework

• GQF — GereIgreja Quality Framework

• GOC — GereIgreja Operations Center

---

# Como Navegar

Cada pasta possui um README próprio explicando seu objetivo.

O arquivo INDEX.md contém a relação completa de todos os documentos existentes.

---

# Filosofia

Código muda.

Tecnologias evoluem.

Ferramentas são substituídas.

Mas conhecimento preservado continua gerando valor.

Por isso a documentação faz parte do software.

---

# Conclusão

Toda funcionalidade importante deverá possuir documentação.

Código e documentação evoluem juntos.

A documentação oficial do GereIgreja representa a fonte única de conhecimento da plataforma.