#!flask/bin/python
"""Dedicated Python module for heroku

Which allows us to start a gunicorn sever with this server on Heroku (using cmd line). Heroku does not provide a web server, instead it expects the application to start its own server. Flask web server not good enough for production, Heroku recommends gunicorn (a web server written in Python).
"""
from app import app

