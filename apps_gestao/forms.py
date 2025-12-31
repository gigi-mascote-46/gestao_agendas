from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, PedidoFerias, Departamento

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # Definimos os campos que aparecem no registo
        fields = ("username", "email", "departamento", "is_chef")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. INDICAÇÕES (Placeholders)
        #username e email
        self.fields['username'].widget.attrs.update({'placeholder': 'Ex: agente_neo_01'})
        self.fields['email'].widget.attrs.update({'placeholder': 'terminal@empresa.com'})
        
        # 2. RESOLUÇÃO DO ERRO 'empty_label'
        # Verificamos se o departamento existe e se é um ModelChoiceField
        if 'departamento' in self.fields:
            field = self.fields['departamento']
            # O Python/Django só atribui empty_label a campos de seleção de modelos
            if hasattr(field, 'empty_label'):
                field.empty_label = "--- SELECIONA O TEU DEPARTAMENTO ---"
        
        # 3. TEXTOS DE AJUDA (Help Texts)
        self.fields['username'].help_text = "Mínimo 4 caracteres. Apenas alfanuméricos."
        self.fields['is_chef'].help_text = "Seleciona apenas se fores gestor de equipa."

class PedidoFeriasForm(forms.ModelForm):
    class Meta:
        model = PedidoFerias
        fields = ['data_inicio', 'data_fim', 'tipo']
        widgets = {
            # Aplicamos as classes Tech diretamente nos widgets
            'data_inicio': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'placeholder': 'Data de Início'
            }),
            'data_fim': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'placeholder': 'Data de Fim'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Placeholder para o select (se necessário)
        if 'tipo' in self.fields:
            self.fields['tipo'].label = "Categoria de Ausência"