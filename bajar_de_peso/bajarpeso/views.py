# Create your views here.
from google.appengine.api import users

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson

from bajar_de_peso.bajarpeso.models import WeightTracker

import datetime
import time

def main(request):
    if request.method == 'POST':
        return_msg = {}
        try:
            date = datetime.date.fromtimestamp(time.mktime(time.strptime(request.POST['date'], '%Y-%m-%d')))
            date_entry = WeightTracker.all().filter('user = ', users.get_current_user()).filter('date = ', date).get()
            if date_entry:
                date_entry.weight = float(request.POST['weight'])
                date_entry.put()
            else:
                track = WeightTracker(weight = float(request.POST['weight']), date = date)
                track.put()
            return_msg['error'] = 0
            return_msg['msg'] = 'Data was saved succesfully'
        except ValueError, e:
            return_msg['error'] = 1
            return_msg['msg'] = 'The date was not in the correct format'
        return HttpResponse(simplejson.dumps(return_msg), mimetype = 'application/json')
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
