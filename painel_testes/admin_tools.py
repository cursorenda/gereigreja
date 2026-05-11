import subprocess
import sys

from django.contrib import admin
from django.conf import settings
from django.template.response import TemplateResponse


def painel_pytest_view(request):
    resultado = None
    if request.method == 'POST':
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', 'tests/', '--tb=short', '-q'],
                capture_output=True,
                text=True,
                cwd=settings.BASE_DIR,
            )
            resultado = result.stdout + '\n' + result.stderr
        except Exception as exc:
            resultado = str(exc)

    context = dict(admin.site.each_context(request), resultado=resultado)
    return TemplateResponse(request, 'admin/painel_pytest.html', context)
