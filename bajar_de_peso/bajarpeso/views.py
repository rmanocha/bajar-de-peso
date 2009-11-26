# Create your views here.
from google.appengine.api import users

from django.http import HttpResponse
from django.shortcuts import render_to_response

from bajar_de_peso.bajarpeso.models import WeightTracker

import datetime

def main(request):
    if request.method == 'POST':
        track = WeightTracker(weight = request.POST['weight'], date = request.POST['date'])
        track.put()
        return HttpResponse('All Done!!')
    else:
        all_data = WeightTracker.all().filter('user = ', users.get_current_user()).order('-date')
        data_dict = {'data' : all_data}
        #Need to put this try/except block in case no entries for 'this' user have been created
        try:
            if all_data.get().date != datetime.date.today():
                data_dict['today'] = datetime.date.today()
        except AttributeError, e:
            data_dict['today'] = datetime.date.today()
        return render_to_response('index.html', data_dict)
