"""
Teste direto da função metricas_produto
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from configuracao.admin_metrics import metricas_produto
from django.test import RequestFactory
from django.contrib.auth.models import User

# Criar request fake
factory = RequestFactory()
request = factory.get('/admin/api/metricas-produto/')

# Criar user staff fake
user = User.objects.filter(is_staff=True).first()
if not user:
    print("❌ Nenhum usuário staff encontrado")
    exit(1)

request.user = user

try:
    response = metricas_produto(request)
    print("✅ Resposta da API:")
    print(response.content.decode('utf-8'))
except Exception as e:
    print(f"❌ Erro ao executar metricas_produto:")
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensagem: {str(e)}")
    
    import traceback
    print("\n📋 Traceback completo:")
    traceback.print_exc()
