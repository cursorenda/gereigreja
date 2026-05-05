# 📋 Manual do Usuário — Assinatura e Planos

**Versão:** v1.9.2  
**Última Atualização:** 05/05/2026  
**Público-alvo:** Administradores de ministério

---

## 1. Visão Geral

A página de **Assinatura** reúne em um único lugar tudo o que você precisa saber sobre o plano contratado pelo seu ministério: consumo atual, limites, faturas e opções para alterar o plano.

**Acesso:** Menu lateral → **Configuração** → "Assinatura" (ou "Gerenciar Assinatura")

---

## 2. O que você verá na página

A página é organizada em seções:

### 2.1 Banners de estado

No topo da página podem aparecer avisos coloridos dependendo da situação da sua conta:

| Cor | Situação | O que fazer |
|-----|----------|-------------|
| 🔵 Azul | Você está no **período de cortesia** (conta recém-criada) | Aproveite para conhecer o sistema |
| 🟡 Amarelo | Você está no **período de teste grátis (trial)** | Acompanhe os dias restantes |
| 🟠 Laranja | Sua assinatura **vence em breve** | Regularize o pagamento para não ter acesso interrompido |
| 🔴 Vermelho | Situação **irregular** (pagamento em atraso ou plano não identificado) | Verifique as faturas ou entre em contato com o suporte |

> **Nota:** Se seu ministério possui uma **liberação especial (beta)**, o aviso de irregularidade fica oculto e você continua operando normalmente.

---

### 2.2 Cartão "Plano Atual"

Exibe as informações do seu plano vigente:

- Nome e descrição do plano
- Preço (mensal ou anual)
- Se há uma **liberação especial** ativa (plano beta concedido pelo suporte)
- Botão **"Portal de Cobrança"** — abre o painel do Stripe para gerenciar cartão, histórico de pagamentos e cancelamento pelo próprio portal

---

### 2.3 Cartão "Uso do Plano"

Exibe quantos recursos seu ministério está consumindo comparado ao limite do plano:

- **Barra de Pessoas Ativas** — quantidade de membros com status "Ativo" em todas as igrejas do ministério, versus o limite do plano
- **Barra de Igrejas** — quantidade de igrejas cadastradas, versus o limite do plano

Cores das barras:
- 🟢 Verde: uso abaixo de 80%
- 🟡 Amarelo: uso entre 80% e 100%
- 🔴 Vermelho: limite excedido

#### Acordeão "Como este cálculo foi feito"

Clique neste botão para ver um diagnóstico completo:
- Qual plano está sendo considerado (contratado ou por liberação especial)
- Critério exato: são contadas apenas as pessoas com status **exatamente "Ativo"** vinculadas às igrejas do ministério
- Fórmula utilizada

---

### 2.4 Opções especiais (quando disponíveis)

#### Período de Cortesia

Aparece quando seu ministério foi criado recentemente e ainda não contratou nenhum plano. Clique em "Ativar Cortesia" para iniciar 3 dias de acesso completo gratuito.

#### Período de Teste (Trial)

Aparece para ministérios elegíveis. Permite testar um plano pago por 14 dias sem custo. Durante o trial, o sistema funciona como se você estivesse no plano escolhido.

---

### 2.5 Abas da seção principal

#### Aba "Alterar Plano"

Exibe os planos disponíveis para o seu ministério em cartões. Cada cartão mostra:

**Identificações visuais dos planos:**

| Selo | Significado |
|------|-------------|
| ✓ **Plano atual** (azul) | Este é o seu plano vigente |
| ⬆ **Upgrade recomendado** (verde com faixa) | O próximo passo ideal para seu crescimento |
| ⬆ **Upgrade** | Planos acima do atual |
| ⬇ **Downgrade** | Planos abaixo do atual (com opacidade reduzida) |

**Avisos de limite:**

Se o seu ministério já excede os limites de um determinado plano, o cartão desse plano exibe:

```
⚠ Seu ministério excede este plano:
· Pessoas ativas: 144 (limite: 100)
· Igrejas: 3 (limite: 1)
Reduza o uso ou escolha um plano maior.
```

Neste caso, os botões de assinatura ficam **desabilitados com ícone de cadeado** até que você reduza o uso ou escolha um plano com limites maiores.

> **Nota:** Planos com limites zerados (valor 0) são **ilimitados** — não há restrição de uso.

**Cupom de desconto:**

Planos pagos exibem um campo para inserir um código de cupom antes de prosseguir para o checkout.

---

#### Aba "Faturas"

Exibe as faturas geradas pelo Stripe (pagamentos realizados, pendentes ou com falha). Mostra data, valor, status e link para download do boleto/recibo.

---

#### Aba "Histórico"

Exibe o histórico completo de assinaturas e eventos do ministério:

| Tipo | Descrição |
|------|-----------|
| Mensalidade | Pagamento mensal ou anual realizado |
| Cortesia | Período de cortesia gratuito concedido |
| Teste Grátis | Período de trial iniciado |

---

## 3. Planos Disponíveis

Os planos são configurados pelo administrador do sistema. A tabela abaixo mostra a estrutura típica:

| Plano | Pessoas Ativas | Igrejas | Observação |
|-------|---------------|---------|------------|
| **Pioneiro** | Até 100 | 1 | Gratuito — ideal para igrejas pequenas |
| **Crescimento** | Até 250 | 1 | Para igrejas em expansão |
| **Ministério** | Até 500 | 3 | Para ministérios com múltiplas congregações |
| **Rede** | Ilimitado | Ilimitado | Para grandes redes eclesiásticas |

> Os valores exatos e limites podem variar. Consulte a aba "Alterar Plano" para os valores atuais.

---

## 4. Como alterar o plano

1. Acesse **Configuração → Assinatura**
2. Clique na aba **"Alterar Plano"**
3. Escolha o plano desejado
4. Se for um plano pago, insira o cupom de desconto (se tiver) e clique em **"Mensal"** ou **"Anual"**
5. Você será redirecionado para a página segura de checkout do Stripe
6. Após o pagamento, o plano é atualizado automaticamente

---

## 5. Como cancelar a assinatura

1. Na página de Assinatura, clique em **"Portal de Cobrança"** (botão no cartão Plano Atual)
2. No portal do Stripe, escolha "Cancelar assinatura"
3. O acesso continua até o fim do período já pago

Ou use o botão **"Cancelar Assinatura"** no rodapé da página de Assinatura, que abre um modal de confirmação antes de prosseguir.

---

## 6. Perguntas Frequentes

**P: O que é "pessoas ativas"?**  
R: São os membros cadastrados no sistema com status exatamente **"Ativo"**. Visitantes, inativos, excluídos ou em outras situações não são contados.

**P: Posso fazer downgrade?**  
R: Sim, mas apenas se o seu uso atual estiver dentro dos limites do plano menor. Se você tiver 144 pessoas ativas e quiser ir para um plano com limite de 100, precisará primeiro reduzir o cadastro de pessoas ativas.

**P: O que acontece se eu exceder o limite?**  
R: O sistema não bloqueia automaticamente o uso — mas ao tentar contratar um plano menor, os botões ficarão desabilitados. Entre em contato com o suporte se precisar de orientação.

**P: O que é "liberação especial (beta)"?**  
R: É uma autorização concedida pelo suporte para que seu ministério acesse um plano específico de forma experimental, independentemente do plano contratado. Enquanto ativa, o sistema usa os limites do plano liberado.

**P: Quanto tempo dura o trial?**  
R: 14 dias gratuitos. O trial é registrado no Histórico e não gera cobrança.

**P: Quanto tempo dura a cortesia?**  
R: 3 dias. Destinada a ministérios recém-criados para conhecer o sistema.

---

*Dúvidas não respondidas aqui? Acesse **Menu → Suporte** ou envie um e-mail para o suporte técnico.*
