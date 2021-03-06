# Create your views here.
from google.appengine.api import users, memcache

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.views.generic.simple import direct_to_template

from bajarpeso.models import WeightTracker, WeightTrackerSettings
from bajarpeso.forms import SettingsForm, TrackerForm, ImportForm
from bajarpeso.decorators import login_required

import datetime
import time
import math
from string import strip
import logging

GET_LOGOUT_URL = lambda : users.create_logout_url('/')
#Caching for 2 days
CACHE_TIMEOUT = 3600*24*2
CHART_DATA_CACHE_KEY = lambda : '-'.join([users.get_current_user().user_id(), "chart_data_dict_json"])
BMI_CACHE_KEY = lambda : '-'.join([users.get_current_user().user_id(), "bmi_key"])

def get_bmi(settings, latest_entry):
    logging.info("BMI_CACHE_KEY for %s is %s" % (users.get_current_user(), BMI_CACHE_KEY()))
    retval = memcache.get(BMI_CACHE_KEY())
    if retval is None:
        if not latest_entry:
            retval = 'Make an entry below'

        if settings.height:
            if settings.units == 'lbs':
                bmi = (latest_entry.weight * 703)/math.pow((settings.height/2.54), 2)
            else:
                bmi = latest_entry.weight/math.pow((settings.height/100.0), 2)

            bmi = '%.2f' % bmi
            retval = bmi
        else:
            retval = 'Enter your height in the settings page'

        memcache.set(BMI_CACHE_KEY(), retval, CACHE_TIMEOUT)
        return retval
    else:
        return retval

def get_weight_time_lost(settings, all_data):
    latest_entry = all_data.get()
    if not latest_entry:
        return ('Make an entry below', 'Make an entry below', 'Make an entry below', 'Make an entry below')

    if settings.target_date:
        if settings.target_date <= datetime.date.today():
            days_left, weight_left, req_rate = ('Target date reached', )*3
        else:
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
        current_rate = '%.2f' % current_rate
    return days_left, weight_left, req_rate, current_rate

@login_required(False)
def big_graph(request):
    settings = WeightTrackerSettings.all().filter('user = ', users.get_current_user()).get()
    return direct_to_template(request, template = 'big-graph.html', extra_context = {'units' : settings.units, 'chart_max' : settings.chart_max})

def main(request):
    user = users.get_current_user()
    if not user:
        return direct_to_template(request, template = 'homepage.html', extra_context = {'login_url' : users.create_login_url(request.get_full_path())})

    if request.method == 'POST':
        return_msg = {}
        try:
            date = datetime.date.fromtimestamp(time.mktime(time.strptime(request.POST['date'], '%Y-%m-%d')))
            tracker = WeightTracker.all().filter('user = ', user).filter('date = ', date).get()
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
        
        #Delete all cache data whenever a new entry is made
        memcache.delete_multi([CHART_DATA_CACHE_KEY(), BMI_CACHE_KEY()])
        if request.is_ajax():
            return HttpResponse(simplejson.dumps(return_msg), mimetype = 'application/json')
        else:
            return HttpResponseRedirect('/')
    else:
        all_data = WeightTracker.all().filter('user = ', user).order('-date')
        data_dict = {'data' : all_data, 'logout_url' : GET_LOGOUT_URL(), 'tracker_form' : TrackerForm()}
        settings = WeightTrackerSettings.all().filter('user = ', user).get()
        #We need this here as well as in login_required 'cause that decorator is not called for this view.
        if not settings:
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

@login_required(False)
def get_chart_data(request):
    if request.is_ajax():
        data_dict_json = memcache.get(CHART_DATA_CACHE_KEY())
        if data_dict_json is None:
            all_data = WeightTracker.all().filter('user = ', users.get_current_user()).order('date')
            data_dict = {'data' : map(lambda entry : (str(entry.date), entry.weight), all_data), 'chart_max' : WeightTrackerSettings.all().filter('user =', users.get_current_user()).get().chart_max}
            data_dict_json = simplejson.dumps(data_dict)
            memcache.set(CHART_DATA_CACHE_KEY(), data_dict_json, CACHE_TIMEOUT)
        return HttpResponse(data_dict_json, mimetype='application/json')
    else:
        return HttpResponseForbidden('You are not allowed to view this URL')


@login_required(True)
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
            #BMI will change if the height is changed.
            memcache.delete(BMI_CACHE_KEY())
            return HttpResponseRedirect('/settings/?success')
    else:
        if get_vars.get('first') is not None:
            msg = 'Welcome. Looks like this is your first time here. Please enter some of your details so we can better track your progress.'
        elif get_vars.get('success') is not None:
            msg = 3
        form = SettingsForm(instance = user_settings)

    return render_to_response('settings.html', {'form' : form, 'logout_url' : GET_LOGOUT_URL(), 'msg' : msg})

@login_required(False)
def delete_data(request):
    if request.is_ajax() and request.method == 'POST':
        if 'date' in request.POST:
            date = datetime.date.fromtimestamp(time.mktime(time.strptime(request.POST['date'], '%Y-%m-%d')))
            WeightTracker.all().filter('user = ', users.get_current_user()).filter('date = ', date).get().delete()
        else:
            from google.appengine.ext import db
            db.delete(WeightTracker.all().filter('user = ', users.get_current_user()))
        return HttpResponse('Delete successful')
    else:
        return HttpResponseForbidden('You are not allowed to view this URL')

@login_required(False)
def import_data(request):
    get_vars = request.GET.copy()
    msg = ''

    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            status, line = handle_uploaded_file(request.FILES['file'])
            if not status:
                return HttpResponseRedirect('/import/?failure=true&line=%s' % str(line))
            else:
                return HttpResponseRedirect('/import/?success')
    else:
        if get_vars.get('failure') is not None:
            msg = 'Oops, looks like there was an error in the uploaded file. The error was found on line # %s. Please fix this error and re-upload.' % get_vars.get('line')
        elif get_vars.get('success') is not None:
            msg = 3

        form = ImportForm()

    return render_to_response('import.html', {'form' : form, 'logout_url' : GET_LOGOUT_URL(), 'msg' : msg})

def handle_uploaded_file(file):
    lines = file.read().split('\n')
    for i, line in enumerate(lines):
        if line:
            date, weight = map(strip, line.split(','))
            try:
                date = datetime.date.fromtimestamp(time.mktime(time.strptime(date, '%m/%d/%Y')))
                weight = float(weight)
            except ValueError:
                return False, i + 1
            entry = WeightTracker.all().filter('user = ', users.get_current_user()).filter('date = ', date).get()
            if entry:
                entry.weight = weight
            else:
                entry = WeightTracker(date = date, weight = weight)
            entry.put()

    return True, -1
