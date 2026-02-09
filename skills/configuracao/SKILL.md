---
name: "configurando-sistema"
description: "Configura organizações, usuários, permissões e integrações. Use para ajustes de sistema, permissões ou configurações gerais."
---

# Quando Usar Esta Skill

Use esta skill quando:
- Configurar organizações e igrejas
- Gerenciar usuários e permissões
- Configurar integrações externas (Cloudinary, Supabase)
- Ajustar parâmetros do sistema
- Personalizar interface por organização

## Estrutura de Dados

### Organização
```python
class Organizacao(models.Model):
    nome = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18)
    endereco = models.CharField(max_length=300)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to='logos/')
    plano = models.ForeignKey(Plano)
    ativo = models.BooleanField(default=True)
```

### Usuário com Permissões
```python
from django.contrib.auth.models import User, Permission

class PerfilUsuario(models.Model):
    PAPEL_CHOICES = [
        ('admin', 'Administrador'),
        ('secretaria', 'Secretaria'),
        ('tesoureiro', 'Tesoureiro'),
        ('lider', 'Líder'),
        ('membro', 'Membro')
    ]
    
    usuario = models.OneToOneField(User)
    organizacao = models.ForeignKey(Organizacao)
    papel = models.CharField(max_length=20, choices=PAPEL_CHOICES)
    telefone = models.CharField(max_length=20)
```

## Permissões por Papel

### Administrador
- Acesso total ao sistema
- Gerenciar usuários e permissões
- Configurar organização
- Ver todos os relatórios

### Secretaria
- Cadastrar/editar pessoas
- Gerenciar famílias
- Ver relatórios de secretaria
- Registrar visitas

### Tesoureiro
- Gerenciar financeiro
- Criar receitas/despesas
- Ver relatórios financeiros
- Fazer fechamento de caixa

### Líder
- Ver membros do seu grupo
- Registrar presenças
- Criar eventos

### Membro
- Ver seus próprios dados
- Inscrever-se em eventos
- Ver comunicados

## Exemplos de Uso

### Criar Organização
```python
organizacao = Organizacao.objects.create(
    nome='Igreja Batista Central',
    cnpj='12.345.678/0001-90',
    endereco='Av. Principal, 1000',
    telefone='(11) 1234-5678',
    email='contato@igreja.com',
    plano=plano_premium,
    ativo=True
)
```

### Criar Usuário com Permissões
```python
from django.contrib.auth.models import User

def criar_usuario_secretaria(username, email, organizacao):
    # Criar usuário Django
    user = User.objects.create_user(
        username=username,
        email=email,
        password='senha_temporaria'
    )
    
    # Criar perfil
    perfil = PerfilUsuario.objects.create(
        usuario=user,
        organizacao=organizacao,
        papel='secretaria'
    )
    
    # Adicionar permissões específicas
    permissoes = Permission.objects.filter(
        codename__in=['add_pessoa', 'change_pessoa', 'view_pessoa']
    )
    user.user_permissions.add(*permissoes)
    
    return user
```

### Verificar Permissão
```python
def pode_editar_pessoa(usuario, pessoa):
    perfil = PerfilUsuario.objects.get(usuario=usuario)
    
    # Admin pode tudo
    if perfil.papel == 'admin':
        return True
    
    # Secretaria pode editar da mesma organização
    if perfil.papel == 'secretaria':
        return pessoa.organizacao == perfil.organizacao
    
    # Próprio usuário pode editar seus dados
    if pessoa.usuario == usuario:
        return True
    
    return False
```

## Configurações do Django (settings.py)

### Cloudinary (Mídia)
```python
import cloudinary

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### Supabase (Banco)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('SUPABASE_DB_NAME'),
        'USER': os.getenv('SUPABASE_DB_USER'),
        'PASSWORD': os.getenv('SUPABASE_DB_PASSWORD'),
        'HOST': os.getenv('SUPABASE_DB_HOST'),
        'PORT': '5432',
    }
}
```

### E-mail (Gmail)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
```

## Variáveis de Ambiente (.env)

```bash
# Django
DJANGO_SECRET_KEY=sua-chave-secreta-aqui
DJANGO_DEBUG=False
ALLOWED_HOSTS=gereigreja.site,www.gereigreja.site

# Supabase
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=sua-senha
SUPABASE_DB_HOST=db.xxx.supabase.co

# Cloudinary
CLOUDINARY_CLOUD_NAME=seu-cloud
CLOUDINARY_API_KEY=123456789
CLOUDINARY_API_SECRET=sua-secret

# E-mail
EMAIL_USER=seu-email@gmail.com
EMAIL_PASSWORD=sua-senha-app
```

## Scripts Úteis

### Verificar Saúde do Sistema
```bash
python skills/configuracao/scripts/health_check.py
```

Verifica automaticamente:
- ✅ Conexão com banco de dados
- ✅ Uso de memória e disco
- ✅ Existência de backups recentes
- ✅ Logs de erro

## Boas Práticas

1. **Nunca commitar .env** - adicionar ao .gitignore
2. **Usar variáveis de ambiente** para credenciais
3. **DEBUG=False em produção**
4. **Permissões granulares** - princípio do menor privilégio
5. **Logs de auditoria** - registrar alterações em configurações
6. **Backup de configurações** antes de mudanças críticas
7. **Testar permissões** antes de deploy
8. **Health checks regulares** - rodar script semanalmente
