# Create your views here.
from google.appengine.api import users

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils import simplejson

from bajarpeso.models import WeightTracker, WeightTrackerSettings
from bajarpeso.forms import SettingsForm, TrackerForm

import datetime
import time
import math

GET_LOGOUT_URL = lambda : users.create_logout_url('/')

def get_bmi(settings, latest_entry):
    if not latest_entry:
        return 'Make an entry below'

    if settings.height:
        if settings.units == 'lbs':
            bmi = (latest_entry.weight * 703)/math.pow((settings.height/2.54), 2)
        else:
            bmi = latest_entry.weight/math.pow((settings.height/100.0), 2)

        bmi = '%.2f' % bmi
        return bmi
    else:
        return 'Enter your height in the settings page'

def get_weight_time_lost(settings, all_data):
    latest_entry = all_data.get()
    if not latest_entry:
        return ('Make an entry below', 'Make an entry below', 'Make an entry below', 'Make an entry below')

    if settings.target_date:
        days_left = (settings.target_date - latest_entry.date).days
        weight_left =  settings.target_weight - latest_entry.weight
        req_rate = weight_left/days_left
        req_rate = '%.2f' % req_rate
    else:
        days_left, weight_left, req_rate = ('Edit your settings', )*3

    first_entry = all_data[all_data.count() - 1]
    if first_entry.date == datetime.date.today():
        current_rate = 'N/A'
    else:
        current_rate = (latest_entry.weight - first_entry.weight)/(datetime.date.today() - first_entry.date).days
    return days_left, weight_left, req_rate, current_rate


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
        
        if request.is_ajax():
            return HttpResponse(simplejson.dumps(return_msg), mimetype = 'application/json')
        else:
            return HttpResponseRedirect('/')
    else:
        all_data = WeightTracker.all().filter('user = ', users.get_current_user()).order('-date')
        data_dict = {'data' : all_data, 'logout_url' : GET_LOGOUT_URL(), 'tracker_form' : TrackerForm()}
        settings = WeightTrackerSettings.all().filter('user = ', users.get_current_user()).get()
        if not settings:
            #settings = WeightTrackerSettings(units = 'kgs')
            #settings.put()
            return HttpResponseRedirect('/settings/?first')
        data_dict['units'] = settings.units
        data_dict['bmi'] = get_bmi(settings, all_data.get())
        data_dict['days_left'], data_dict['weight_left'], data_dict['req_rate'], data_dict['cur_rate'] = get_weight_time_lost(settings, all_data)

        #Need to put this try/except block in case no entries for 'this' user have been created
        try:
            if all_data.get().date != datetime.date.today():
                data_dict['today'] = datetime.date.today()
        except AttributeError, e:
            data_dict['today'] = datetime.date.today()
        return render_to_response('index.html', data_dict)

def get_chart_data(request):
    all_data = WeightTracker.all().filter('user = ', users.get_current_user()).order('date')
    data_dict = {'data' : map(lambda entry : (str(entry.date), entry.weight), all_data)}
    #This seems like a Hack. There needs to be a better way of doing things.
    #for i in range(5, all_data.count() + 1):
    #    data_dict['data'][i - 1].append(sum(map(lambda l: l.weight, all_data[i - 5:i]))/5)
    return HttpResponse(simplejson.dumps(data_dict), mimetype='application/json')

def edit_settings(request):
    user_settings = WeightTrackerSettings.all().filter('user = ', users.get_current_user()).get()
    get_vars = request.GET.copy()
    msg = ''

    if request.method == 'POST':
        form = SettingsForm(request.POST, instance = user_settings)
        if form.is_valid():
            item = form.save(commit = False)
            item.user = users.get_current_user()
            item.put()
            return HttpResponseRedirect('/settings/?success')
    else:
        if get_vars.get('first') is not None:
            msg = 'Welcome. Looks like this is your first time here. Please enter some of your details so we can better track your progress.'
        elif get_vars.get('success') is not None:
            msg = 'Settings saved succesfully. You can now go and start entering your weight'
        form = SettingsForm(instance = user_settings)

    return render_to_response('settings.html', {'form' : form, 'logout_url' : GET_LOGOUT_URL(), 'msg' : msg})
