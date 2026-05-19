"""
Formulários para gerenciamento de imagens do sistema.
"""
from django import forms
from django.core.exceptions import ValidationError
from PIL import Image
from pathlib import Path

from .models import SistemaImagem


class SistemaImagemForm(forms.ModelForm):
    """
    Formulário para criar/editar imagens do sistema.
    
    Inclui validações de:
    - Dimensões de imagem
    - Formato de arquivo
    - Tamanho máximo de arquivo
    """
    
    class Meta:
        model = SistemaImagem
        fields = ['tipo', 'variacao', 'descricao', 'imagem', 'largura', 'altura', 'notas']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-control',
                'help_text': 'Selecione a categoria da imagem'
            }),
            'variacao': forms.Select(attrs={
                'class': 'form-control',
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Logo horizontal colorido',
                'maxlength': '255',
            }),
            'imagem': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.jpg,.jpeg,.png,.svg,.ico,.gif,.webp',
                'id': 'id_imagem',
            }),
            'largura': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Largura em pixels (opcional)',
                'min': '1',
                'max': '9999',
            }),
            'altura': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Altura em pixels (opcional)',
                'min': '1',
                'max': '9999',
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações técnicas (opcional)',
            }),
        }
    
    def clean_imagem(self):
        """Valida o arquivo de imagem."""
        imagem = self.cleaned_data.get('imagem')
        
        if not imagem:
            raise ValidationError('Selecione um arquivo de imagem.')
        
        # Validar tamanho máximo (5MB)
        tamanho_maximo = 5 * 1024 * 1024  # 5MB
        if imagem.size > tamanho_maximo:
            raise ValidationError(
                f'Arquivo muito grande. Máximo: 5MB. Seu arquivo: {imagem.size / 1024 / 1024:.1f}MB'
            )
        
        extensao = Path(imagem.name).suffix.lower().lstrip('.')

        if extensao == 'svg':
            return imagem

        # Validar se é uma imagem válida
        try:
            img = Image.open(imagem)
            img.verify()
        except Exception as e:
            raise ValidationError(f'Arquivo inválido ou corrompido: {str(e)}')
        
        return imagem
    
    def clean(self):
        """Validações cruzadas do formulário."""
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        variacao = cleaned_data.get('variacao')
        largura = cleaned_data.get('largura')
        altura = cleaned_data.get('altura')
        ativo = self.instance.ativo if self.instance.pk else False
        
        # Validar dimensões se fornecidas
        if largura and altura:
            if largura <= 0 or altura <= 0:
                raise ValidationError('Largura e altura devem ser maiores que zero.')
        
        # Validar se vai substituir versão ativa
        if ativo and tipo and variacao:
            outras_ativas = SistemaImagem.objects.filter(
                tipo=tipo,
                variacao=variacao,
                ativo=True
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            if outras_ativas.exists():
                # Isso é ok, o modelo desativa automaticamente
                pass
        
        return cleaned_data
    
    def save(self, commit=True):
        """
        Salva o formulário.
        
        Se marcar como ativo, outras versões são desativadas automaticamente
        pelo modelo.
        """
        instance = super().save(commit=False)
        
        # Se é novo e do tipo raster, extrair dimensões automaticamente
        if not self.instance.pk and instance.imagem:
            try:
                extensao = Path(instance.imagem.name).suffix.lower().lstrip('.')
                if extensao != 'svg':
                    img = Image.open(instance.imagem)
                    if not instance.largura:
                        instance.largura = img.width
                    if not instance.altura:
                        instance.altura = img.height
            except Exception:
                pass  # Se falhar, campos ficam vazios
        
        if commit:
            instance.save()
        
        return instance
