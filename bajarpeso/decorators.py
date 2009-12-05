from google.appengine.api import users

from django.http import HttpResponseRedirect

def login_required(func):
    def _wrapper(request, *args, **kw):
        user = users.get_current_user()
        if user:
            return func(request, *args, **kw)
        else:
            return HttpResponseRedirect(users.create_login_url(request.get_full_path()))

    return _wrapper

