from google.appengine.api import users
from google.appengine.ext.db import djangoforms

from django import forms

from bajarpeso.models import WeightTracker, WeightTrackerSettings

class TrackerForm(djangoforms.ModelForm):
    date = forms.DateField(required = True, widget = forms.TextInput(attrs = {'size' : 10}))
    weight = forms.FloatField(required = True, widget = forms.TextInput(attrs = {'size' : 5}))

    class Meta:
        model = WeightTracker
        exclude = ['user']

class SettingsForm(djangoforms.ModelForm):
    units = forms.ChoiceField(required = True, label = 'Units', choices = (('lbs', 'Pounds'), ('kgs', 'Kilograms')))

    def clean_target_date(self):
        cleaned_data = self.cleaned_data
        target_date = cleaned_data.get('target_date', '')
        target_weight = cleaned_data.get('target_weight', '')

        if target_date and target_weight:
            return target_date
        elif not target_date and not target_weight:
            return target_date
        else:
            raise forms.ValidationError('You have to enter both target date and target weight. You have only entered one.')

    class Meta:
        model = WeightTrackerSettings
        exclude = ['user']

class ImportForm(forms.Form):
    file = forms.FileField()
