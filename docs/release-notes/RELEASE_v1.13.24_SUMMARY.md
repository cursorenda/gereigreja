# RELEASE v1.13.24 - Onboarding premium e ajuste de aprovação

Data: 01/07/2026

## Resumo Executivo
A release v1.13.24 consolida a base estratégica de SEO do produto e corrige o fluxo de entrada do usuário/ministério para que o onboarding seja consistente com a automação do sistema: a igreja criada automaticamente passa a ser o destino principal após o cadastro.

## Entregas Principais

### 1) Redirecionamento correto no cadastro
- Após criar usuário/ministério no plano pioneiro, o sistema redireciona para a edição da igreja auto-criada.
- Remove o passo desnecessário de criar igreja manualmente logo após o cadastro.

### 2) Base documental SEO premium
- Novo conjunto de documentos em `docs/seo-premium/` com:
	- manifesto de marca;
	- estratégia geral;
	- arquitetura do site;
	- páginas pilares;
	- mapa mestre de palavras-chave.

### 3) Aprovação com destino útil
- Quando o ministério já está ativo, a tela de aprovação deixa de enviar o usuário para a home.
- O fluxo agora vai para a edição da igreja principal, com fallback seguro para a secretaria.

### 4) Regra reforçada no backend
- Import explícito de `Igreja` em `contas/views.py`.
- Teste de regressão cobrindo o redirect final do onboarding.

## Validação
- `python manage.py check` executado sem erros.

## Observações Operacionais
- Esta release não altera schema de banco.
- O warning de `requests/urllib3` no ambiente local permanece não bloqueante.