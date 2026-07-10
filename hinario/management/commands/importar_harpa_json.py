"""
Importa hinos em JSON para HinoGlobal com compliance-first.

Politica aplicada:
- license_status = pending_review (por padrao)
- blocked_for_public_use = True (sempre no seed inicial)
- reviewed_by/reviewed_at = None
- registro de auditoria com action='imported'

Exemplo:
  python manage.py importar_harpa_json \
    --file "C:/Users/ju_ju/Downloads/Harpa-Crista-JSON-640-Hinos-Completa-main/harpa_crista_640_hinos.json" \
    --declaracao-legal "Importacao para revisao juridica interna; proibida exibicao publica sem aprovacao." \
    --source-origin "DanielLiberato/Harpa-Crista-JSON-640-Hinos-Completa"
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from hinario.models import HinoAuditLog, HinoGlobal


class Command(BaseCommand):
    help = (
        "Importa JSON da Harpa para HinoGlobal com bloqueio padrao e trilha de auditoria."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            required=True,
            help="Caminho absoluto do arquivo JSON de hinos.",
        )
        parser.add_argument(
            "--colecao",
            default="Harpa Crista",
            help="Nome da colecao a gravar no banco. Padrao: Harpa Crista",
        )
        parser.add_argument(
            "--source-origin",
            default="JSON Externo",
            help="Identificador da origem de dados para rastreabilidade.",
        )
        parser.add_argument(
            "--declaracao-legal",
            required=True,
            help=(
                "Declaracao obrigatoria de base legal/escopo de uso. "
                "Exemplo: 'Importacao para revisao juridica interna; proibida exibicao publica sem aprovacao.'"
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula importacao sem salvar no banco.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Importa apenas os N primeiros hinos (apos filtros).",
        )
        parser.add_argument(
            "--from-num",
            type=int,
            default=None,
            help="Numero inicial para recorte (inclusivo).",
        )
        parser.add_argument(
            "--to-num",
            type=int,
            default=None,
            help="Numero final para recorte (inclusivo).",
        )
        parser.add_argument(
            "--upsert",
            action="store_true",
            help="Atualiza registros existentes (mesma colecao+numero).",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"])
        colecao = options["colecao"].strip() or "Harpa Crista"
        source_origin = options["source_origin"].strip() or "JSON Externo"
        declaracao_legal = options["declaracao_legal"].strip()
        dry_run = options["dry_run"]
        limit = options["limit"]
        from_num = options["from_num"]
        to_num = options["to_num"]
        upsert = options["upsert"]

        if not declaracao_legal:
            raise CommandError("--declaracao-legal e obrigatoria e nao pode ser vazia.")

        if not file_path.exists() or not file_path.is_file():
            raise CommandError(f"Arquivo nao encontrado: {file_path}")

        if from_num is not None and to_num is not None and from_num > to_num:
            raise CommandError("--from-num nao pode ser maior que --to-num.")

        payload = self._load_json(file_path)
        hinos = self._normalize_entries(payload)

        if from_num is not None:
            hinos = [h for h in hinos if h["numero"] >= from_num]
        if to_num is not None:
            hinos = [h for h in hinos if h["numero"] <= to_num]
        if limit is not None:
            hinos = hinos[:limit]

        if not hinos:
            self.stdout.write(self.style.WARNING("Nenhum hino valido encontrado para importacao."))
            return

        self.stdout.write(self.style.HTTP_INFO("\n=== Importacao de Hinos (compliance-first) ==="))
        self.stdout.write(f"Arquivo: {file_path}")
        self.stdout.write(f"Colecao: {colecao}")
        self.stdout.write(f"Origem: {source_origin}")
        self.stdout.write(f"Declaracao legal: {declaracao_legal}")
        self.stdout.write(f"Dry-run: {'SIM' if dry_run else 'NAO'}")
        self.stdout.write(f"Modo upsert: {'SIM' if upsert else 'NAO'}")
        self.stdout.write(f"Quantidade alvo: {len(hinos)}\n")

        created = 0
        updated = 0
        skipped = 0
        invalid = 0

        if dry_run:
            self._print_preview(hinos)
            self.stdout.write(self.style.SUCCESS("\nDry-run concluido. Nenhum registro foi salvo."))
            return

        with transaction.atomic():
            for hino in hinos:
                try:
                    status = self._upsert_hino(
                        colecao=colecao,
                        source_origin=source_origin,
                        declaracao_legal=declaracao_legal,
                        hino=hino,
                        allow_update=upsert,
                    )
                    if status == "created":
                        created += 1
                    elif status == "updated":
                        updated += 1
                    else:
                        skipped += 1
                except Exception as exc:
                    invalid += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"[IGNORADO] Hino {hino.get('numero')} - erro: {exc}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS("\nImportacao concluida com sucesso."))
        self.stdout.write(f"Criados: {created}")
        self.stdout.write(f"Atualizados: {updated}")
        self.stdout.write(f"Ignorados: {skipped}")
        self.stdout.write(f"Invalidos: {invalid}")

    def _load_json(self, file_path: Path) -> dict:
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            return json.loads(file_path.read_text(encoding="latin-1"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"JSON invalido: {exc}") from exc

    def _normalize_entries(self, payload: dict) -> list[dict]:
        entries = []
        for raw_key, item in payload.items():
            if not self._is_hino_key(raw_key):
                continue
            numero = int(raw_key)
            if numero <= 0:
                continue

            titulo = self._extract_titulo(item.get("hino", ""), numero)
            letra = self._build_letra(item.get("verses"), item.get("coro"))

            if not titulo or not letra:
                continue

            entries.append(
                {
                    "numero": numero,
                    "titulo": titulo,
                    "letra": letra,
                    "cifra": None,
                }
            )

        entries.sort(key=lambda x: x["numero"])
        return entries

    def _is_hino_key(self, raw_key: str) -> bool:
        return bool(re.fullmatch(r"-?\d+", str(raw_key)))

    def _extract_titulo(self, hino_field: str, numero: int) -> str:
        text = self._normalize_text(hino_field)
        if not text:
            return f"Hino {numero}"

        match = re.match(r"^\s*\d+\s*[-:\u2013]\s*(.+)$", text)
        if match:
            return match.group(1).strip()
        return text.strip()

    def _build_letra(self, verses, coro: str | None) -> str:
        partes = []

        if isinstance(verses, dict):
            for key in sorted(verses.keys(), key=lambda k: int(k) if str(k).isdigit() else 9999):
                verso = self._normalize_text(verses.get(key, ""))
                if verso:
                    partes.append(f"{key}. {verso}")

        if coro:
            coro_txt = self._normalize_text(coro)
            if coro_txt:
                partes.append(f"Coro: {coro_txt}")

        return "\n\n".join(partes).strip()

    def _normalize_text(self, value: str) -> str:
        if value is None:
            return ""
        text = str(value)
        text = re.sub(r"<\s*br\s*/?\s*>", "\n", text, flags=re.IGNORECASE)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _upsert_hino(self, colecao: str, source_origin: str, declaracao_legal: str, hino: dict, allow_update: bool) -> str:
        existente = HinoGlobal.objects.all_including_deleted().filter(
            colecao=colecao,
            numero=hino["numero"],
        ).first()

        if existente and not allow_update:
            return "skipped"

        if existente and existente.deleted_at is not None:
            existente.deleted_at = None

        if existente:
            existente.titulo = hino["titulo"]
            existente.letra = hino["letra"]
            existente.cifra = hino["cifra"]
            existente.ativo = True
            existente.license_status = "pending_review"
            existente.blocked_for_public_use = True
            existente.is_public_domain = False
            existente.rights_holder = None
            existente.license_reference = None
            existente.license_expires_at = None
            existente.legal_notes = declaracao_legal
            existente.reviewed_by = None
            existente.reviewed_at = None
            existente.source_origin = source_origin
            existente.save()
            self._registrar_auditoria_import(existente, declaracao_legal)
            return "updated"

        novo = HinoGlobal.objects.create(
            colecao=colecao,
            numero=hino["numero"],
            titulo=hino["titulo"],
            letra=hino["letra"],
            cifra=hino["cifra"],
            ativo=True,
            is_public_domain=False,
            license_status="pending_review",
            blocked_for_public_use=True,
            legal_notes=declaracao_legal,
            source_origin=source_origin,
        )
        self._registrar_auditoria_import(novo, declaracao_legal)
        return "created"

    def _registrar_auditoria_import(self, hino: HinoGlobal, declaracao_legal: str) -> None:
        after_json = {
            "id": hino.id,
            "numero": hino.numero,
            "titulo": hino.titulo,
            "colecao": hino.colecao,
            "license_status": hino.license_status,
            "blocked_for_public_use": hino.blocked_for_public_use,
        }
        HinoAuditLog.objects.create(
            tenant_igreja=None,
            target_type="global",
            target_id=hino.id,
            action="imported",
            after_json=after_json,
            reason=f"Importacao inicial com declaracao legal: {declaracao_legal}",
            actor_user=None,
        )

    def _print_preview(self, hinos: list[dict]) -> None:
        self.stdout.write(self.style.WARNING("Amostra dos primeiros 5 hinos normalizados:"))
        for hino in hinos[:5]:
            preview = hino["letra"][:90].replace("\n", " ")
            self.stdout.write(
                f"  - #{hino['numero']} {hino['titulo']} | letra: {preview}..."
            )
