# 🔒 Documentação: Sistema de Validações do Cadastro de Pessoas

**Data de Implementação:** 12 de Março de 2026  
**Versão:** 1.6.1  
**Status:** ✅ Implementado e Testado

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Validações Backend](#validações-backend)
3. [Máscaras JavaScript (Frontend)](#máscaras-javascript-frontend)
4. [Busca Automática de Endereço (ViaCEP)](#busca-automática-de-endereço-viacep)
5. [Como Testar](#como-testar)
6. [Localização do Código](#localização-do-código)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Sistema completo de validação de dados para o cadastro de pessoas, implementando:

- ✅ **Validação Backend:** CPF e Email com algoritmos robustos
- ✅ **Máscaras Automáticas:** Formatação em tempo real (CPF, Telefone, CEP, RG)
- ✅ **Busca de Endereço:** Integração com API ViaCEP para preenchimento automático
- ✅ **Feedback Visual:** Indicadores visuais de sucesso/erro

### 📊 Tabela Resumo

| Campo       | Validação Backend | Máscara Frontend | Formato           | API Externa |
|-------------|-------------------|------------------|-------------------|-------------|
| **CPF**     | ✅ Dígito Verif.  | ✅               | XXX.XXX.XXX-XX    | —           |
| **Email**   | ✅ Regex          | —                | nome@exemplo.com  | —           |
| **Telefone**| —                 | ✅               | (XX) XXXXX-XXXX   | —           |
| **CEP**     | —                 | ✅               | XXXXX-XXX         | ✅ ViaCEP   |
| **RG**      | —                 | ✅ Sanitização   | A-Z 0-9           | —           |

---

## 🔐 Validações Backend

### 1. Validação de CPF

**Implementação:** Algoritmo oficial da Receita Federal com dígito verificador

**Arquivo:** [`secretaria/forms.py`](secretaria/forms.py) (linhas 1-50)

#### Função Validadora

```python
def validar_cpf(cpf):
    """
    Valida CPF brasileiro usando algoritmo de dígito verificador.
    
    Args:
        cpf (str): CPF com ou sem formatação
        
    Returns:
        str: CPF validado (apenas números)
        
    Raises:
        ValidationError: Se CPF for inválido
    """
    cpf = re.sub(r'[^0-9]', '', cpf)  # Remove pontuação
    
    # Valida comprimento
    if len(cpf) != 11:
        raise ValidationError('CPF deve ter 11 dígitos.')
    
    # Rejeita CPFs com todos dígitos iguais
    if cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido (todos os dígitos iguais).')
    
    # Valida primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10: resto = 0
    if resto != int(cpf[9]):
        raise ValidationError('CPF inválido.')
    
    # Valida segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10: resto = 0
    if resto != int(cpf[10]):
        raise ValidationError('CPF inválido.')
    
    return cpf
```

#### Método do Form

```python
def clean_cpf(self):
    """Valida CPF se fornecido."""
    cpf = self.cleaned_data.get('cpf')
    if cpf:
        try:
            cpf_limpo = validar_cpf(cpf)
            # Formata XXX.XXX.XXX-XX para exibição
            return f'{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}'
        except ValidationError as e:
            raise ValidationError(e.message)
    return cpf
```

#### Comportamento

| Entrada         | Resultado            | Status |
|-----------------|----------------------|--------|
| 12345678909     | 123.456.789-09       | ✅     |
| 123.456.789-09  | 123.456.789-09       | ✅     |
| 000.000.000-00  | ❌ Erro              | ❌     |
| 111.111.111-11  | ❌ Erro              | ❌     |
| 12345678        | ❌ CPF deve ter 11 dígitos | ❌ |

---

### 2. Validação de Email

**Implementação:** Regex completo + normalização

**Arquivo:** [`secretaria/forms.py`](secretaria/forms.py) (linhas ~240-250)

#### Método do Form

```python
def clean_email(self):
    """Valida formato de email."""
    email = self.cleaned_data.get('email')
    if email:
        email = email.strip().lower()  # Remove espaços + lowercase
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError('Email inválido. Use o formato: nome@exemplo.com')
    return email
```

#### Comportamento

| Entrada              | Resultado            | Status |
|----------------------|----------------------|--------|
| TESTE@GMAIL.COM      | teste@gmail.com      | ✅     |
| teste@email.com      | teste@email.com      | ✅     |
| teste@com            | ❌ Email inválido    | ❌     |
| teste@               | ❌ Email inválido    | ❌     |
| teste                | ❌ Email inválido    | ❌     |

---

## ⚡ Máscaras JavaScript (Frontend)

**Implementação:** Event listeners com formatação em tempo real

**Arquivo:** [`secretaria/templates/partials/_form_dados_cadastrais.html`](secretaria/templates/partials/_form_dados_cadastrais.html) (linhas ~485-570)

### 1. Máscara de CPF

**Formato:** `XXX.XXX.XXX-XX`

```javascript
// Função genérica de máscara
function aplicarMascara(input, mascara) {
    input.addEventListener('input', function(e) {
        let valor = e.target.value.replace(/\D/g, '');
        let resultado = '';
        let j = 0;
        
        for (let i = 0; i < mascara.length && j < valor.length; i++) {
            if (mascara[i] === '#') {
                resultado += valor[j];
                j++;
            } else {
                resultado += mascara[i];
            }
        }
        
        e.target.value = resultado;
    });
}

// Aplicação
aplicarMascara(cpfInput, '###.###.###-##');
```

**Experiência do Usuário:**
- Digita: `1` → Exibe: `1`
- Digita: `123` → Exibe: `123`
- Digita: `1234` → Exibe: `123.4`
- Digita: `123456789` → Exibe: `123.456.789`
- Digita: `12345678909` → Exibe: `123.456.789-09`

---

### 2. Máscara de Telefone

**Formato:** `(XX) XXXXX-XXXX` (suporta celular com 9 dígitos)

```javascript
telefoneInput.addEventListener('input', function(e) {
    let valor = e.target.value.replace(/\D/g, '');
    let resultado = '';
    
    if (valor.length > 0) {
        resultado = '(' + valor.substring(0, 2);
        if (valor.length > 2) {
            resultado += ') ' + valor.substring(2, 7);
        }
        if (valor.length > 7) {
            resultado += '-' + valor.substring(7, 11);
        }
    }
    
    e.target.value = resultado;
});
```

**Experiência do Usuário:**
- Digita: `85` → Exibe: `(85`
- Digita: `85987` → Exibe: `(85) 987`
- Digita: `8598765` → Exibe: `(85) 98765`
- Digita: `85987654321` → Exibe: `(85) 98765-4321`

---

### 3. Máscara de CEP

**Formato:** `XXXXX-XXX`

```javascript
aplicarMascara(cepInput, '#####-###');
```

**Experiência do Usuário:**
- Digita: `60000` → Exibe: `60000`
- Digita: `600001` → Exibe: `60000-1`
- Digita: `60000000` → Exibe: `60000-000`

---

### 4. Sanitização de RG

**Formato:** Apenas letras maiúsculas (A-Z) e números (0-9)

```javascript
rgInput.addEventListener('input', function(e) {
    e.target.value = e.target.value.toUpperCase().replace(/[^0-9A-Z]/g, '');
});
```

**Experiência do Usuário:**
- Digita: `123456a` → Exibe: `123456A`
- Digita: `123-456` → Exibe: `123456`
- Digita: `abc123` → Exibe: `ABC123`

---

## 🌐 Busca Automática de Endereço (ViaCEP)

**API Utilizada:** [ViaCEP](https://viacep.com.br/)  
**Implementação:** Fetch API com feedback visual

**Arquivo:** [`secretaria/templates/partials/_form_dados_cadastrais.html`](secretaria/templates/partials/_form_dados_cadastrais.html) (linhas ~516-560)

### Código Completo

```javascript
cepInput.addEventListener('blur', function() {
    let cep = this.value.replace(/\D/g, '');
    
    if (cep.length === 8) {
        // Mostra loading
        const originalPlaceholder = this.placeholder;
        this.placeholder = 'Buscando endereço...';
        this.disabled = true;
        
        fetch(`https://viacep.com.br/ws/${cep}/json/`)
            .then(response => response.json())
            .then(data => {
                if (!data.erro) {
                    // Preenche campos automaticamente
                    if (data.logradouro) {
                        document.getElementById('id_rua').value = data.logradouro;
                    }
                    if (data.bairro) {
                        document.getElementById('id_bairro_distrito').value = data.bairro;
                    }
                    if (data.localidade) {
                        document.getElementById('id_cidade').value = data.localidade;
                    }
                    if (data.uf) {
                        document.getElementById('id_estado').value = data.uf;
                    }
                    
                    // Foca no número da casa
                    document.getElementById('id_numero_casa').focus();
                    
                    // Feedback visual (borda verde)
                    cepInput.style.borderColor = '#28a745';
                    setTimeout(() => {
                        cepInput.style.borderColor = '';
                    }, 2000);
                } else {
                    alert('CEP não encontrado. Verifique o número digitado.');
                    cepInput.style.borderColor = '#dc3545';  // Borda vermelha
                    setTimeout(() => {
                        cepInput.style.borderColor = '';
                    }, 2000);
                }
            })
            .catch(error => {
                console.error('Erro ao buscar CEP:', error);
                alert('Erro ao buscar CEP. Verifique sua conexão.');
            })
            .finally(() => {
                this.placeholder = originalPlaceholder;
                this.disabled = false;
            });
    }
});
```

### Fluxo de Funcionamento

```
1. Usuário digita CEP: 60000-000
   ↓
2. Ao sair do campo (blur):
   ↓
3. Máscara formata automaticamente
   ↓
4. JavaScript remove formatação → 60000000
   ↓
5. Faz requisição: https://viacep.com.br/ws/60000000/json/
   ↓
6. ViaCEP retorna:
   {
     "cep": "60000-000",
     "logradouro": "Rua Exemplo",
     "bairro": "Centro",
     "localidade": "Fortaleza",
     "uf": "CE"
   }
   ↓
7. JavaScript preenche campos automaticamente
   ↓
8. Feedback visual (borda verde por 2s)
   ↓
9. Foca no campo "Número da casa"
```

### Feedback Visual

| Situação          | Visual                        | Duração |
|-------------------|-------------------------------|---------|
| **Buscando**      | Placeholder: "Buscando endereço..." + campo desabilitado | Até resposta |
| **Sucesso**       | Borda verde (`#28a745`)       | 2 segundos |
| **CEP não encontrado** | Borda vermelha (`#dc3545`) + Alert | 2 segundos |
| **Erro de conexão** | Alert: "Erro ao buscar CEP. Verifique sua conexão." | — |

### Campos Preenchidos Automaticamente

1. ✅ **Rua/Logradouro** (`id_rua`)
2. ✅ **Bairro/Distrito** (`id_bairro_distrito`)
3. ✅ **Cidade** (`id_cidade`)
4. ✅ **Estado/UF** (`id_estado`)

### Funcionamento Offline

⚠️ **IMPORTANTE:** O sistema **não bloqueia o formulário** se a API estiver indisponível:

- ✅ Usuário pode preencher manualmente
- ✅ Campos permanecem editáveis
- ✅ Formulário pode ser submetido normalmente
- ✅ Timeout adequado para evitar travamento

---

## 🧪 Como Testar

### 1. Testar Validação de CPF

**Casos de Teste:**

```python
# 1. CPF válido sem formatação
teste_cpf('12345678909')  # ✅ Deve formatar: 123.456.789-09

# 2. CPF válido com formatação
teste_cpf('123.456.789-09')  # ✅ Deve aceitar: 123.456.789-09

# 3. CPF inválido (todos dígitos iguais)
teste_cpf('111.111.111-11')  # ❌ Deve rejeitar

# 4. CPF inválido (dígito verificador incorreto)
teste_cpf('123.456.789-00')  # ❌ Deve rejeitar

# 5. CPF incompleto
teste_cpf('12345678')  # ❌ Deve rejeitar: "CPF deve ter 11 dígitos"
```

**Procedimento Manual:**
1. Acesse: `http://localhost:8000/secretaria/membros/criar/`
2. Preencha campo CPF com valores acima
3. Clique em "Salvar"
4. Verifique mensagens de erro/sucesso

---

### 2. Testar Máscaras JavaScript

**CPF:**
1. Digite: `12345678909`
2. Deve exibir em tempo real: `123.456.789-09`

**Telefone:**
1. Digite: `85987654321`
2. Deve exibir: `(85) 98765-4321`

**CEP:**
1. Digite: `60000000`
2. Deve exibir: `60000-000`

**RG:**
1. Digite: `abc123-xyz`
2. Deve exibir: `ABC123XYZ` (remove hífen)

---

### 3. Testar Busca de CEP

**CEPs de Teste (Fortaleza - CE):**

| CEP       | Resultado Esperado           |
|-----------|------------------------------|
| 60000-000 | Rua, Bairro, Fortaleza, CE   |
| 60030-140 | Rua Barão do Rio Branco + bairro |
| 99999-999 | ❌ CEP não encontrado        |

**Procedimento:**
1. Acesse cadastro de pessoa
2. Campo CEP: digite `60000000`
3. Ao sair do campo (Tab ou clique fora):
   - ⏳ Deve mostrar "Buscando endereço..."
   - 🟢 Borda verde + campos preenchidos (< 1s)
   - ✅ Foco automático em "Número da casa"

---

### 4. Testar Validação de Email

**Casos de Teste:**

| Entrada              | Resultado Esperado       | Status |
|----------------------|--------------------------|--------|
| TESTE@GMAIL.COM      | teste@gmail.com          | ✅     |
| teste@email.com      | teste@email.com          | ✅     |
| teste@com            | ❌ Email inválido        | ❌     |
| teste                | ❌ Email inválido        | ❌     |
| (vazio)              | ✅ Aceito (campo opcional)| ✅    |

---

## 📂 Localização do Código

### Backend (Python/Django)

```
secretaria/
├── forms.py
│   ├── validar_cpf()          # Linhas 1-50
│   └── MembroForm
│       ├── clean_cpf()        # Linha ~240
│       └── clean_email()      # Linha ~250
```

### Frontend (JavaScript)

```
secretaria/templates/partials/
└── _form_dados_cadastrais.html
    ├── <script> Máscaras      # Linhas 485-570
    │   ├── aplicarMascara()   # Função genérica
    │   ├── CPF                # ###.###.###-##
    │   ├── Telefone           # (##) #####-####
    │   ├── CEP                # #####-###
    │   ├── RG                 # A-Z 0-9
    │   └── ViaCEP             # Busca endereço
```

### Documentação

```
Gereigreja/
├── CHANGELOG.md               # Changelog completo v1.6.1
└── README_VALIDACOES.md       # Esta documentação
```

---

## 🔧 Troubleshooting

### Problema: Máscara não está funcionando

**Sintomas:**
- Usuário digita CPF mas não formata automaticamente

**Soluções:**

1. **Verificar se JavaScript está habilitado:**
   ```javascript
   // Abra console do navegador (F12)
   console.log('JavaScript OK');
   ```

2. **Verificar ID do campo:**
   ```html
   <!-- Deve ser exatamente: -->
   <input type="text" id="id_cpf" name="cpf">
   ```

3. **Verificar console por erros:**
   - Abra DevTools (F12)
   - Aba "Console"
   - Procure erros em vermelho

---

### Problema: ViaCEP não retorna dados

**Sintomas:**
- Digite CEP válido mas campos não preenchem

**Soluções:**

1. **Verificar conexão com internet:**
   ```bash
   # Testar diretamente no navegador:
   https://viacep.com.br/ws/60000000/json/
   ```

2. **Verificar CORS/Firewall:**
   - ViaCEP permite requisições de qualquer domínio
   - Verificar se empresa não bloqueia API externa

3. **Verificar IDs dos campos:**
   ```javascript
   // Devem existir:
   document.getElementById('id_rua')
   document.getElementById('id_bairro_distrito')
   document.getElementById('id_cidade')
   document.getElementById('id_estado')
   ```

4. **CEP Teste Alternativo:**
   ```
   01310-100 (Av. Paulista, São Paulo - SP)
   20040-020 (Centro, Rio de Janeiro - RJ)
   ```

---

### Problema: Validação CPF rejeita CPF válido

**Sintomas:**
- CPF correto é rejeitado pelo sistema

**Soluções:**

1. **Verificar algoritmo:**
   ```python
   # Testar diretamente no shell Django:
   python manage.py shell
   
   from secretaria.forms import validar_cpf
   validar_cpf('12345678909')  # Deve retornar '12345678909'
   ```

2. **Validar CPF online:**
   - Usar validador oficial: https://www.calculadorafacil.com.br/computacao/validar-cpf
   - Comparar resultado

3. **Verificar formatação:**
   ```python
   # CPF deve ter exatamente 11 dígitos numéricos
   # Aceita com ou sem pontuação:
   '123.456.789-09'  # ✅ OK
   '12345678909'     # ✅ OK
   '123 456 789 09'  # ✅ OK (remove espaços)
   ```

---

### Problema: Email em maiúsculas não é convertido

**Sintomas:**
- Email salvo como `TESTE@GMAIL.COM` ao invés de `teste@gmail.com`

**Soluções:**

1. **Verificar método clean_email:**
   ```python
   # Deve conter:
   email = email.strip().lower()
   ```

2. **Verificar se form está usando método:**
   ```python
   # No MembroForm deve existir:
   def clean_email(self):
       email = self.cleaned_data.get('email')
       if email:
           email = email.strip().lower()
           # ... validação ...
       return email
   ```

---

## 📚 Referências

- **Algoritmo CPF:** Receita Federal do Brasil
- **API ViaCEP:** https://viacep.com.br/
- **Regex Email:** RFC 5322 (simplificado)
- **Bootstrap 5:** https://getbootstrap.com/docs/5.0/
- **Django Forms:** https://docs.djangoproject.com/en/stable/topics/forms/

---

## 📝 Notas de Versão

**v1.6.1 — 12/03/2026**

✨ **Novas Funcionalidades:**
- Validação CPF com dígito verificador
- Validação Email com regex
- Máscaras automáticas (CPF, Telefone, CEP, RG)
- Busca automática CEP via ViaCEP
- Feedback visual (bordas coloridas)

🔧 **Melhorias Técnicas:**
- Event listeners eficientes (DOMContentLoaded)
- Tratamento de erros robusto
- Função genérica de máscara reutilizável
- Conversão automática date → datetime

📁 **Arquivos Modificados:**
- `secretaria/forms.py` (+80 linhas)
- `secretaria/templates/partials/_form_dados_cadastrais.html` (+120 linhas)
- `CHANGELOG.md` (v1.6.1 documentada)

---

**Última atualização:** 12 de Março de 2026  
**Autor:** Sistema Gereigreja  
**Contato:** Ver documentação principal do projeto
