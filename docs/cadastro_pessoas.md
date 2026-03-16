# Documentação do Cadastro de Pessoas

## Visão Geral
O sistema Gereigreja permite o cadastro de pessoas de duas formas principais:
- **Cadastro Público:** Via link único por igreja, sem necessidade de login.
- **Cadastro Interno:** Realizado por secretários ou administradores autenticados.

Ambos os fluxos garantem integridade dos dados, controle de status e aprovação pela secretaria.

---

## 1. Cadastro Público

### Fluxo
1. O usuário acessa o link público: `/secretaria/cadastro/igreja/<id>/`
2. Preenche o formulário simplificado (campos essenciais).
3. Campos de controle (igreja, tipo, status) são preenchidos automaticamente no backend:
   - **Igreja:** Definida pelo link.
   - **Tipo:** "Membro" (ou outro padrão configurado).
   - **Status:** "Aguardando aprovação".
4. Após envio, o usuário vê uma tela de sucesso e recebe orientação sobre a aprovação.
5. O cadastro fica pendente até análise da secretaria.

### Observações
- O usuário não escolhe igreja, tipo ou status.
- O status inicial pode ser "Aguardando aprovação" ou "Pendente" (compatível com filtros internos).
- O sistema exibe mensagens claras sobre o andamento do cadastro.

---

## 2. Cadastro Interno (Secretaria/Admin)

### Fluxo
1. Usuário autenticado acessa `/secretaria/pessoas/` e clica em "Adicionar Pessoa".
2. Preenche formulário completo, podendo definir igreja, tipo, status e outros campos.
3. Pode aprovar cadastros pendentes, alterar status e editar dados.
4. Mudanças de status são registradas no histórico.

### Observações
- Secretários podem aprovar/reprovar cadastros públicos.
- O sistema mantém histórico de mudanças de status e tipo.

---

## 3. Aprovação e Status
- Cadastros públicos entram como "Aguardando aprovação".
- Secretários visualizam pendentes na dashboard e na lista de pessoas.
- Ao aprovar, o status é alterado para "Ativo" (ou outro conforme regra da igreja).
- O histórico de status é registrado automaticamente.

---

## 4. Personalização e Campos Obrigatórios
- Campos obrigatórios podem ser ajustados no ModelForm.
- `help_text` nos campos orienta o usuário e o desenvolvedor.
- Para adicionar/remover campos do cadastro público, ajuste o parâmetro `auto_cadastro` no form.

---

## 5. Testando o Fluxo
- Realize um cadastro público e verifique se aparece como pendente.
- Aprove o cadastro e confira se o status muda para "Ativo".
- Teste o cadastro interno para garantir que todos os campos e históricos funcionam.

---

## 6. Dicas para Desenvolvedores
- Sempre use as URLs nomeadas (`lista_pessoas`, `editar_membro`, etc) para garantir compatibilidade.
- Consulte os `help_text` dos campos para entender regras e obrigatoriedades.
- Use os arquivos README e RELEASE_NOTES para histórico de versões e mudanças.

---

## 7. Referências
- Views principais: `secretaria/views.py`
- Formulários: `secretaria/forms.py`
- Modelos: `secretaria/models.py`
- Templates: `secretaria/templates/secretaria/`
- Rotas: `secretaria/urls.py`

---

*Última atualização: 16/03/2026*
