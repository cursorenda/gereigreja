# Notas de Atualização - Página de Igreja

## Melhorias Técnicas e de Usabilidade (Abril/2026)

### 1. Máscara de CNPJ Profissional e Automática
- A máscara do campo CNPJ agora é aplicada automaticamente, mesmo quando o valor é preenchido pelo sistema ou ao selecionar "Usar CNPJ do Ministério".
- O campo aceita apenas o formato válido (99.999.999/9999-99), evitando erros de digitação e facilitando a conferência visual.

### 2. Seletor de CNPJ Integrado ao Cadastro do Ministério
- Ao selecionar "Usar CNPJ do Ministério", o campo CNPJ é preenchido automaticamente com o CNPJ cadastrado no ministério.
- O campo fica bloqueado para edição manual neste modo, garantindo integridade dos dados.
- Ao retornar para "Usar CNPJ próprio", o campo é liberado para digitação.

### 3. Modularização e Organização do Código JavaScript
- Toda a lógica de máscara de campos foi centralizada em um único arquivo (form_masks.js), facilitando manutenção e padronização.
- A lógica do seletor de CNPJ foi separada em um arquivo próprio (cnpj_igreja.js), tornando o código mais limpo e fácil de evoluir.

### 4. Correção de Bugs
- Corrigido o problema onde o campo CNPJ não recebia o valor do ministério ao selecionar o modo correspondente.
- Corrigido o problema onde a máscara não era aplicada ao valor inicial ou ao valor preenchido automaticamente.

### 5. Orientações para Usuários
- Sempre que o CNPJ do ministério for atualizado, ele será refletido automaticamente nas igrejas que utilizam o modo "Usar CNPJ do Ministério".
- Para usar um CNPJ próprio, basta selecionar a opção e preencher normalmente.
- O sistema impede o uso de formatos inválidos, aumentando a confiabilidade dos dados.

---

Essas melhorias tornam o cadastro e edição de igrejas mais seguro, padronizado e fácil de usar, reduzindo erros e aumentando a produtividade dos usuários.

---

**Equipe Gereigreja**
Abril/2026
