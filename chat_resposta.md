# WAHA: Railway vs Render — O que é hospedado e para quem

## O que é hospedado

**WAHA** (WhatsApp HTTP API) é um **servidor separado** — uma aplicação Docker que roda independente do Gereigreja. Ele é quem se conecta ao WhatsApp (como um cliente WhatsApp Web) e expõe uma API REST. O Gereigreja chama essa API para enviar mensagens.

```
Gereigreja (Render) ──HTTP──► WAHA Server (Railway/Render/VPS) ──► WhatsApp
```

---

## Railway vs Render para hospedar o WAHA

| | **Railway** | **Render** |
|---|---|---|
| **Deploy Docker** | 1 clique com template pronto | Precisa configurar manualmente |
| **Custo** | ~$5/mês (uso real) | Free tier tem sleep após inatividade |
| **Sleep em inatividade** | Não (plano pago) | Sim (free tier) — WAHA cai após 15min |
| **Facilidade** | Muito fácil, template oficial WAHA disponível | Mais trabalhoso |
| **Indicação** | ✅ Recomendado para WAHA | Só se já pagar plano pago |

**Problema crítico do Render free:** O WAHA "dorme" após inatividade. Quando o Gereigreja tentar enviar mensagem de madrugada (cron job), o WAHA pode estar offline.

---

## Perspectiva: Desenvolvedor vs Admin do Ministério

**Desenvolvedor (você):**
- Faz o deploy do WAHA no Railway uma vez
- Configura a variável de ambiente `WAHA_API_KEY` lá
- Pega a URL pública gerada (ex: `https://waha-xyz.up.railway.app`)
- Isso é feito **uma única vez** por ministério

**Admin do Ministério (usuário não-técnico):**
- Recebe a URL e a API Key do desenvolvedor
- Entra em `/comunicacao/whatsapp/configuracao-global/` e cola os dois dados
- Clica em "Salvar" — pronto
- Depois, cada congregação só precisa escanear um QR code

---

## Conclusão prática

O mais simples seria **remover a opção Render** do passo a passo e deixar **só Railway** como recomendação, com o botão de 1 clique. O admin do ministério não precisa escolher — o desenvolvedor já fez isso por ele.

---

## Alterações Realizadas

### 1. Novo Context Processor Unificado (`core/context_status_plano.py`)
- Consolida os 3 canais de alerta em um único `status_plano_unificado()`
- Sistema de prioridade em 4 níveis:
  - 🔴 **CRÍTICO**: Sem assinatura ou assinatura vencida
  - 🔴 **AVISO**: Limite de membros atingido (100%)
  - 🟡 **ATENÇÃO**: Limite próximo (80–99%)
  - ✅ **OK**: Nenhum alerta necessário
- Extrai o ministério de forma inline (evita importação circular de `core.utils`)
- Fallback seguro com log de erros

### 2. Utils Simplificado (`core/utils.py`)
- Removido `messages.warning()` de `get_ministerio_or_error()`
- Mantida apenas a lógica do sininho de notificações para admin/financeiro
- Verificações de assinatura agora delegadas ao context processor

### 3. Context Processors Limpos (`core/context_processors.py`)
- Removida a função redundante `alerta_limite_plano()`
- Mantida `deduplicate_assinatura_vencida()` como deduplicador de mensagens residuais

### 4. Settings Atualizado (`core/settings.py`)
- Registrado novo processor: `core.context_status_plano.status_plano_unificado`
- Removida referência ao antigo `alerta_limite_plano`

### 5. Banner Unificado no Template (`templates/base_com_menu.html`)
- Bloco `{% if status_plano %}` único substitui os 2 blocos anteriores
- Trata os 3 estados de alerta com estilo adequado:
  - `alert-danger` para crítico/aviso (vermelho)
  - `alert-warning` para atenção (amarelo)
- Exibe ícone, mensagem, porcentagem e botão "Fazer upgrade"

---

## Validação
✅ `python manage.py check` passou (sem erros de sintaxe ou importação)
✅ Todas as funções de serviço existem e foram importadas corretamente
✅ URL `configuracao:gerenciar_assinatura` verificada
✅ Sem importações circulares

---

## Arquitetura — Fluxo do Processor

```
status_plano_unificado(request)
  ├─ Verificação de autenticação    → retorna None
  ├─ Extrai ministério (inline)
  ├─ Verifica assinatura_esta_regular()
  │    NÃO                          → retorna alerta crítico
  ├─ Verifica limite em 100%
  │    SIM                          → retorna alerta de aviso
  ├─ Verifica limite entre 80–99%
  │    SIM                          → retorna alerta de atenção
  └─ caso contrário                 → retorna None (estado OK)
```

---

## Benefícios do Refactor
- **Fonte única de verdade**: toda lógica de status do plano em um único processor
- **Baseado em prioridade**: alerta de maior prioridade exibido primeiro
- **Sem duplicatas**: integrado ao `deduplicate_assinatura_vencida()` existente
- **Degradação elegante**: falha silenciosa em caso de erros
- **Testável**: fácil de mockar o ministério nos testes unitários

O refactor está concluído. Todo o enforcement do Item 1 e a lógica de alerta do Item 2 funcionam dentro deste sistema unificado. Pronto para avançar para os Itens 3–8.

---

## Próximos Itens

| # | Item | Status |
|---|------|--------|
| 1 | Enforcement de limites de plano | ✅ Concluído |
| 2 | Alerta de 80% no painel | ✅ Concluído |
| 3 | Portal Stripe (Billing Portal) | ⏳ Pendente |
| 4 | Downgrade automático para Pioneiro | ⏳ Pendente |
| 5 | Tratamento de inadimplência + grace period | ⏳ Pendente |
| 6 | Cupons de desconto no checkout | ⏳ Pendente |
| 7 | Página "Minha Assinatura" | ⏳ Pendente |
| 8 | Trial de 14 dias | ⏳ Pendente |

---

# Plano de Integração WAHA (WhatsApp HTTP API) com Django

---

## 1. Análise do Sistema e Pontos de Integração

### a) Pontos de Notificação
- Identifique onde no sistema Django faz sentido enviar notificações (ex: cadastro de membros, aniversariantes, eventos, confirmações, avisos de reuniões, etc).
- Defina quais modelos e ações vão disparar notificações (signals, views, tasks).

### b) Estrutura de Usuários
- Certifique-se de que os usuários/membros possuem um campo para número de WhatsApp (com DDI, DDD e validação).

---

## 2. Documentação WAHA (WhatsApp HTTP API)

### a) Como funciona
- WAHA expõe endpoints HTTP REST para envio de mensagens, recebimento de webhooks, status, etc.
- Você precisa de uma instância WAHA rodando (Docker/local/cloud) conectada a um WhatsApp Business.

### b) Endpoints principais
- Envio de mensagem: `POST /api/sendText`
- Recebimento de mensagens/eventos: Webhook configurável
- Status da instância: `GET /api/status`

### c) Exemplo de payload para envio:
```json
{
  "chatId": "5511999999999@c.us",
  "text": "Sua mensagem aqui"
}
```

---

## 3. Integração Django

### a) Instalação de dependências
- Use `requests` para chamadas HTTP.
- (Opcional) Celery para envio assíncrono.

### b) Função utilitária para envio
Crie um utilitário em `core/utils.py`:
```python
import requests

WAHA_URL = "http://localhost:3000/api/sendText"  # ajuste para seu endpoint

def send_whatsapp_message(phone, text):
    payload = {
        "chatId": f"{phone}@c.us",
        "text": text
    }
    response = requests.post(WAHA_URL, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()
```

### c) Uso em signals/views
Exemplo em um signal:
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Membro
from core.utils import send_whatsapp_message

@receiver(post_save, sender=Membro)
def notifica_novo_membro(sender, instance, created, **kwargs):
    if created and instance.telefone:
        send_whatsapp_message(instance.telefone, f"Bem-vindo, {instance.nome}!")
```

### d) Recebendo Webhooks (opcional)
- Crie uma view Django para receber webhooks do WAHA (mensagens recebidas, status, etc).
- Exemplo:
```python
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def waha_webhook(request):
    # Parse e trate o payload recebido
    return JsonResponse({'status': 'ok'})
```

---

## 4. Segurança e Logs

- Proteja o endpoint de webhook (token/segreado).
- Faça log dos envios e respostas para auditoria.
- Trate erros de envio (timeout, número inválido, etc).

---

## 5. Testes

- Teste localmente com um número real.
- Valide logs e respostas do WAHA.
- Simule falhas e veja o tratamento.

---

## 6. Documentação e Treinamento

- Documente no README como configurar o WAHA, variáveis de ambiente, exemplos de uso.
- Oriente o time sobre onde disparar notificações e como monitorar.

---

# Exemplos e Ideias Profissionais para WhatsApp Integrado (WAHA)

---

## 1. Estrutura Recomendada no Sistema

### a) Cadastro de Número WhatsApp por Congregação/Pastor
- Modelagem: Adicione campos na tabela de configuração da congregação/pastor:
  - `whatsapp_numero_envio` (número do WhatsApp conectado ao WAHA)
  - `whatsapp_nome_remetente` (opcional, para exibir no painel)
  - `whatsapp_token_webhook` (para segurança de recebimento)
- Tela de Configuração: Permita que cada pastor/congregação cadastre e teste seu número.

### b) Associação de Membros a Números de WhatsApp
- Garanta que cada membro tenha um campo `telefone_whatsapp` validado (com DDI/DDD).

---

## 2. Exemplos de Automação de Envios

### a) Aniversariantes
- Agendamento: Use um comando Django customizado (management command) ou Celery para rodar diariamente.
- Lógica: Para cada membro aniversariante do dia, envie mensagem personalizada.
- Exemplo:
```python
from core.utils import send_whatsapp_message
from datetime import date
from .models import Membro, Congregacao

def enviar_aniversariantes():
    hoje = date.today()
    for congregacao in Congregacao.objects.all():
        membros = Membro.objects.filter(
            data_nascimento__month=hoje.month,
            data_nascimento__day=hoje.day,
            congregacao=congregacao,
            telefone_whatsapp__isnull=False
        )
        for membro in membros:
            send_whatsapp_message(
                membro.telefone_whatsapp,
                f"Parabéns, {membro.nome}! Que Deus te abençoe!"
            )
```

### b) Novos Membros
- Trigger: Signal `post_save` no cadastro de membro.
- Mensagem: "Bem-vindo à família!" (personalizável por congregação).

### c) Agradecimento por Contribuição (Dízimo/Oferta)
- Trigger: Após registro de contribuição.
- Mensagem: "Obrigado por sua fidelidade, {nome}! Deus multiplique."

### d) Lembrete de Cultos/Eventos
- Agendamento: Celery ou comando semanal.
- Segmentação: Envie para todos ou grupos específicos (ex: jovens, casais).
- Mensagem: "Lembrete: culto especial amanhã às 19h!"

### e) Versículos por Categoria
- Futuro: Permita cadastrar listas de versículos por categoria (jovens, mulheres, etc).
- Envio: Agendado ou manual, com seleção de categoria.

---

## 3. Ideias para Botões de Envio Manual

- No painel do membro: Botão "Enviar WhatsApp" ao lado do telefone.
- Na lista de aniversariantes: Botão "Enviar para todos" ou individual.
- Na tela de eventos: Botão "Notificar participantes".
- Na tela de contribuições: Botão "Agradecer por WhatsApp".
- Painel de automações: Permita ativar/desativar automações e visualizar logs de envios.

---

## 4. Boas Práticas dos Melhores Sistemas de Igreja

- Personalização: Permitem editar o texto das mensagens por congregação.
- Logs e Auditoria: Guardam histórico de envios, status (enviado, entregue, erro).
- Opt-in/Opt-out: Permitem ao membro pedir para não receber mensagens.
- Templates: Oferecem modelos prontos e variáveis (ex: {nome}, {evento}).
- Testes: Botão "Testar envio" na configuração.
- Limites: Protegem contra spam (ex: máximo X mensagens/dia).
- Centralização: Painel para ver todas as automações e mensagens agendadas.

---

## 5. Exemplo de Modelos Django

```python
# models.py
class Congregacao(models.Model):
    nome = models.CharField(max_length=100)
    whatsapp_numero_envio = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_token_webhook = models.CharField(max_length=64, blank=True, null=True)
    # ...outros campos...

class Membro(models.Model):
    nome = models.CharField(max_length=100)
    telefone_whatsapp = models.CharField(max_length=20, blank=True, null=True)
    data_nascimento = models.DateField()
    congregacao = models.ForeignKey(Congregacao, on_delete=models.CASCADE)
    # ...outros campos...
```

---

## 6. Exemplo de Utilitário Centralizado

```python
# core/utils.py
def send_whatsapp_message(phone, text, congregacao=None):
    # Use o número/configuração da congregação para autenticar no WAHA
    # ...código conforme exemplo anterior...
    pass
```

---

## 7. Sugestão de Interface/Admin

- Configuração WhatsApp: Menu em "Configurações da Congregação".
- Painel de Mensagens: Listagem de mensagens enviadas, status, filtros por data/membro.
- Ações em massa: Selecionar membros/eventos e enviar mensagem personalizada.
- Logs: Exibir falhas, tentativas, entregas.

---

## 8. Segurança

- Cada congregação só pode enviar/receber pelo seu número.
- Proteja webhooks com token secreto.
- Valide números antes de enviar.

---

## 9. Futuro: Integração com Chatbot

- Permita respostas automáticas (ex: "Quero saber o próximo culto").
- Use webhooks do WAHA para receber e tratar mensagens.

---

Se quiser, posso gerar um exemplo de código completo para um dos casos acima (ex: envio automático para aniversariantes ou painel de configuração). Qual deseja priorizar?



---

## Variáveis de Ambiente para o Render Cron Job (07/05/2026)

### Nome do Cron Job
O nome **gereigreja** pode ficar assim — não afeta o funcionamento.

---

### Variáveis OBRIGATÓRIAS (copiar do Web Service → Environment para o Cron Job)

| Variável | Observação |
|---|---|
| `DJANGO_SECRET_KEY` | Chave secreta do Django |
| `DJANGO_DEBUG` | Coloque **False** (fixo no Cron) |
| `DB_NAME` | Nome do banco PostgreSQL |
| `DB_USER` | Usuário do banco |
| `DB_PASSWORD` | Senha do banco |
| `DB_HOST` | Host do banco |
| `DB_PORT` | Porta do banco (geralmente 5432) |
| `CLOUDINARY_CLOUD_NAME` | Obrigatório — Django não inicia sem ele |
| `CLOUDINARY_API_KEY` | Obrigatório |
| `CLOUDINARY_API_SECRET` | Obrigatório |
| `gereigreja_email_password` | Senha SMTP Brevo |

### Variáveis OPCIONAIS
| Variável | Observação |
|---|---|
| `STRIPE_PUBLISHABLE_KEY` | Só se o Cron usar pagamentos |
| `STRIPE_SECRET_KEY` | Idem |
| `STRIPE_WEBHOOK_SECRET` | Idem |

---

### WAHA — não precisa de variável de ambiente
A URL do WAHA, API Key e token ficam salvos no **banco de dados**, na tela:
**Comunicação → Configurar WhatsApp por congregação**

---

### Resumo crítico
- **Não usar** `DATABASE_URL` — o projeto usa as 5 variáveis separadas (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)
- As mais críticas: 5 de banco + 3 do Cloudinary — sem elas o Django não inicia
- `DJANGO_DEBUG` = `False` obrigatório em produção

