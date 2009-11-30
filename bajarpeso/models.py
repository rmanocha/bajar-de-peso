from google.appengine.ext import db

class WeightTracker(db.Model):
    user = db.UserProperty(required = True, auto_current_user_add = True)
    date = db.DateProperty(required = True, auto_now_add = True)
    weight = db.FloatProperty(required = True)

    def __str__(self):
        return '%skgs on %s for %s' % (self.weight, self.date, self.user.nickname())

class WeightTrackerSettings(db.Model):
    user = db.UserProperty(required = True, auto_current_user_add = True)
    units = db.StringProperty(required = True, choices = set(["lbs","kgs"]))
    target_weight = db.FloatProperty(required = False)
    target_date = db.DateProperty(required = False)
    height = db.IntegerProperty(required = False)

    def __str__(self):
        return "Using %s for %s" % (self.units, self.user.nickname())

