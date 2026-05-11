"""
Ponto de entrada do admin do modulo escola_biblica.
As classes admin estao organizadas em submodulos por dominio:
  - admin_estrutura.py : AnoLetivo, Classe, Turma
  - admin_alunos.py    : CadastroAluno, Aluno, Frequencia
  - admin_aulas.py     : Licao, Avaliacao
"""
# noqa: F401 - imports necessarios para que Django registre os admins via AppConfig
from .admin_alunos import (  # noqa: F401
    AlunoAdmin,
    CadastroAlunoAdmin,
    FrequenciaAdmin,
)
from .admin_aulas import (  # noqa: F401
    AvaliacaoAdmin,
    LicaoAdmin,
)
from .admin_estrutura import (  # noqa: F401
    AnoLetivoAdmin,
    ClasseAdmin,
    TurmaAdmin,
)
