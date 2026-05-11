"""
Ponto de entrada do admin do modulo contas.
As classes admin estao organizadas em submodulos por dominio:
  - admin_contas.py: Group (override), Convite, NotaUsuario, ConsentimentoLGPD
"""
# noqa: F401 - imports necessarios para que Django registre os admins via AppConfig
from .admin_contas import (  # noqa: F401
    ConsentimentoLGPDAdmin,
    ConviteAdmin,
    GroupAdminProtegido,
    NotaUsuarioAdmin,
)
