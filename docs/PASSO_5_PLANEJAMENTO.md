# 🎯 PASSO 5 PLANEJAMENTO - Workflow de Requisição de Permissões

**Próximo Passo:** 8-13 de Abril de 2026 (Estimado)  
**Prerequisito:** Passo 4 (✅ Concluído)  
**Complexidade:** Média-Alta  
**Horas Estimadas:** 8-12 horas

---

## 📋 OBJETIVO

Implementar um sistema de requisição de permissões onde:
1. Usuarios podem **solicitar acesso** a grupos/igrejas
2. Administradores **revisam e aprovam** requisições
3. Sistema **registra** na auditoria cada aprovação/negação
4. **Notificações** informam interessados sobre mudanças
5. Histórico completo é **mantido** para compliance

---

## 🔧 ESTRUTURA TÉCNICA

### Modelos a Criar

```python
class PermissionRequest(Model):
    """Requisição de acesso a grupo/permissão"""
    usuario_solicitante = ForeignKey(User)
    grupo_solicitado = ForeignKey(Group)
    data_solicitacao = DateTimeField()
    motivo = TextField()  # Por que precisa deste acesso?
    status = CharField(choices=['PENDENTE', 'APROVADO', 'NEGADO', 'CANCELADO'])
    
class PermissionApproval(Model):
    """Log de aprovação/negação"""
    requisicao = ForeignKey(PermissionRequest)
    usuario_aprovador = ForeignKey(User)
    data_resposta = DateTimeField()
    tipo_resposta = CharField(choices=['APROVADO', 'NEGADO'])
    comentario = TextField()  # Justificativa
    # Integração com PermissionChangeLog na auditoria
```

### Views a Criar

```python
# Usuário Final
1. listar_minhas_requisicoes()
   - Mostra requisições do usuário
   - Status: Pendente, Aprovada, Negada

2. criar_requisicao_permissao()
   - Formulário para solicitar grupo
   - Seleção de motivo (predefinidos)
   - Campo de justificativa livre

# Administrador
3. listar_requisicoes_pendentes()
   - Dashboard de requisições à espera
   - Filtros: usuário, grupo, data

4. detalhe_requisicao_para_aprovar()
   - Visualizar requisição completa
   - Histórico do usuário
   - Botões: Aprovar / Negar

5. processar_requisicao()
   - POST endpoint
   - Salva aprovação/negação
   - Dispara signal para auditoria
   - Envia notificação

# Relatórios
6. relatorio_requisicoes()
   - Taxa de aprovação
   - Tempo médio de resposta
   - Grupos mais requisitados
```

### Permission Request States

```
┌─────────────────────────────────────────┐
│                                          │
│  1. PENDENTE                             │
│  └──────► 2a. APROVADO ──► ATIVADO      │
│           2b. NEGADO ───► FINALIZADO    │
│  └─────► 3. CANCELADO ──► FINALIZADO    │
│                                          │
└─────────────────────────────────────────┘

PENDENTE → Aguardando resposta do admin
APROVADO → Admin aprovou, aplicar grupo
NEGADO → Admin recusou, motivo registrado
CANCELADO → Usuário cancelou a requisição
```

---

## 📧 NOTIFICAÇÕES

### Eventos que Geram Notificações

```
1. Requisição Criada
   Destinatário: Admin do ministério
   Conteúdo: Novo usuário X solicitou acesso ao grupo Y
   Link: Para dashboard de aprovação

2. Requisição Aprovada
   Destinatário: Usuário solicitante
   Conteúdo: Sua requisição para {grupo} foi aprovada!
   Link: Para lista de permissões

3. Requisição Negada
   Destinatário: Usuário solicitante
   Conteúdo: Sua requisição foi negada pelo motivo: {motivo}
   Link: Para solicitar novamente

4. SLA Vencido (opcional)
   Destinatário: Gerente de permissões
   Conteúdo: {N} requisições pendentes há mais de 7 dias
   Link: Para dashboard
```

### Canais de Notificação

```
✅ Email
✅ System Messages (banco de dados)
✅ (Futuro) SMS
✅ (Futuro) Push notifications
```

---

## 🎨 TEMPLATES NECESSÁRIOS

```
1. requerer_permissao.html
   └─ Formulário para solicitar grupo
      ├─ Seleção do grupo desejado
      ├─ Motivo predefinido (dropdown)
      ├─ Descrição livre
      └─ Botão: Enviar Requisição

2. minhas_requisicoes.html
   └─ Lista de requisições do usuário
      ├─ Filtro: Status (Todas, Pendentes, Aprovadas, Negadas)
      ├─ Tabela com histórico
      │  ├─ Grupo solicitado
      │  ├─ Data
      │  ├─ Status (badge colorido)
      │  ├─ Ação (Cancelar se pendente)
      └─ Detalhes ao clicar

3. requisicoes_pendentes_admin.html
   └─ Dashboard para admin
      ├─ Filtros: Usuário, Grupo, Data
      ├─ Tabela de requisições pendentes
      │  ├─ Usuário solicitante
      │  ├─ Grupo solicitado
      │  ├─ Motivo (snippet)
      │  ├─ Data
      │  └─ Ação: "Revisar"
      └─ Alertas de SLA

4. detalhe_requisicao.html
   └─ Página de revisão (admin)
      ├─ Informações do usuário
      │  ├─ Nome, email, grupos atuais
      │  ├─ Histórico de mudanças de permissão
      │  └─ Últimos acessos negados
      ├─ Detalhes da requisição
      │  ├─ Motivo
      │  ├─ Justificativa
      │  └─ Data
      ├─ Análise de risco
      │  ├─ "Este usuário já tem X grupos (MÉDIO risco)"
      │  └─ Recomendação
      └─ Ações
         ├─ Textarea para comentário
         ├─ Botão: Aprovar
         └─ Botão: Negar

5. relatorio_requisicoes.html
   └─ Dashboard de estatísticas
      ├─ Cards: Total, Pendentes, Aprovadas, Negadas
      ├─ Gráficos:
      │  ├─ Taxa de aprovação (%)
      │  ├─ Tempo médio de resposta
      │  └─ Grupos mais requisitados
      └─ Tabela: Últimas 20 requisições
```

---

## 🔄 INTEGRAÇÃO COM PASSO 4

### Auditoria Automática

```
Quando: Permmissão é APROVADA
┌─────────────────────────────────┐
│ 1. PermissionApproval criado    │
│ 2. Signal dispara               │
│ 3. Grupo adicionado ao usuário  │
│    └─ (trigger m2m_changed)     │
│ 4. PermissionChangeLog criado   │
│    com metadata:                │
│    ├─ usuario_executor: admin   │
│    ├─ acao: 'ADD'               │
│    ├─ observacao: reference     │
│    │   a PermissionRequest ID   │
│    └─ Integração completa!      │
└─────────────────────────────────┘
```

---

## 🔐 PERMISSÕES

```
Criar Requisição
├─ Permissão: user.is_authenticated
└─ Filtro: Grupos disponíveis (por ministério)

Listar Minhas Requisições
├─ Permissão: user.is_authenticated
└─ Filtro: Apenas as do usuário

Listar Requisições (admin)
├─ Permissão: ADMIN_MINISTERIO ou SUPER
└─ Filtro: Seu ministério

Aprovar/Negar
├─ Permissão: ADMIN_MINISTERIO ou SUPER
└─ Restrição: Apenas requisições do seu ministério
```

---

## 📊 BANCO DE DADOS

### Migrações Necessárias

```
1. Criar modelo PermissionRequest
   - 10 campos
   - 3 índices
   - 1 unique constraint

2. Criar modelo PermissionApproval
   - 7 campos
   - 2 índices

3. Criar tabela intermediária para notificações (opcional)
```

---

## 🧪 TESTES NECESSÁRIOS

```
Unit Tests:
✓ Criar requisição com dados válidos
✓ Criar requisição com dados inválidos
✓ Listar requisições do usuário
✓ Aprovar requisição (deve adicionar grupo)
✓ Negar requisição
✓ Cancelar requisição
✓ Validação de SLA
✓ Isolamento por ministério

Integration Tests:
✓ Signal dispara após aprovação
✓ Auditoria registra corretamente
✓ Notificações são enviadas
✓ Email contém link correto
✓ Fluxo completo: solicitar → aprovar → ativar

E2E Tests:
✓ Usuário cria requisição
✓ Admin recebe notificação
✓ Admin aprova
✓ Usuário recebe notificação
✓ Grupo é adicionado
✓ Auditoria registra tudo
```

---

## 📝 CHECKLIST PRÉ-IMPLEMENTAÇÃO

### Código
- [ ] Criar `permissao/models.py` com PermissionRequest e PermissionApproval
- [ ] Criar `permissao/forms.py` com formulários
- [ ] Criar `permissao/views.py` com 6 views (3 user, 2 admin, 1 report)
- [ ] Criar `permissao/urls.py` com 6 rotas
- [ ] Criar `permissao/signals.py` para integração com auditoria
- [ ] Criar `permissao/apps.py` com AppConfig

### UI/Templates
- [ ] 5 templates HTML (listar abaixo)
- [ ] CSS/Bootstrap para cards e badges de status
- [ ] Emails templates (3 tipos)

### Testes
- [ ] 8+ unit tests
- [ ] 5+ integration tests
- [ ] 3+ E2E tests

### Documentação
- [ ] PASSO_5_REQUISICOES_RESUMO.md
- [ ] PASSO_5_CHECKLIST_FINAL.md
- [ ] PASSO_5_RELATORIO_FINAL.md

---

## 🎯 CRITÉRIOS DE ACEITAÇÃO

```
✅ Usuário pode criar requisição de permissão
✅ Admin vê dashboard com requisições pendentes
✅ Admin pode aprovar/negar com justificativa
✅ Grupo é adicionado automaticamente após aprovação
✅ Auditoria registra cada ação
✅ Notificações são enviadas (email + sistema)
✅ Histórico completo é mantido
✅ Testes validam funcionalidade (>85% coverage)
✅ Isolamento por ministério é respeitado
✅ SLA de resposta pode ser monitorado
```

---

## 📆 ROADMAP

### Fase 1: Modelos e Lógica (1-2h)
- Criar modelos
- Criar signals
- Criar formas

### Fase 2: Views e URL (2-3h)
- Implementar 6 views
- Registrar rotas
- Integrar com auditoria

### Fase 3: UI/Templates (2-3h)
- 5 templates
- Email templates
- Layout responsivo

### Fase 4: Notificações (1-2h)
- Sistema de notificações
- Email sending
- Integração

### Fase 5: Testes (1-2h)
- Unit tests
- Integration tests
- E2E tests

### Fase 6: Documentação (0.5-1h)
- README
- Documentação técnica
- Checklist final

**Total Estimado:** 8-13 horas

---

## 🚀 PRÓXIMO: PASSO 6

Após Passo 5 concluído:
- Dashboard de compliance
- Relatórios de conformidade
- Integração com auditorias externas
- Alertas automáticos
- Recomendações baseadas em IA

---

## 📞 PONTOS DE CONTATO

**Integração com Passo 4:**
- Usar signals do auditoria/signals.py
- Registrar em PermissionChangeLog
- Usar helpers de AccessDeniedLog

**Permissões:**
- Usar `user_has_permission_level_or_higher()` existente
- Respeitar isolamento de ministério

**UI:**
- Seguir bootstrap 5 como em Passo 3
- Usar mesmos estilos e patterns

---

*Planejamento criado: 7 de Abril de 2026*  
*Status: Pronto para iniciar quando Passo 4 for aprovado*
