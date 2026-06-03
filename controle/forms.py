from pathlib import Path

from django import forms

from .impressao import EXTENSOES_IMPRESSAO


class SolicitarImpressaoForm(forms.Form):
    paginas = forms.IntegerField(min_value=1, initial=1, label='Quantidade de paginas')
    arquivo = forms.FileField(
        label='Arquivo para imprimir',
        help_text='Formatos: PDF, TXT, PS, PNG, JPG.',
    )
    descricao = forms.CharField(
        max_length=200,
        required=False,
        label='Descricao (opcional)',
        widget=forms.TextInput(attrs={'placeholder': 'Ex.: trabalho de matematica'}),
    )

    def clean_arquivo(self):
        arquivo = self.cleaned_data['arquivo']
        extensao = Path(arquivo.name).suffix.lower()
        if extensao not in EXTENSOES_IMPRESSAO:
            formatos = ', '.join(sorted(EXTENSOES_IMPRESSAO))
            raise forms.ValidationError(f'Formato nao suportado. Use: {formatos}.')
        return arquivo
