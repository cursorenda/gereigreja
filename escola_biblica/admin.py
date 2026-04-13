from django.contrib import admin, messages
from .models import AnoLetivo, CadastroAluno, Classe, Turma, Aluno, Frequencia, Licao, Avaliacao


@admin.register(AnoLetivo)
class AnoLetivoAdmin(admin.ModelAdmin):
    list_display = ("ano", "ativo")
    list_filter = ("ativo",)

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ("nome", "faixa_etaria")


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ("nome", "classe", "ano_letivo")
    list_filter = ("ano_letivo", "classe")

@admin.register(CadastroAluno)
class CadastroAlunoAdmin(admin.ModelAdmin):
    list_display = ("nome", "pessoa", "vinculado_secretaria", "igreja", "ativo")
    list_filter = ("igreja", "ativo", ("pessoa", admin.EmptyFieldListFilter))
    search_fields = ("nome", "responsavel", "telefone_responsavel", "pessoa__nome", "pessoa__email")
    actions = ("tentar_vincular_com_secretaria",)

    @admin.display(boolean=True, description='Vinculado à Secretaria')
    def vinculado_secretaria(self, obj):
        return bool(obj.pessoa_id)

    @admin.action(description='Tentar vincular com Pessoa da Secretaria')
    def tentar_vincular_com_secretaria(self, request, queryset):
        vinculados = 0
        sem_match = 0

        for cadastro in queryset:
            pessoa = cadastro.tentar_vincular_pessoa(force=True)
            if pessoa is None:
                sem_match += 1
                continue

            cadastro.save()
            vinculados += 1

        if vinculados:
            self.message_user(
                request,
                f'{vinculados} cadastro(s) vinculados com sucesso à Secretaria.',
                level=messages.SUCCESS,
            )
        if sem_match:
            self.message_user(
                request,
                f'{sem_match} cadastro(s) permaneceram sem correspondência segura.',
                level=messages.WARNING,
            )

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("nome", "cadastro", "cadastro_pessoa", "turma", "ativo")
    list_filter = ("turma", "ativo")
    search_fields = ("nome", "cadastro__nome", "cadastro__pessoa__nome")

    @admin.display(description='Pessoa (Secretaria)')
    def cadastro_pessoa(self, obj):
        return getattr(obj.cadastro, 'pessoa', None)

@admin.register(Frequencia)
class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ("aluno", "data", "presente")
    list_filter = ("data", "presente")

@admin.register(Licao)
class LicaoAdmin(admin.ModelAdmin):
    list_display = ("tema", "turma", "data")
    list_filter = ("turma", "data")

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("aluno", "licao", "nota", "participacao")
    list_filter = ("licao", "participacao")
