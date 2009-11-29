# Create your views here.
from google.appengine.api import users

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson

from bajarpeso.models import WeightTracker, WeightTrackerSettings
from bajarpeso.forms import SettingsForm

import datetime
import time

GET_LOGOUT_URL = lambda : users.create_logout_url('/')

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
        data_dict = {'data' : all_data, 'logout_url' : GET_LOGOUT_URL()}
        settings = WeightTrackerSettings.all().filter('user = ', users.get_current_user()).get()
        if not settings:
            settings = WeightTrackerSettings(units = 'kgs')
            settings.put()
        data_dict['units'] = settings.units

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
    data_dict = {'data' : map(lambda entry : (str(entry.date), entry.weight), all_data)}
    #This seems like a Hack. There needs to be a better way of doing things.
    #for i in range(5, all_data.count() + 1):
    #    data_dict['data'][i - 1].append(sum(map(lambda l: l.weight, all_data[i - 5:i]))/5)
    return HttpResponse(simplejson.dumps(data_dict), mimetype='application/json')

def edit_settings(request):
    user_settings = WeightTrackerSettings.all().filter('user = ', users.get_current_user()).get()
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance = user_settings)
        if form.is_valid():
            item = form.save(commit = False)
            item.user = users.get_current_user()
            item.put()
            return HttpResponse('Thanks for editing your settings')
    else:
        form = SettingsForm(instance = user_settings)

    return render_to_response('settings.html', {'form' : form, 'logout_url' : GET_LOGOUT_URL()});
