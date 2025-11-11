from django import forms
from .models import Tag

class TagTestForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('nome'),
        widget=forms.SelectMultiple,
        required=False,
        label='Tags de Teste'
    )
