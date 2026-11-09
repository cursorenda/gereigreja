# Usuário — Manuais e Guias para Uso do GereIgreja

Usuário  
↓  
Como pessoas usuárias utilizam o GereIgreja no dia a dia.

Esta pasta reúne documentação orientada ao uso da plataforma.

Ela não documenta arquitetura, implementação interna nem regras técnicas de engenharia.

A finalidade é explicar jornadas, telas, rotinas e procedimentos do ponto de vista de quem usa o sistema.

## Finalidade da pasta

- manter manuais de uso;
- organizar guias operacionais por perfil;
- registrar tutoriais e instruções práticas;
- manter documentação sobre planos, assinatura e acesso quando destinada ao usuário final;
- preservar materiais históricos de novidades quando ainda forem úteis;
- separar orientação de uso da especificação técnica dos módulos.

## Fronteira com outras famílias

### `docs/apps/`

Define o comportamento funcional canônico dos módulos.

Exemplos:

```text
apps/06-EBD.md
→ o que a EBD faz

usuario/GUIA_OPERACIONAL_EBD.md
→ como secretaria, professor e liderança usam a EBD
```

### `docs/desenvolvimento/`

É voltada a desenvolvedores.

### `docs/operacoes/`

Contém runbooks técnicos e operacionais de serviço.

Um guia para usuário final não é runbook técnico.

### `docs/release-notes/`

Registra mudanças por versão.

Arquivos de “melhorias para usuários” podem ter valor histórico, mas não devem substituir release notes oficiais.

## Índice atual

| Documento | Natureza | Situação |
|---|---|---|
| [USUARIO_MANUAL.md](USUARIO_MANUAL.md) | Manual geral de uso | Manter e atualizar |
| [GUIA_OPERACIONAL_EBD.md](GUIA_OPERACIONAL_EBD.md) | Guia de uso da EBD por perfil | Manter |
| [MANUAL_ASSINATURA_PLANOS.md](MANUAL_ASSINATURA_PLANOS.md) | Manual de assinatura e planos | Manter, sujeito à revisão funcional |
| [README_IGREJA_USER.md](README_IGREJA_USER.md) | Guia histórico específico | Revisar classificação |
| [MELHORIAS_USUARIOS_v1.7.2.md](MELHORIAS_USUARIOS_v1.7.2.md) | Histórico de melhorias | Revisar / possível release-notes |
| [MELHORIAS_USUARIOS_v1.8.0_a_v1.8.67.md](MELHORIAS_USUARIOS_v1.8.0_a_v1.8.67.md) | Histórico consolidado de melhorias | Revisar / possível release-notes |
| [MELHORIAS_USUARIOS_v1.8.75.md](MELHORIAS_USUARIOS_v1.8.75.md) | Histórico de melhorias | Revisar / possível release-notes |
| [chat_respostas.md](chat_respostas.md) | Histórico de respostas/conversas | Reclassificar ou remover após revisão |

## USUARIO_MANUAL.md

Este é o manual geral da plataforma.

Ele contém instruções para:

- acesso ao sistema;
- cadastro e consulta de pessoas;
- Financeiro;
- Eventos;
- Comunicação;
- Escola Bíblica;
- Configurações;
- FAQ;
- suporte.

O documento registra explicitamente:

```text
Versão do Sistema: v1.12.0
Última atualização: 13/05/2026
```

Portanto, ele deve ser tratado como manual válido apenas na medida em que suas telas e fluxos continuarem correspondendo ao sistema atual.

Quando uma jornada mudar de forma relevante, o manual deve ser atualizado.

## GUIA_OPERACIONAL_EBD.md

Este documento está corretamente classificado nesta pasta.

Ele organiza a rotina da EBD por perfil:

```text
Secretaria / superintendência
Professor
Liderança
```

Também orienta:

- preparação do período;
- rotina semanal;
- chamada;
- ofertas;
- filtros;
- conferência;
- tratamento de divergências.

O guia considera explicitamente igreja ativa e permissões do usuário, o que é coerente com a arquitetura multi-tenant do GereIgreja.

## Diferença entre guia de usuário e regra funcional

A relação correta é:

```text
apps/
↓
define a regra funcional

usuario/
↓
explica como utilizar essa regra
```

Um manual pode simplificar linguagem e focar em passos de uso.

Ele não deve redefinir permissões, regras de negócio ou comportamento técnico.

Se houver divergência, a documentação funcional canônica do módulo deve ser revisada primeiro.

## Melhorias por versão

Os documentos:

```text
MELHORIAS_USUARIOS_v1.7.2.md
MELHORIAS_USUARIOS_v1.8.0_a_v1.8.67.md
MELHORIAS_USUARIOS_v1.8.75.md
```

possuem natureza histórica.

Eles não devem ser tratados como manual vigente.

São candidatos a:

```text
docs/release-notes/
```

ou manutenção nesta pasta apenas se houver uma decisão explícita de preservar uma visão histórica orientada ao usuário.

Não criar novos arquivos `MELHORIAS_USUARIOS_*` sem revisar primeiro a política de `release-notes/`.

## MANUAL_ASSINATURA_PLANOS.md

Esse documento pode permanecer nesta pasta se sua finalidade principal for orientar o usuário sobre:

- planos;
- assinatura;
- ativação;
- renovação;
- funcionalidades disponíveis.

Caso passe a documentar regras comerciais internas, billing técnico ou implementação de pagamentos, deve ser dividido ou referenciar a família responsável.

## README_IGREJA_USER.md

Esse arquivo deve ser revisado individualmente.

O nome indica um documento histórico ou específico de determinada jornada.

Antes de mantê-lo como referência ativa, verificar:

- se o conteúdo ainda corresponde à interface atual;
- se não está duplicado em `USUARIO_MANUAL.md`;
- se não foi absorvido por documentação funcional atual.

## chat_respostas.md

Arquivos de histórico de conversa não devem permanecer como documentação canônica.

Antes de remover:

1. verificar se contém decisões ainda não consolidadas;
2. incorporar qualquer conteúdo útil ao documento correto;
3. então arquivar ou remover.

Não deve ser usado como fonte oficial de produto.

## Regra para criar novo documento de usuário

Antes de criar arquivo em `docs/usuario/`:

1. confirme que o público principal é usuário final ou operador funcional;
2. verifique se o conteúdo já cabe em um manual existente;
3. prefira evoluir `USUARIO_MANUAL.md` antes de criar outro manual geral;
4. crie guia separado quando a jornada for extensa ou específica de perfil;
5. use linguagem operacional;
6. descreva passos concretos;
7. evite detalhes de implementação interna;
8. indique permissões apenas do ponto de vista do uso;
9. registre versão/data quando o conteúdo depender fortemente da interface;
10. atualize este README.

## Padrão de conteúdo

Um guia de usuário deve responder:

```text
Quem usa?
Para fazer o quê?
Onde acessar?
Quais passos seguir?
O que esperar depois?
O que fazer em caso de erro?
```

## Estado atual da pasta

A pasta tem uma finalidade válida e deve continuar existindo.

Entretanto, ela mistura atualmente:

```text
manuais ativos
guias operacionais
histórico de melhorias
documentos antigos
histórico de conversa
```

A prioridade é preservar os manuais úteis e reclassificar o conteúdo histórico.

## Princípio de manutenção

Documentação de usuário deve refletir a experiência real.

**Se a tela, jornada ou permissão mudou, o manual também precisa mudar.**

Manuais desatualizados não são apenas históricos: podem orientar o usuário a executar ações erradas.
