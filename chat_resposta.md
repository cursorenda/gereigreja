# Modo demonstração (sandbox) para o GereIgreja

## Objetivo
Permitir que qualquer usuário acesse o sistema com dados fictícios completos, podendo navegar, testar e trocar de perfil/grupo, sem afetar dados reais. Ao sair, tudo volta ao estado inicial.

## Plano técnico resumido

### 1. Estrutura dos dados demo
- Criar um "Ministério Demo" (ex: nome: DEMONSTRAÇÃO) e várias igrejas/congregações/subsedes fictícias.
- Todos os dados demo (membros, visitantes, lançamentos, etc.) devem estar ligados a esse ministério demo.
- Usuários demo para cada grupo de permissão (admin, secretário, pastor, tesoureiro, etc.), todos ligados ao ministério demo.
- Adicionar um campo/flag (ex: is_demo=True) nos objetos principais, se necessário.

### 2. Reset automático dos dados demo
- Criar um comando customizado Django (ex: `python manage.py reset_demo`) que:
  - Apaga todos os dados ligados ao ministério demo.
  - Recria os dados demo a partir de fixtures/scripts.
- Opcional: agendar reset automático (ex: via cronjob, celery beat, ou sempre que um usuário demo faz logout).

### 3. Fluxo de login demo
- Na página de vendas, adicionar botão "Entrar como demonstração".
- Ao clicar, mostrar tela para escolher o grupo/perfil desejado.
- Autenticar o usuário demo correspondente ao grupo escolhido.
- Permitir trocar de perfil facilmente (ex: menu "Trocar perfil demo").
- Exibir aviso claro de "Você está em modo demonstração. Nenhuma alteração será salva".

### 4. Segurança e isolamento
- Garantir que usuários demo nunca vejam dados reais (filtrar sempre por ministério demo).
- Bloquear envio de e-mails, notificações externas, etc. no modo demo.
- Resetar dados demo sempre que necessário para garantir ambiente limpo.

### 5. Atualização automática
- Como os dados demo estão no mesmo banco e seguem o mesmo modelo, qualquer atualização de código/migração será refletida automaticamente no ambiente demo.
- Basta rodar o comando de reset demo após deploys importantes.

---
## Checklist de arquivos e funções para modo demonstração (sandbox)

### 1. Templates
- Página de vendas: adicionar botão "Entrar como demonstração".
- Nova tela: seleção de perfil/grupo demo.
- Aviso/banner de "Modo demonstração" visível em todas as páginas demo.
- (Opcional) Menu ou botão para "Trocar perfil demo".

### 2. Views e URLs
- Nova view para login demo (ex: `demo_login_view`).
- Nova view para seleção/troca de perfil demo.
- Ajustar views principais para garantir filtro por ministério demo quando em modo demo.
- Nova URL para login demo e troca de perfil.

### 3. Models
- Garantir que todos os dados demo estejam ligados a um ministério demo (ex: campo ministry__is_demo=True ou ministry__name='DEMONSTRAÇÃO').
- (Opcional) Adicionar flag is_demo em modelos principais para facilitar filtros e resets.

### 4. Comando customizado Django
- Criar comando `reset_demo` para:
  - Apagar todos os dados ligados ao ministério demo.
  - Repopular com fixtures/scripts.

### 5. Fixtures/scripts
- Criar fixture JSON ou script Python para popular dados fictícios completos (membros, igrejas, lançamentos, etc.).

### 6. Middleware (opcional)
- Middleware para garantir que usuários demo nunca acessem dados reais.
- Bloquear envio de e-mails/notificações externas no modo demo.

### 7. Testes
- Testar login demo, troca de perfil, reset de dados e isolamento dos dados reais.

---

Esse checklist cobre todos os pontos essenciais para implementar o modo demonstração de forma segura e funcional.

---
## Sugestão de comandos úteis
- `python manage.py reset_demo` — Reseta e repovoa o ambiente demo.
- `python manage.py loaddata demo_fixture.json` — Carrega dados demo a partir de fixture.

---
## Observações
- O ambiente demo pode ser acessado por múltiplos usuários ao mesmo tempo, mas todos verão e editarão os mesmos dados fictícios.
- Para maior isolamento, pode-se criar "sessões demo" separadas, mas isso aumenta a complexidade.

---
# Fim do plano técnico para modo demonstração

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
