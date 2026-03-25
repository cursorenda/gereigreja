# Resposta Técnica: Transferência de Membros entre Igrejas do Mesmo Ministério

**Data:** 16/03/2026

---

## 1. Como implementar a transferência de membros?

### a) Processo sugerido
- Secretário/admin acessa o cadastro do membro na igreja de origem.
- Clica em "Transferir membro" e seleciona a igreja de destino (dentro do mesmo ministério).
- Confirma a transferência.
- O sistema move o membro para a igreja de destino, mantendo todos os dados, histórico, documentos, cargos, etc.
- O histórico de transferências é registrado (data, igreja origem, igreja destino, usuário responsável).

### b) Dados transferidos
- Todos os dados cadastrais do membro.
- Histórico de status, cargos, participações, documentos.
- O membro passa a pertencer à igreja de destino.

### c) Dados mantidos na igreja de origem
- O cadastro do membro pode ficar como "Inativo" ou "Transferido" na igreja de origem, com registro documental.
- O histórico de participação na igreja de origem permanece para relatórios e consultas.
- O campo "sub_status_inativo" pode ser preenchido como "TRANSFERIDO".

### d) Registro documental
- O sistema deve registrar a transferência no histórico do membro.
- Relatórios podem mostrar membros transferidos, para estatísticas e acompanhamento pastoral.

---

## 2. Como outros sistemas de igreja fazem?

### a) Sistemas conhecidos
- **Sistemas Batista, Assembleia, Adventista, Católico**: Geralmente permitem transferência entre congregações do mesmo ministério.
- O processo envolve:
  - Solicitação de transferência (por secretaria ou pastor)
  - Aprovação pela igreja de destino
  - Registro documental na igreja de origem (membro "transferido")
  - Cadastro completo na igreja de destino
- Alguns sistemas mantêm o histórico na igreja de origem, outros apenas registram a transferência.

### b) Exemplos práticos
- **Sistema Batista**: Membro é transferido, cadastro na origem fica "inativo/transferido", todos os dados vão para a igreja de destino.
- **Sistema Adventista**: Membro é transferido, histórico de participação e cargos permanece na origem, novo histórico começa na igreja de destino.
- **Sistema Católico**: Registro de batismo e histórico permanece na origem, transferência é registrada documentalmente.

---

## 3. Processo sugerido para Gereigreja

1. Membro é transferido via funcionalidade específica.
2. Todos os dados são migrados para a igreja de destino.
3. Na igreja de origem, o cadastro fica "inativo/transferido".
4. O histórico de status/cargos/documentos permanece acessível na origem.
5. O sistema registra a transferência (data, usuário, motivo, igreja origem/destino).
6. Relatórios podem mostrar membros transferidos, tanto na origem quanto na destino.

---

## 4. Considerações técnicas
- Evitar duplicidade de cadastro: o membro deve ter apenas um cadastro ativo.
- Permitir consulta ao histórico completo, tanto na origem quanto na destino.
- Permitir reversão da transferência, se necessário (ex: erro ou retorno do membro).
- Garantir integridade dos dados e registros.

---

## 5. Sugestão de campos/documentação
- Campo "sub_status_inativo" na origem: "TRANSFERIDO"
- Campo "igreja_origem", "igreja_destino", "data_transferencia", "usuario_transferencia" no histórico
- Relatório de transferências por período, igreja, motivo

---

## 6. Resposta sobre múltiplos cadastros e cargos

### a) Sobre cargos
- O cargo do membro não deve ser transferido automaticamente.
- Cada congregação tem seus próprios cargos e cooperações locais.
- Ao transferir, o membro chega sem cargo na igreja de destino; cargos devem ser atribuídos localmente.

### b) Sobre múltiplos cadastros
- Se cada transferência gera um novo cadastro de pessoa, o membro terá múltiplos cadastros dentro do mesmo ministério.
- Isso pode dificultar o acompanhamento pastoral, histórico e evitar duplicidade.
- O ideal é que o membro tenha **um cadastro único** no ministério, com histórico de todas as congregações por onde passou.
- O histórico de status, cargos, participações e transferências deve registrar a igreja de cada evento.

### c) Fluxo sugerido para múltiplas transferências
- O cadastro do membro permanece único, vinculado ao ministério.
- O campo "igreja_atual" indica a congregação onde o membro está.
- O histórico de transferências registra todas as mudanças de congregação.
- O histórico de cargos, participações e documentos deve registrar a igreja de cada evento.
- Relatórios podem mostrar por onde o membro passou, cargos em cada congregação, etc.

### d) Sobre edição do cadastro na igreja de origem
- Após a transferência, o cadastro na igreja de origem deve ficar "inativo/transferido".
- Não deve ser editável para dados pessoais, apenas para histórico documental.
- Apenas a igreja de destino pode editar dados pessoais do membro.
- O histórico na origem permanece para consulta e relatórios.

### e) Resumo
- Cadastro único por membro no ministério.
- Histórico completo de transferências, cargos, participações, documentos.
- Cargos atribuídos localmente em cada congregação.
- Cadastro na origem fica inativo/documental, não editável.
- Evita duplicidade e facilita acompanhamento pastoral.

---

## 7. Resposta sobre desistência ou mudança de destino na transferência

### a) Processo sugerido
- Quando o membro solicita transferência, o cadastro fica em "pendente de aprovação" na igreja de destino.
- Na igreja de origem, o status pode ser "aguardando transferência" ou "pendente de desligamento".
- O membro só é considerado transferido após aprovação da igreja de destino.

### b) Caso de desistência ou mudança de ideia
- Se o membro desistir antes da aprovação na igreja de destino:
  - O cadastro permanece ativo na igreja de origem.
  - O pedido de transferência pode ser cancelado pela secretaria/admin.
  - O histórico registra a solicitação e o cancelamento.
- Se o membro quiser ir para outro ministério:
  - O pedido de transferência é cancelado.
  - O processo de desligamento pode ser iniciado conforme regras do ministério.
  - O histórico registra o motivo e destino final.

### c) Fluxo de reversão
- O sistema deve permitir cancelar ou reverter pedidos de transferência antes da aprovação final.
- O cadastro do membro na origem não deve ser inativado/desligado até a confirmação da transferência.
- O histórico deve registrar todas as etapas: solicitação, aprovação, cancelamento, mudança de destino.

### d) Considerações técnicas
- Evitar perda de dados ou status incorreto.
- Permitir flexibilidade para casos de desistência, mudança de destino ou retorno.
- Garantir rastreabilidade de todas as ações no histórico do membro.

### e) Resumo
- Transferência só é efetivada após aprovação da igreja de destino.
- Pedido pode ser cancelado ou alterado antes da aprovação.
- Cadastro permanece ativo na origem até confirmação.
- Histórico registra todas as etapas e decisões.

---

## 8. Sugestões de melhorias para o processo de transferência

### a) Notificações automáticas
- Enviar notificações para secretaria/admin da igreja de origem e destino em cada etapa (solicitação, aprovação, cancelamento).
- Permitir acompanhamento do status pelo membro e pelas secretarias.

### b) Auditoria detalhada
- Registrar todas as ações no histórico: quem solicitou, quem aprovou, quem cancelou, datas e motivos.
- Permitir consulta fácil ao histórico de transferências.

### c) Permissões e controles
- Definir claramente quem pode solicitar, aprovar, cancelar ou editar transferências.
- Permitir apenas usuários autorizados para cada ação.

### d) Interface amigável
- Tela específica para acompanhamento de transferências pendentes, aprovadas e canceladas.
- Filtros por igreja, período, status, motivo.

### e) Relatórios
- Relatórios de transferências por período, igreja, motivo, destino.
- Relatórios de membros transferidos, retornados, cancelados.

### f) Integração com outros módulos
- Integrar transferências com módulos de cargos, eventos, documentos.
- Garantir que participações e cargos sejam corretamente registrados por igreja.

### g) Fluxo de retorno
- Permitir retorno do membro à igreja de origem de forma simples, mantendo histórico.
- Registrar motivo e data do retorno.

### h) Mensagens para o membro
- Informar o membro sobre status do processo, aprovações, cancelamentos e retorno.

---

## 9. Inclusão das melhorias no roadmap de alterações

### a) Roadmap sugerido para implementação

1. **Notificações automáticas**
   - Implementar envio de notificações para secretarias e membros em cada etapa do processo.

2. **Auditoria detalhada**
   - Registrar todas as ações no histórico, com usuário, data, motivo e status.

3. **Permissões e controles**
   - Definir e implementar permissões para solicitação, aprovação, cancelamento e edição de transferências.

4. **Interface amigável**
   - Criar telas específicas para acompanhamento de transferências, com filtros e status.

5. **Relatórios**
   - Desenvolver relatórios de transferências por período, igreja, motivo e status.

6. **Integração com outros módulos**
   - Garantir integração com cargos, eventos e documentos, registrando a igreja de cada evento.

7. **Fluxo de retorno**
   - Permitir retorno do membro à igreja de origem, mantendo histórico e registrando motivo.

8. **Mensagens para o membro**
   - Informar o membro sobre status, aprovações, cancelamentos e retorno.

---

Essas melhorias devem ser incluídas no processo de alteração/melhorias do sistema, priorizando transparência, rastreabilidade e facilidade de uso.

---

**Referências:**
- Sistemas Batista, Adventista, Católico
- Documentação Gereigreja (REGRAS_TIPOS_PESSOA_STATUS.md)

---

**Autor:** GitHub Copilot
