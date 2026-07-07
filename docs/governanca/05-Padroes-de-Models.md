# 05 - Padrões de Models

> "Os Models representam o coração do GereIgreja. Toda regra estrutural da plataforma nasce deles."

---

# Sumário

1. Objetivo
2. Filosofia dos Models
3. Responsabilidade dos Models
4. Estrutura dos Models
5. Campos
6. Meta
7. Managers
8. Métodos
9. Relacionamentos
10. Auditoria
11. Soft Delete
12. Performance
13. Segurança
14. Documentação
15. Checklist
16. Princípios Finais

# 1. Objetivo

Este documento estabelece os padrões oficiais para criação e manutenção dos Models do GereIgreja.

Seu objetivo é garantir consistência estrutural, facilidade de manutenção e evolução sustentável da plataforma.

Todo Model desenvolvido deverá seguir as diretrizes aqui definidas.

---
# 2. Filosofia dos Models

Os Models representam as entidades centrais do domínio da aplicação.

Eles descrevem a estrutura dos dados e comportamentos diretamente relacionados à própria entidade.

Os Models não deverão concentrar regras complexas de negócio.

Essas responsabilidades pertencem aos Services.

Os Models deverão permanecer simples, claros e reutilizáveis.

---
# 3. Responsabilidade dos Models

Um Model deverá ser responsável apenas por:

- representar uma entidade;
- definir seus campos;
- manter relacionamentos;
- encapsular pequenos comportamentos da própria entidade;
- fornecer propriedades úteis.

Operações complexas deverão permanecer fora do Model.


# 4. Estrutura dos Models

Todos os Models deverão seguir uma estrutura organizada.

Ordem recomendada:

- Classe Meta
- Managers
- Campos
- Propriedades
- Métodos públicos
- Métodos privados
- __str__()
- get_absolute_url() (quando aplicável)

Essa organização facilita leitura e manutenção.

---
# 5. Campos

Os campos deverão possuir nomes claros e objetivos.

Boas práticas:

- evitar abreviações;
- utilizar verbose_name quando necessário;
- utilizar help_text para facilitar administração;
- definir valores padrão conscientemente;
- utilizar choices quando fizer sentido.

Todo campo deverá possuir um propósito claro.

---
# 6. Classe Meta

Sempre que necessário utilizar:

- ordering
- indexes
- constraints
- verbose_name
- verbose_name_plural

A Classe Meta deverá concentrar configurações estruturais do Model.


# 7. Managers

Consultas reutilizáveis deverão permanecer em Managers personalizados.

Exemplo:

MembroManager

EventoManager

FinanceiroManager

Managers reduzem duplicação de consultas.

---
# 8. Métodos

Os métodos do Model deverão representar comportamentos da própria entidade.

Exemplos:

membro.nome_completo()

evento.esta_encerrado()

igreja.total_membros()

Métodos que executam processos complexos deverão ser movidos para Services.

---
# 9. Relacionamentos

Relacionamentos deverão refletir o domínio da aplicação.

Sempre avaliar cuidadosamente:

- ForeignKey
- OneToOne
- ManyToMany

Evitar relacionamentos desnecessários.

Utilizar related_name padronizado sempre que possível.


# 10. Auditoria

Sempre que necessário registrar:

- data de criação;
- data de alteração;
- usuário responsável;
- histórico de alterações.

A auditoria faz parte da arquitetura da plataforma.

---
# 11. Soft Delete

Sempre que apropriado utilizar exclusão lógica.

A remoção física de registros deverá ocorrer apenas quando realmente necessária.

---


# 12. Performance

Os Models deverão ser projetados pensando em escalabilidade.

Boas práticas:

- índices;
- constraints;
- normalização;
- consultas otimizadas;
- uso consciente de relacionamentos.

Performance começa na modelagem.


# 13. Segurança

Os Models deverão proteger a integridade dos dados.

Sempre validar:

- consistência;
- restrições;
- relacionamentos;
- unicidade;
- permissões.

---
# 14. Documentação

Models importantes deverão possuir documentação adequada.

A documentação facilita manutenção e reduz curva de aprendizado para novos desenvolvedores.

---


# 15. Checklist

Antes de concluir um novo Model verificar:

- responsabilidade bem definida;
- campos padronizados;
- relacionamentos corretos;
- índices avaliados;
- constraints implementadas;
- Manager criado quando necessário;
- documentação atualizada;
- testes previstos.

---
# 16. Princípios Finais

Os Models representam a base estrutural do GereIgreja.

Toda modelagem deverá priorizar clareza, simplicidade, consistência e evolução contínua.

Um bom Model facilita todo o restante da arquitetura da plataforma.
