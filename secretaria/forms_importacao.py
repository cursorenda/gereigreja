from django import forms

class ImportacaoPessoasForm(forms.Form):
    arquivo = forms.FileField(
        label="Arquivo Excel (.xlsx)",
        help_text="Faça upload do arquivo modelo preenchido com os dados dos membros.",
        required=True,
        widget=forms.ClearableFileInput(attrs={"accept": ".xlsx"})
    )
