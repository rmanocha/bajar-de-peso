from google.appengine.ext import db
from google.appengine.api import users

# Create your models here.

class WeightTracker(db.Model):
    user = db.UserProperty(required = True, auto_current_user_add = True)
    date = db.DateProperty(auto_now_add = True)
    weight = db.FloatProperty()

    def __str__(self):
        return '%skgs on %s for %s' % (self.weight, self.date, users.get_current_user().nickname())
