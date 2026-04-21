# Como implementar alteração em massa de pessoas/membros no módulo Secretaria

---

## 1. Análise do Sistema Atual
- Cadastro de pessoas/membros já possui:
  - Models robustos (`Pessoa`), com muitos campos e relacionamentos.
  - Forms reutilizáveis e validados.
  - Templates de listagem, edição, visualização e impressão.
  - Validações backend e frontend (CPF, email, máscaras, ViaCEP).
  - Documentação detalhada e sugestões de melhorias (inclusive UX).

---

## 2. Como implementar alteração em massa (Bulk Edit) de Pessoas

### a) Novo recurso: “Alteração em Massa”
- Adicionar botão “Alterar em Massa” na tela de listagem de pessoas/membros.
- Permitir seleção múltipla (checkbox) dos registros a serem alterados.

### b) Fluxo sugerido
1. Usuário seleciona várias pessoas na lista.
2. Clica em “Alterar em Massa”.
3. Abre uma tela/modal com os campos editáveis em massa (ex: status, tipo, grupo, tags, igreja, etc).
4. Usuário preenche os novos valores (apenas campos desejados).
5. Confirma a alteração.
6. Sistema aplica as mudanças apenas nos campos preenchidos, mantendo os demais inalterados.
7. Exibe resumo do que foi alterado e logs de auditoria.

### c) Implementação técnica
- **View:** Nova view/class-based view para receber lista de IDs e campos a alterar.
- **Form:** Formulário especial (ex: `PessoaBulkEditForm`) com campos opcionais.
- **Template:** Modal ou página dedicada, com UX clara sobre o que será alterado.
- **Validação:** Reutilizar validações já existentes (ex: status permitido, tipo válido).
- **Permissões:** Respeitar regras de permissão do usuário logado.
- **Auditoria:** Registrar alterações em massa para rastreabilidade.

### d) Sugestão de arquivos impactados
- `secretaria/views.py` (nova view ou método)
- `secretaria/forms.py` (novo form)
- `secretaria/templates/secretaria/lista_membros.html` (checkbox + botão)
- `secretaria/templates/secretaria/bulk_edit_pessoas.html` (nova tela/modal)
- `secretaria/urls.py` (nova rota)
- Testes em `secretaria/tests/`

---

## 3. Boas práticas
- Permitir desfazer (rollback) em caso de erro.
- Exibir resumo antes de confirmar.
- Limitar campos sensíveis (ex: não permitir troca de CPF em massa).
- Documentar o recurso para os usuários/admins.

---

## 4. Exemplo de uso
- Selecionar 10 membros e alterar status para “Inativo”.
- Trocar igreja de vários membros após transferência de congregação.
- Adicionar/remover tags em lote.

---

Se quiser um exemplo de código inicial para a view/form ou um esqueleto de template, posso gerar para você!
