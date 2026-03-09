# Implementação LGPD - GereIgreja

## Status Geral
**Data de início:** Março 2026  
**Lei:** Lei 13.709/2018 (LGPD - Lei Geral de Proteção de Dados)  
**Objetivo:** Garantir conformidade legal com direitos dos titulares de dados

---

## ✅ Fases Implementadas

### Fase 1: Consentimento no Registro
**Status:** ✅ Completo  
**Implementado em:** Março 2026

**Arquivos modificados:**
- `contas/models.py` - Modelo `ConsentimentoLGPD`
- `contas/forms.py` - Campo `aceito_termos`
- `contas/views.py` - Registro de consentimento com IP
- `contas/templates/contas/registrar.html` - Checkbox obrigatório
- `contas/admin.py` - Admin somente leitura (auditoria)
- `contas/migrations/0005_add_consentimento_lgpd.py`

**Recursos:**
- Registro auditável de consentimentos
- Captura de IP real (considerando proxies)
- User Agent do navegador
- Versões dos documentos (Termos 1.0, Privacidade 1.0)
- Links para Termos de Uso e Política de Privacidade

**Conformidade LGPD:**
- ✅ Art. 7º - Base legal para tratamento de dados
- ✅ Art. 8º - Consentimento livre, informado e inequívoco

---

### Fase 2: Visualização de Dados Pessoais
**Status:** ✅ Completo  
**URL:** `/contas/meus-dados/`

**Arquivos:**
- `contas/views.py` - View `meus_dados_lgpd()`
- `contas/templates/contas/meus_dados.html`
- `contas/urls.py`
- `templates/base_com_menu.html` - Link no menu dropdown

**Recursos:**
- Cards organizados por categoria:
  - Dados da Conta
  - Ministério/Organização
  - Dados Pessoais (Membro)
  - Histórico de Consentimentos
  - Atividades no Sistema
- Mascaramento de dados sensíveis (CPF, RG)
- Toggle JavaScript para mostrar/ocultar
- Ações LGPD na sidebar

**Conformidade LGPD:**
- ✅ Art. 18, I - Confirmação da existência de tratamento
- ✅ Art. 18, II - Acesso aos dados

---

### Fase 3: Exportação JSON
**Status:** ✅ Completo  
**URL:** `/contas/meus-dados/exportar-json/`

**Arquivos:**
- `contas/views.py` - View `exportar_dados_json()`
- `contas/urls.py`

**Recursos:**
- Formato JSON estruturado
- Timestamps ISO8601
- Metadata (data exportação, versão, titular)
- Seções:
  - Usuario (conta, grupos, permissões)
  - Ministerio (nome, igrejas permitidas)
  - Membro (dados cadastrais completos)
  - Consentimentos (histórico completo)
  - Notas Pessoais
- Nome de arquivo: `meus_dados_[username]_[timestamp].json`
- Log de auditoria

**Conformidade LGPD:**
- ✅ Art. 18, II - Acesso aos dados
- ✅ Art. 18, V - Portabilidade dos dados

---

### Fase 4: Exportação PDF
**Status:** ✅ Completo  
**URL:** `/contas/meus-dados/exportar-pdf/`  
**Dependência:** ReportLab 4.2.5

**Arquivos:**
- `contas/views.py` - View `exportar_dados_pdf()`
- `contas/urls.py`
- `requirements.txt` - reportlab==4.2.5

**Recursos:**
- PDF formatado profissionalmente
- Design com cores e tabelas estilizadas
- Logo e identidade visual
- Seções idênticas ao JSON
- Rodapé com informações legais LGPD
- Quebra de página para consentimentos
- Nome de arquivo: `meus_dados_[username]_[timestamp].pdf`

**Conformidade LGPD:**
- ✅ Art. 18, II - Acesso aos dados em formato legível
- ✅ Art. 18, V - Portabilidade (formato PDF universal)

---

### Fase 5: Histórico Detalhado de Consentimentos
**Status:** ✅ Completo  
**URL:** `/contas/meus-dados/historico-consentimentos/`

**Arquivos:**
- `contas/views.py` - View `historico_consentimentos()`
- `contas/templates/contas/historico_consentimentos.html`
- `contas/urls.py`

**Recursos:**
- Estatísticas (total, mais recente, primeiro)
- Tabela completa com filtros visuais
- Badges coloridos (aceito/negado)
- Versões dos documentos
- IP completo (não truncado)
- User Agent completo (tooltip)
- Card educativo sobre LGPD
- Links para Termos e Política
- Contador de registros

**Conformidade LGPD:**
- ✅ Art. 8º § 6º - Informações sobre consentimento
- ✅ Transparência no tratamento de dados

---

## ❌ Fase Pendente - DECISÃO NECESSÁRIA

### Fase 6: Exclusão/Anonimização de Conta
**Status:** ❌ PENDENTE - Decisão de Design  
**Prioridade:** ALTA (requisito legal LGPD)

#### 🚨 Problema Técnico Identificado
```python
# configuracao/models.py linha 134-139
administrador_principal = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.PROTECT,  # ← Bloqueia exclusão!
    related_name='ministerios_administrados',
    verbose_name="Administrador Principal"
)
```

**Implicação:** Não é possível excluir completamente um usuário que seja `administrador_principal` de um ministério sem quebrar integridade referencial.

---

#### 🔀 Opção 1: Anonimização (Recomendada)

**Conceito:**
Manter o registro do usuário no banco de dados, mas substituir todos os dados pessoais por valores genéricos.

**Implementação:**
```python
# Pseudocódigo
def anonimizar_usuario(user):
    # User model
    user.username = f'anonimizado_{user.id}'
    user.email = f'anonimizado_{user.id}@sistema.local'
    user.first_name = 'Usuário'
    user.last_name = 'Anonimizado'
    user.is_active = False
    user.save()
    
    # PerfilUsuario
    perfil.telefone_contato = None
    perfil.whatsapp_contato = None
    perfil.foto_perfil = None
    perfil.save()
    
    # Membro (se existir)
    membro.cpf = None
    membro.rg = None
    membro.telefone = None
    membro.rua = None
    membro.numero_casa = None
    # ... outros campos sensíveis
    membro.save()
    
    # Criar registro de anonimização
    ConsentimentoLGPD.objects.create(
        usuario=user,
        tipo='anonimizacao',
        data_anonimizacao=timezone.now(),
        ip=request_ip,
        motivo='Solicitação LGPD Art. 18 VI'
    )
```

**Vantagens:**
- ✅ Mantém integridade referencial
- ✅ Preserva estrutura de ministérios
- ✅ Não quebra relatórios históricos
- ✅ Atende LGPD (eliminação de dados pessoais)
- ✅ Mais simples de implementar
- ✅ Reversível (em teoria, com backup)

**Desvantagens:**
- ❌ Registro permanece no banco (anonimizado)
- ❌ Possível preocupação com GDPR (Europa) - mais restritivo

**Conformidade Legal:**
- ✅ LGPD Art. 18, VI - "eliminação dos dados pessoais tratados com o consentimento do titular"
- ✅ Interpretação: Anonimização = Eliminação dos dados (dados não são mais pessoais)

---

#### 🔀 Opção 2: Transferência de Propriedade + Exclusão

**Conceito:**
Antes de permitir exclusão, exigir que o administrador transfira propriedade do ministério para outro usuário.

**Fluxo:**
1. Usuário clica "Solicitar Exclusão"
2. Sistema verifica: `Ministerio.objects.filter(administrador_principal=user).exists()`
3. **SE SIM:**
   - Mostrar modal/página: "Você é administrador. Transfira propriedade primeiro"
   - Lista de usuários elegíveis (membros do ministério com grupo Admin)
   - Usuário seleciona novo administrador
   - Sistema atualiza `ministerio.administrador_principal = novo_admin`
   - Sistema confirma transferência
4. **SE NÃO:**
   - Permite exclusão direta
5. Após transferência/confirmação: Excluir registro completamente

**Implementação:**
```python
# Pseudocódigo
def solicitar_exclusao_conta(request):
    # Verificar se é admin principal
    ministerios = Ministerio.objects.filter(administrador_principal=request.user)
    
    if ministerios.exists():
        # Exige transferência
        usuarios_elegiveis = obter_admins_ministerio(ministerios.first())
        return render('transferir_propriedade.html', {
            'ministerios': ministerios,
            'usuarios': usuarios_elegiveis
        })
    else:
        # Pode excluir após confirmação
        return render('confirmar_exclusao.html')

def transferir_propriedade(request, ministerio_id, novo_admin_id):
    ministerio = Ministerio.objects.get(id=ministerio_id)
    novo_admin = User.objects.get(id=novo_admin_id)
    
    # Validações
    if ministerio.administrador_principal != request.user:
        raise PermissionDenied
    
    # Transferir
    ministerio.administrador_principal = novo_admin
    ministerio.save()
    
    # Notificar novo admin
    enviar_email_nova_propriedade(novo_admin, ministerio)
    
    # Agora pode excluir
    return redirect('solicitar_exclusao_conta')

def confirmar_exclusao_definitiva(request):
    # Pedir senha para confirmar
    # Exportar dados automaticamente antes (JSON)
    # Deletar usuario
    request.user.delete()
    logout(request)
    return redirect('login')
```

**Vantagens:**
- ✅ Exclusão completa do registro
- ✅ Transparência total (usuário controla)
- ✅ Pode ser preferível em auditoria GDPR

**Desvantagens:**
- ❌ Mais complexo de implementar
- ❌ Requer interface de transferência
- ❌ E se não houver outro usuário elegível?
- ❌ Pode causar resistência do usuário (mais fricção)
- ❌ Precisa notificações/emails

---

#### 🔀 Opção 3: Híbrida (Recomendação Final)

**Conceito:**
Combinar as duas abordagens baseado no contexto.

**Regra:**
```
SE usuário é administrador_principal:
    → ANONIMIZAR (automaticamente, informar ao usuário)
    
SENÃO:
    → PERMITIR ESCOLHA:
       [ ] Anonimizar minha conta
       [ ] Excluir completamente
```

**Vantagens:**
- ✅ Melhor dos dois mundos
- ✅ Flexibilidade para usuários comuns
- ✅ Proteção de integridade para admins

---

## 📋 Checklist de Implementação (Quando Decidir)

### Arquivos a Criar/Modificar:
- [ ] `contas/views.py` - View `solicitar_exclusao_conta()`
- [ ] `contas/templates/contas/solicitar_exclusao.html`
- [ ] `contas/templates/contas/confirmar_exclusao.html`
- [ ] `contas/urls.py` - URL da exclusão
- [ ] `contas/models.py` - Método `anonimizar_usuario()` (se Opção 1/3)
- [ ] `contas/models.py` - Adicionar campo `data_anonimizacao` em ConsentimentoLGPD?
- [ ] `contas/templates/contas/meus_dados.html` - Ativar botão
- [ ] `configuracao/models.py` - Ajustes se necessário

### Funcionalidades Necessárias:
- [ ] Confirmação por senha (segurança)
- [ ] Modal de aviso (ação irreversível)
- [ ] Exportação automática antes de excluir (auditoria)
- [ ] Email de confirmação pós-exclusão
- [ ] Log de auditoria detalhado
- [ ] Testes unitários

### Validações de Segurança:
- [ ] Impedir exclusão de superusuários (is_superuser=True)
- [ ] Impedir exclusão se houver pendências financeiras?
- [ ] Verificar cascata de exclusões (ForeignKeys com CASCADE)
- [ ] Período de "quarentena" antes de exclusão definitiva? (30 dias)

---

## 🔐 Considerações de Segurança

### Auditoria:
- Todo processo de exclusão/anonimização deve ser logado
- Salvar snapshot dos dados antes (backup automático)
- Email de confirmação enviado ao usuário
- Registro no ConsentimentoLGPD com tipo='exclusao' ou 'anonimizacao'

### Reversibilidade:
- Anonimização pode ser parcialmente reversível com backup
- Exclusão completa é IRREVERSÍVEL (avisar usuário)

### Casos Especiais:
- **Superusuários:** Bloquear exclusão (manter pelo menos 1)
- **Únicos administradores:** Exigir transferência ou impedir
- **Dados financeiros:** Considerar manter anonimizado por obrigação contábil

---

## 📚 Referências Legais

### LGPD (Lei 13.709/2018)
- **Art. 7º:** Bases legais para tratamento
- **Art. 8º:** Consentimento
- **Art. 18:** Direitos do titular:
  - I - confirmação da existência de tratamento
  - II - acesso aos dados
  - III - correção de dados
  - V - portabilidade
  - **VI - eliminação dos dados** ← PENDENTE
  - IX - revogação do consentimento
- **Art. 46:** Segurança

### Interpretação Jurídica
- Anonimização de dados = Eliminação de dados pessoais (dado anonimizado não é mais "pessoal")
- LGPD não exige exclusão física do registro, mas eliminação da identificação

---

## 📞 Próximos Passos

1. **DECISÃO:** Escolher entre Opção 1, 2 ou 3
2. **DESIGN:** Criar wireframes da interface
3. **APROVAÇÃO:** Validar com advogado/DPO
4. **IMPLEMENTAÇÃO:** Seguir checklist acima
5. **TESTES:** Ambiente de staging antes de produção
6. **DOCUMENTAÇÃO:** Atualizar Política de Privacidade
7. **COMUNICAÇÃO:** Avisar usuários da nova funcionalidade

---

**Documento mantido por:** Equipe de Desenvolvimento  
**Última atualização:** 08/03/2026  
**Revisão legal:** Pendente
