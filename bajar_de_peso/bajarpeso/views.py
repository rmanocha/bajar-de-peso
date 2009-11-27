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
            tracker = WeightTracker.all().filter('user = ', users.get_current_user()).filter('date = ', date).get()
            if tracker:
                tracker.weight = float(request.POST['weight'])
                tracker.put()
            else:
                tracker = WeightTracker(weight = float(request.POST['weight']), date = date)
                tracker.put()
            return_msg['error'] = 0
            return_msg['msg'] = 'Data was saved succesfully'
            return_msg['weight'] = str(tracker.weight)
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

def get_prev_date(request):
    first_entry = WeightTracker.all().filter('user = ', users.get_current_user()).order('date').get()
    first_date = first_entry.date if first_entry else datetime.date.today()
    return HttpResponse(str(first_date - datetime.timedelta(1)))

def get_chart_data(request):
    all_data = WeightTracker.all().filter('user = ', users.get_current_user()).order('date')
    data_dict = {'data' : map(lambda entry : [str(entry.date), entry.weight], all_data)}
    #This seems like a Hack. There needs to be a better way of doing things.
    for i in range(5, all_data.count() + 1):
        data_dict['data'][i - 1].append(sum(map(lambda l: l.weight, all_data[i - 5:i]))/5)
    return HttpResponse(simplejson.dumps(data_dict), mimetype='application/json')
