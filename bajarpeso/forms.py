from google.appengine.api import users
from google.appengine.ext.db import djangoforms

from django import forms

from bajarpeso.models import WeightTrackerSettings

class SettingsForm(djangoforms.ModelForm):
    def clean(self):
        cleaned_data = self.cleaned_data
        target_date = cleaned_data.get('target_date', '')
        target_weight = cleaned_data.get('target_weight', '')

        if target_date and target_weight:
            return cleaned_data
        elif not target_date and not target_weight:
            return cleaned_data
        else:
            raise forms.ValidationError('You have to enter both target date and target weight. You have only entered one')

    class Meta:
        model = WeightTrackerSettings
        exclude = ['user']
