from secretaria.models import Membro

# Conte quantos membros ativos do tipo 'Membro' existem
print(Membro.objects.filter(status_pessoa__considerar_ativo_relatorios=True, tipo_pessoa__nome__iexact="Membro").count())

# Liste os nomes e ids para conferência
for m in Membro.objects.filter(status_pessoa__considerar_ativo_relatorios=True, tipo_pessoa__nome__iexact="Membro"):
    print(m.id, m.nome, m.status_pessoa, m.tipo_pessoa)
