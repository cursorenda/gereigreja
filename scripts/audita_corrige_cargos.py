# Script para auditar e corrigir cargos ativos de membros no Gereigreja
# Uso: python manage.py shell < scripts/audita_corrige_cargos.py

from secretaria.models import Membro, Cargo, MembroCargo
from django.utils import timezone

# 1. Identifique o membro pelo nome ou email
NOME_MEMBRO = "Maryellen Coutinho Cunha Barbosa"
EMAIL_MEMBRO = "maryellenbarbosa16@gmail.com"

# 2. Busque o membro
membro = Membro.objects.filter(nome=NOME_MEMBRO).first()
if not membro:
    membro = Membro.objects.filter(email=EMAIL_MEMBRO).first()

if not membro:
    print(f"Membro '{NOME_MEMBRO}' não encontrado.")
    exit(1)

print(f"Membro encontrado: {membro.nome} (ID: {membro.pk})")

# 3. Liste todos os cargos disponíveis
cargos = Cargo.objects.all()
print("Cargos disponíveis:")
for cargo in cargos:
    print(f"- {cargo.pk}: {cargo.nome}")

# 4. Liste todos os cargos já atribuídos ao membro
cargos_membro = MembroCargo.objects.filter(membro=membro)
print("\nCargos já atribuídos ao membro:")
for mc in cargos_membro:
    print(f"- {mc.cargo.nome} | Início: {mc.data_inicio} | Fim: {mc.data_fim}")

# 5. Corrija: para cada cargo desejado, crie/atualize para ficar ativo (data_fim=None)
# Exemplo: garantir que ela seja 'Secretário' e 'Professor de Escola Dominical' ativos
CARGOS_DESEJADOS = ["Secretário", "Professor de Escola Dominical"]

for nome_cargo in CARGOS_DESEJADOS:
    cargo = Cargo.objects.filter(nome__iexact=nome_cargo).first()
    if not cargo:
        print(f"Cargo '{nome_cargo}' não encontrado.")
        continue
    mc, created = MembroCargo.objects.get_or_create(membro=membro, cargo=cargo, defaults={
        'data_inicio': timezone.now().date(),
        'data_fim': None
    })
    if not created:
        if mc.data_fim is not None:
            mc.data_fim = None
            mc.save()
            print(f"Corrigido: cargo '{nome_cargo}' agora está ativo para {membro.nome}.")
        else:
            print(f"Cargo '{nome_cargo}' já está ativo para {membro.nome}.")
    else:
        print(f"Cargo '{nome_cargo}' atribuído como ativo para {membro.nome}.")

print("\nAuditoria e correção concluídas.")
