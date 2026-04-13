import re
from datetime import datetime
from pathlib import Path

from configuracao.models import AtualizacaoSistema

changelog = Path("c:/Gereigreja/CHANGELOG.md").read_text(encoding="utf-8")
pattern = re.compile(
    r"^##\s+v(?P<versao>\d+\.\d+\.\d+)\s+—\s+(?P<data>\d{2}/\d{2}/\d{4})\n"
    r"(?P<corpo>.*?)(?=^##\s+v\d+\.\d+\.\d+\s+—|\Z)",
    re.M | re.S,
)

criados = 0
atualizados = 0
ignorados = 0

for match in pattern.finditer(changelog):
    versao = match.group("versao")
    partes = tuple(int(x) for x in versao.split("."))

    # Publica somente versões ainda não cadastradas no admin histórico (>= 1.8.24)
    if partes < (1, 8, 24):
        ignorados += 1
        continue

    data_publicacao = datetime.strptime(match.group("data"), "%d/%m/%Y").date()
    corpo = match.group("corpo").strip()

    primeira_linha = next(
        (linha.strip() for linha in corpo.splitlines() if linha.strip()),
        f"Atualizacao do Sistema v{versao}",
    )
    titulo = re.sub(r"^[^A-Za-z0-9À-ÿ]+", "", primeira_linha)
    titulo = titulo.replace("**", "").strip()[:200] or f"Atualizacao do Sistema v{versao}"

    _, created = AtualizacaoSistema.objects.update_or_create(
        versao=versao,
        defaults={
            "titulo": titulo,
            "data_publicacao": data_publicacao,
            "conteudo": corpo,
            "publicado": True,
        },
    )

    if created:
        criados += 1
    else:
        atualizados += 1

print(f"criados={criados} atualizados={atualizados} ignorados={ignorados}")
