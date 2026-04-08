from django.contrib import admin

from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.template.response import TemplateResponse
import subprocess

from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
import subprocess

def painel_pytest_view(request):
    resultado = None
    if request.method == "POST":
        result = subprocess.run(
            ["pytest", "tests/", "--tb=short", "-q"],
            capture_output=True, text=True
        )
        resultado = result.stdout + "\n" + result.stderr
    context = dict(
        admin.site.each_context(request),
        resultado=resultado
    )
    return TemplateResponse(request, "admin/painel_pytest.html", context)
