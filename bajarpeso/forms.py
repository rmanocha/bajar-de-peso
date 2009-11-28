from google.appengine.api import users

from django import forms

from bajarpeso.models import WeightTrackerSettings

class SettingsForm(forms.Form):
    units = forms.ChoiceField(required = True, choices = (('lbs', 'Pounds'), ('kgs', 'Kilograms')))
    target_weight = forms.CharField(required = False)
    target_date = forms.DateField(required = False, input_formats = ['%Y-%m-%d'])

    def clean_target_weight(self):
        #print "here"
        self.clean_data['target_weight'] = float(self.clean_data['target_weight'])

    def save(self, user):
        tracker_settings = WeightTrackerSettings.all().filter('user = ', user).get()
        if tracker_settings:
            tracker_settings.units = self.clean_data['units']
        else:
            tracker_settings = WeightTrackerSettings(units = self.clean_data['units'], target_weight = self.clean_data['target_weight'], target_data = self.clean_data['target_date'])
        tracker_settings.save()
