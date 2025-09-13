from django import forms

class ResultadoAnaliseSiteForm(forms.Form):
    url = forms.CharField(label="", max_length=4096)


class TipoDeficienciaForm(forms.Form):
    deficiencia = forms.CharField(label="", max_length=255)


class NovaCategoriaForm(forms.Form):
    categoria = forms.CharField(label="", max_length=255)


class NovoCriterioWCAG(forms.Form):
    criterio = forms.CharField(label="Critério", max_length=255)
    prioridade = forms.CharField(label="Prioridade", max_length=10)