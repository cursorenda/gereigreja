"""Observabilidade dos fluxos da Escola Bíblica."""

import logging
import time
from functools import wraps


logger = logging.getLogger(__name__)


def log_ebd_endpoint(action):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            started_at = time.perf_counter()
            status_code = 500
            user_id = getattr(request.user, 'pk', None)
            igreja_ativa_id = getattr(getattr(request, 'igreja_ativa', None), 'pk', None)
            try:
                response = view_func(request, *args, **kwargs)
                status_code = getattr(response, 'status_code', 200)
                return response
            except Exception:
                logger.exception(
                    'ebd.endpoint.error action=%s method=%s path=%s user_id=%s igreja_ativa_id=%s',
                    action, request.method, request.path, user_id, igreja_ativa_id,
                )
                raise
            finally:
                logger.info(
                    'ebd.endpoint.metric action=%s method=%s path=%s status=%s elapsed_ms=%.2f user_id=%s igreja_ativa_id=%s',
                    action, request.method, request.path, status_code,
                    (time.perf_counter() - started_at) * 1000, user_id, igreja_ativa_id,
                )
        return _wrapped
    return decorator


def log_ebd_audit_event(request, action, **extra):
    igreja_ativa = getattr(request, 'igreja_ativa', None)
    payload = {
        'action': action,
        'user_id': getattr(request.user, 'pk', None),
        'igreja_ativa_id': getattr(igreja_ativa, 'pk', None),
        **extra,
    }
    logger.info('ebd.audit %s', ' '.join(f'{key}={value}' for key, value in payload.items()))
