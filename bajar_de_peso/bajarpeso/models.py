from google.appengine.ext import db

# Create your models here.

class WeightTracker(db.Model):
    user = db.UserProperty(required = True, auto_current_user_add = True)
    date = db.DateProperty(auto_now_add = True)
    weight = db.FloatProperty()
