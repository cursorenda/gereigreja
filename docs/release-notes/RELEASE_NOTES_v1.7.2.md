# RELEASE_NOTES_v1.7.2.md

## Gereigreja v1.7.2 – Abril/2026

### Melhorias na Página de Igreja

- **Máscara de CNPJ Profissional:**
  - A máscara do campo CNPJ agora é aplicada automaticamente, mesmo quando o valor é preenchido pelo sistema ou ao selecionar "Usar CNPJ do Ministério".
  - O campo aceita apenas o formato válido (99.999.999/9999-99), evitando erros de digitação.
- **Seletor de CNPJ Integrado:**
  - Ao selecionar "Usar CNPJ do Ministério", o campo CNPJ é preenchido automaticamente com o CNPJ cadastrado no ministério e bloqueado para edição.
  - Ao retornar para "Usar CNPJ próprio", o campo é liberado para digitação.
- **Modularização do JS:**
  - Máscaras centralizadas em `form_masks.js`.
  - Lógica do seletor de CNPJ separada em `cnpj_igreja.js`.
- **Correções:**
  - O campo CNPJ agora recebe corretamente o valor do ministério.
  - A máscara é aplicada ao valor inicial e a valores preenchidos automaticamente.

---

**Equipe Gereigreja**
Abril/2026
