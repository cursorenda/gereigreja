# c:\Gereigreja\core\middleware.py
from configuracao.models import Igreja
# Assumindo que sua função get_allowed_churches_for_user está em financeiro.utils
# Se você a moveu para um local mais central (ex: core.utils), ajuste o import abaixo.
from financeiro.utils import get_allowed_churches_for_user 
import logging

logger = logging.getLogger(__name__)

class ActiveChurchMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.igreja_ativa = None # Inicializa o atributo no request

        # Só processa para usuários autenticados, com perfil e que não sejam superusuários
        if request.user.is_authenticated and \
           hasattr(request.user, 'perfil') and \
           request.user.perfil and \
           not request.user.is_superuser:
            
            igreja_ativa_id = request.session.get('igreja_ativa_id')
            allowed_churches = Igreja.objects.none() # Inicializa como queryset vazio

            try:
                # É importante obter as igrejas permitidas a cada requisição ou de um cache confiável,
                # pois as permissões podem mudar.
                allowed_churches = get_allowed_churches_for_user(request.user)
            except Exception as e:
                logger.error(f"Erro ao obter igrejas permitidas para o usuário {request.user.username} no ActiveChurchMiddleware: {e}")
                # allowed_churches permanece como queryset vazio, o que é seguro.

            if igreja_ativa_id:
                try:
                    # Verifica se a igreja da sessão ainda está entre as permitidas
                    igreja = allowed_churches.get(pk=igreja_ativa_id)
                    request.igreja_ativa = igreja
                except Igreja.DoesNotExist:
                    # Igreja não encontrada ou não mais permitida, limpar da sessão
                    logger.warning(f"Igreja ativa ID {igreja_ativa_id} na sessão do usuário {request.user.username} não é válida ou não é mais permitida. Removendo da sessão.")
                    if 'igreja_ativa_id' in request.session:
                        del request.session['igreja_ativa_id']
                except Exception as e:
                    logger.error(f"Erro ao tentar obter igreja ativa ID {igreja_ativa_id} para usuário {request.user.username}: {e}")
            # Opcional: Lógica para definir uma igreja padrão se nenhuma estiver na sessão
            # e o usuário tiver acesso a apenas uma. Pode ser adicionado depois.
            # elif allowed_churches.count() == 1:
            #     igreja_unica = allowed_churches.first()
            #     request.igreja_ativa = igreja_unica
            #     request.session['igreja_ativa_id'] = igreja_unica.pk
            #     logger.info(f"Igreja ativa definida automaticamente para {igreja_unica.nome_igreja} para o usuário {request.user.username}.")

        response = self.get_response(request)
        return response

