from google.appengine.api import users
from google.appengine.ext.db import djangoforms

from bajarpeso.models import WeightTrackerSettings

class SettingsForm(djangoforms.ModelForm):
    class Meta:
        model = WeightTrackerSettings
        exclude = ['user']
