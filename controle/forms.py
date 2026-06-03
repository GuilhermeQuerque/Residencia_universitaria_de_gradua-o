import re
from pathlib import Path

from django import forms
from django.contrib.auth.models import User

from .impressao import EXTENSOES_IMPRESSAO


class RegistroForm(forms.Form):
    email = forms.EmailField(label='Email institucional *')
    nome = forms.CharField(max_length=100, label='Nome completo *')
    cpf = forms.CharField(max_length=14, required=False, label='CPF *')
    inscricao = forms.CharField(max_length=50, required=False, label='Inscrição')
    senha = forms.CharField(widget=forms.PasswordInput, label='Senha *')
    confirmar_senha = forms.CharField(widget=forms.PasswordInput, label='Confirmar senha')

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        if not cpf:
            return cpf
        cpf = re.sub(r'\D', '', cpf)
        if len(cpf) != 11:
            raise forms.ValidationError('CPF deve ter 11 digitos.')
        if cpf == cpf[0] * 11:
            raise forms.ValidationError('CPF invalido.')
        for i in range(9, 11):
            soma = sum(int(cpf[j]) * (i + 1 - j) for j in range(i))
            digito = 11 - soma % 11
            if digito > 9:
                digito = 0
            if int(cpf[i]) != digito:
                raise forms.ValidationError('CPF invalido.')
        return cpf

    def clean(self):
        cleaned = super().clean()
        cpf = cleaned.get('cpf', '')
        inscricao = cleaned.get('inscricao', '')
        senha = cleaned.get('senha')
        confirmar = cleaned.get('confirmar_senha')

        if not cpf and not inscricao:
            raise forms.ValidationError('Informe CPF ou Inscricao (pelo menos um).')

        if senha and confirmar and senha != confirmar:
            raise forms.ValidationError('Senhas nao conferem.')

        email = cleaned.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ja esta cadastrado.')

        return cleaned


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        return files.getlist(name)


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def to_python(self, data):
        if not data:
            return []
        if isinstance(data, list):
            return data
        return [data]

    def validate(self, value):
        if value in self.empty_values or not value:
            raise forms.ValidationError('Selecione pelo menos um arquivo.', code='required')
        for f in value:
            super().validate(f)

    def clean(self, data, initial=None):
        data = self.to_python(data)
        self.validate(data)
        self.run_validators(data)
        return data


class SolicitarImpressaoForm(forms.Form):
    arquivo = MultipleFileField(
        label='Arquivo(s) para imprimir',
        help_text='Formatos: PDF, TXT, PS, PNG, JPG. Segure Ctrl para selecionar varios.',
        widget=MultipleFileInput(attrs={'multiple': True}),
    )
    descricao = forms.CharField(
        max_length=200,
        required=False,
        label='Descricao (opcional)',
        widget=forms.TextInput(attrs={'placeholder': 'Ex.: trabalho de matematica'}),
    )

    def clean_arquivo(self):
        arquivos = self.cleaned_data['arquivo']
        for arquivo in arquivos:
            extensao = Path(arquivo.name).suffix.lower()
            if extensao not in EXTENSOES_IMPRESSAO:
                formatos = ', '.join(sorted(EXTENSOES_IMPRESSAO))
                raise forms.ValidationError(
                    f'Formato "{extensao}" nao suportado para "{arquivo.name}". Use: {formatos}.'
                )
        return arquivos
