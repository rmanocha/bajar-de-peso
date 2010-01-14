from google.appengine.api import users

from django.http import HttpResponseRedirect

from bajarpeso.models import WeightTracker, WeightTrackerSettings

class login_required(object):
    """
        Need this to be a class 'cause we shouldn't be redirecting to '/success/' 
        if we're viewing /success/ already. To do so, we need to pass an argument
        to the decorator to tell it where we are.
    """
    def __init__(self, settings = False):
        self.in_settings = settings

    def __call__(self, func):
        def _wrapper(request, *args, **kw):
            user = users.get_current_user()
            if user:
                if not self.in_settings:
                    settings = WeightTrackerSettings.all().filter('user = ', user).get()
                    if not settings:
                        return HttpResponseRedirect('/settings/?first')
                return func(request, *args, **kw)
            else:
                return HttpResponseRedirect(users.create_login_url(request.get_full_path()))

        return _wrapper

