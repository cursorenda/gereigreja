# c:\Gereigreja\core\middleware.py
# NÃO importar models no topo para permitir servidor iniciar sem BD
import logging
from django.db import OperationalError, DatabaseError
from django.shortcuts import render

logger = logging.getLogger(__name__)

class ActiveChurchMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.igreja_ativa = None  # Inicializa o atributo no request
        request.igrejas_permitidas = None  # Escopo automático global

        if request.user.is_authenticated:
            # Import lazy para permitir servidor iniciar sem BD
            from configuracao.models import Igreja
            from core.utils import get_igrejas_permitidas

            igreja_ativa_id = request.session.get('igreja_ativa_id')
            allowed_churches = Igreja.objects.none()

            try:
                if request.user.is_superuser:
                    allowed_churches = Igreja.objects.all()
                else:
                    perfil = getattr(request.user, 'perfil', None) or getattr(request.user, 'perfil_usuario', None)
                    ministerio = getattr(perfil, 'ministerio', None)
                    if ministerio:
                        allowed_churches = get_igrejas_permitidas(request.user, ministerio)
                request.igrejas_permitidas = allowed_churches
            except Exception as e:
                logger.error(f"Erro ao obter igrejas permitidas para o usuário {request.user.username} no ActiveChurchMiddleware: {e}")
                request.igrejas_permitidas = allowed_churches

            # Só controla igreja ativa para usuários não superusuários
            if not request.user.is_superuser:
                if igreja_ativa_id:
                    try:
                        # Verifica se a igreja da sessão ainda está entre as permitidas
                        igreja = allowed_churches.get(pk=igreja_ativa_id)
                        request.igreja_ativa = igreja
                        logger.info(f"[ActiveChurchMiddleware] igreja_ativa definida: {igreja.nome_igreja} (ID: {igreja.pk}) para usuário {request.user.username}")
                    except Igreja.DoesNotExist:
                        # Igreja não encontrada ou não mais permitida, limpar da sessão
                        logger.warning(f"Igreja ativa ID {igreja_ativa_id} na sessão do usuário {request.user.username} não é válida ou não é mais permitida. Removendo da sessão.")
                        if 'igreja_ativa_id' in request.session:
                            del request.session['igreja_ativa_id']
                    except Exception as e:
                        logger.error(f"Erro ao tentar obter igreja ativa ID {igreja_ativa_id} para usuário {request.user.username}: {e}")
                # Se não houver igreja ativa na sessão e o usuário tiver acesso a apenas uma igreja, define automaticamente
                elif allowed_churches.count() == 1:
                    igreja_unica = allowed_churches.first()
                    request.igreja_ativa = igreja_unica
                    request.session['igreja_ativa_id'] = igreja_unica.pk
                    logger.info(f"[ActiveChurchMiddleware] igreja_ativa definida automaticamente: {igreja_unica.nome_igreja} (ID: {igreja_unica.pk}) para usuário {request.user.username}")

            logger.info(f"[ActiveChurchMiddleware] Valor final de request.igreja_ativa: {getattr(request.igreja_ativa, 'nome_igreja', None)}")

        response = self.get_response(request)
        return response


class VerificarGruposUsuarioMiddleware:
    """
    Middleware que verifica se usuários autenticados têm grupos/papéis.
    Se não tiverem, redireciona para página "Aguardando Permissões".
    
    Isso evita que usuários sem permissões fiquem navegando em páginas
    quebradas ou com mensagens de erro inconsistentes.
    """
    
    # URLs que usuários SEM grupos podem acessar
    # (para evitar loops de redirecionamento)
    URLS_PERMITIDAS = [
        '/contas/aguardando-acesso/',
        '/configuracao/perfil/',
        '/configuracao/perfil/editar/',
        '/contas/alterar-senha/',
        '/contas/alterar-senha/concluido/',
        '/contas/logout/',
        '/static/',
        '/media/',
        '/admin/',  # Django admin é separado
        '/teste-permissao/',  # Permite todas as rotas de teste de permissão
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Se não está autenticado → deixa passar (vai pro login)
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # 2. Se é superuser → deixa passar (acesso total)
        if request.user.is_superuser:
            return self.get_response(request)
        
        # 3. Se a URL está na lista de permitidas → deixa passar
        if any(request.path.startswith(url) for url in self.URLS_PERMITIDAS):
            return self.get_response(request)
        
        # 4. Verifica se tem permissão mínima (membro comum ou superior)
        from contas.constants import user_has_permission_level_or_higher, MEMBRO_COMUM
        if not user_has_permission_level_or_higher(request.user, MEMBRO_COMUM):
            # Não tem permissão reconhecida → redireciona para página de aguardando
            from django.shortcuts import redirect
            return redirect('contas:aguardando_acesso')
        
        # 5. Tem grupos → deixa passar normalmente
        response = self.get_response(request)
        return response

class PermissionDeniedMiddleware:
    """
    Middleware que captura exceções PermissionDenied e renderiza página 403 personalizada
    em vez de redirecionar para login.
    
    Isso melhora a UX mostrando ao usuário que ele JÁ ESTÁ LOGADO mas não tem permissão,
    em vez de enviar para a página de login (confuso).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Captura PermissionDenied e renderiza 403.html.
        """
        from django.core.exceptions import PermissionDenied
        from django.shortcuts import render
        
        if isinstance(exception, PermissionDenied):
            # Usuário está logado mas não tem permissão
            # Renderiza 403.html personalizado em vez de redirecionar para login
            return render(request, '403.html', status=403)
        
        # Outras exceções não são tratadas aqui
        return None


class DatabaseErrorMiddleware:
    """
    Middleware que captura erros de conexão com banco de dados e exibe
    página amigável em vez do erro genérico 500.
    
    Detecta erros como:
    - Connection timeout
    - Connection refused
    - Database server offline
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except (OperationalError, DatabaseError) as e:
            # Captura erros de banco de dados
            return self.handle_database_error(request, e)

    def process_exception(self, request, exception):
        """
        Captura exceções de banco de dados que ocorrem nas views.
        """
        if isinstance(exception, (OperationalError, DatabaseError)):
            return self.handle_database_error(request, exception)
        return None

    def handle_database_error(self, request, exception):
        """
        Renderiza página personalizada para erro de banco de dados.
        """
        error_message = str(exception).lower()
        
        # Detectar tipo específico de erro
        if any(keyword in error_message for keyword in ['timeout', 'timed out', '10060']):
            erro_tipo = 'timeout'
            titulo = '⏱️ Conexão Expirada'
            descricao = 'O servidor de banco de dados não respondeu a tempo.'
            detalhes = 'Isso pode indicar que o provedor de banco (Supabase) está temporariamente indisponível ou com lentidão extrema.'
        elif any(keyword in error_message for keyword in ['refused', 'could not connect', 'cannot connect']):
            erro_tipo = 'refused'
            titulo = '🔌 Conexão Recusada'
            descricao = 'Não foi possível conectar ao servidor de banco de dados.'
            detalhes = 'O serviço de banco de dados pode estar offline ou com problemas de firewall.'
        else:
            erro_tipo = 'generic'
            titulo = '💾 Erro no Banco de Dados'
            descricao = 'Ocorreu um problema ao tentar acessar o banco de dados.'
            detalhes = str(exception)[:200]  # Limita tamanho
        
        # Loga o erro para análise posterior
        logger.error(f"Erro de banco de dados capturado pelo middleware: {exception}")
        
        context = {
            'erro_tipo': erro_tipo,
            'titulo': titulo,
            'descricao': descricao,
            'detalhes': detalhes,
            'erro_completo': str(exception) if request.user.is_superuser else None,  # Só superuser vê detalhes
        }
        
        return render(request, 'database_error.html', context, status=503)