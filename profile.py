#!flask/bin/python
"""Profiling

Profiling watches how much time is spent on each function, measuring the performance of the app. Werkzeug module used by Flask comes with a profiler plugin. This is a starter script (like run.py) which enables Werkzeug profiler
"""
from werkzeug.contrib.profiler import ProfilerMiddleware
from app import app

app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [30])
app.run(debug = True)

