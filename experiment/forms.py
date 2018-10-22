from django import forms
from .models import Experiment


class ScaleForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ['parallel']
