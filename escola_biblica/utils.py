# Utilitários para Escola Bíblica Dominical

def calcular_frequencia_aluno(aluno):
    total = aluno.frequencia_set.count()
    presentes = aluno.frequencia_set.filter(presente=True).count()
    return {'total': total, 'presentes': presentes, 'percentual': (presentes/total*100) if total else 0}
