"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect, after_this_request, make_response

from flask_cache import Cache

from application import app
import schedule_parse


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
ALLOWED_EXTENSIONS = ['html', 'htm']

def valid_filename(fname):
  return fname.split('.')[-1].lower() in ALLOWED_EXTENSIONS


def home():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        schedule = request.files['schedule']
        try:
            if schedule and valid_filename(schedule.filename):
                cal = schedule_parse.build_calendar(schedule.filename)
                response = make_response(cal.to_ical())
                response.headers['Content-Type'] = 'text/calendar'
                response.headers['Content-Disposition'] = 'attachment; filename="schedule.ics"'
                return response
            else:
                return render_template('index.html', error='Sorry, the file you gave could not be parsed.')
        except:
            return render_template('404.html'), 404
    else:
        return render_template('404.html'), 404


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''

