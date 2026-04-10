import subprocess

from django.contrib import admin
from django.template.response import TemplateResponse


def painel_pytest_view(request):
    resultado = None
    if request.method == "POST":
        result = subprocess.run(
            ["pytest", "tests/", "--tb=short", "-q"],
            capture_output=True,
            text=True,
            cwd=None,
        )
        resultado = result.stdout + "\n" + result.stderr
    context = dict(
        admin.site.each_context(request),
        resultado=resultado,
    )
    return TemplateResponse(request, "admin/painel_pytest.html", context)
