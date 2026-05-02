from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse

from configuracao.models import Igreja, Ministerio, PerfilUsuario


class _HrefParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attr_map = dict(attrs)
        href = (attr_map.get("href") or "").strip()
        if href:
            self.hrefs.append(href)


class IntegridadeLinksSistemaTest(TestCase):
    maxDiff = None

    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="linkcrawler",
            email="linkcrawler@gereigreja.local",
            password="123456",
        )

        self.ministerio = Ministerio.objects.create(
            nome_fantasia="Ministerio Links",
            administrador_principal=self.user,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            nome_igreja="Igreja Links",
            ministerio=self.ministerio,
        )

        perfil = PerfilUsuario.objects.create(
            user=self.user,
            ministerio=self.ministerio,
        )
        perfil.igrejas_permitidas.add(self.igreja)

        grupo_admin, _ = Group.objects.get_or_create(name="Admin Ministerio")
        self.user.groups.add(grupo_admin)

        self.client = Client()
        self.client.login(username="linkcrawler", password="123456")

        session = self.client.session
        session["igreja_ativa_id"] = self.igreja.pk
        session.save()

    def _status_ok(self, status_code):
        return status_code in {200, 301, 302, 303, 307, 308, 401, 403}

    def _normalize_internal_href(self, href):
        if not href:
            return None
        if href.startswith("#"):
            return None
        if href.lower().startswith("javascript:"):
            return None
        if href.lower().startswith("mailto:"):
            return None
        if href.lower().startswith("tel:"):
            return None
        if href.startswith("//"):
            return None

        parsed = urlparse(href)
        if parsed.scheme and parsed.scheme not in {"http", "https"}:
            return None
        if parsed.netloc and parsed.netloc != "testserver":
            return None

        path = parsed.path or "/"
        if not path.startswith("/"):
            return None

        blocked_prefixes = (
            "/static/",
            "/media/",
            "/admin/logout",
            "/contas/logout",
        )
        if path.startswith(blocked_prefixes):
            return None

        query = f"?{parsed.query}" if parsed.query else ""
        return f"{path}{query}"

    def _extract_hrefs(self, response):
        content_type = (response.headers.get("Content-Type") or "").lower()
        if "text/html" not in content_type:
            return []

        parser = _HrefParser()
        parser.feed(response.content.decode("utf-8", errors="ignore"))
        return parser.hrefs

    def test_links_internos_dashboard_sem_quebra(self):
        seeds = [
            reverse("secretaria:index"),
            reverse("secretaria:dashboard"),
            reverse("secretaria:portal_membro"),
            reverse("secretaria:lista_membros"),
            reverse("secretaria:lista_visitantes"),
            reverse("secretaria:lista_grupos_casa"),
            reverse("secretaria:registrar_presenca_visitante_evento"),
        ]

        queue = deque(seeds)
        visited = set()
        broken = []
        max_pages = 160

        while queue and len(visited) < max_pages:
            url = queue.popleft()
            if url in visited:
                continue
            visited.add(url)

            response = self.client.get(url, follow=False)
            if not self._status_ok(response.status_code):
                broken.append((url, response.status_code))
                continue

            if response.status_code != 200:
                continue

            for href in self._extract_hrefs(response):
                normalized = self._normalize_internal_href(href)
                if not normalized:
                    continue
                if normalized in visited:
                    continue
                if normalized not in queue:
                    queue.append(normalized)

        self.assertFalse(
            broken,
            msg=f"Links com status inválido (404/5xx): {broken}",
        )
