"""Init script"""
import os
# Import class Flask
from flask import Flask
# Import SQLAlchemy database
from flask.ext.sqlalchemy import SQLAlchemy
# Import Flask-Login and Flask-Openid flask exts for login system
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
# Import Flask-Mail to send emails from app
from flask.ext.mail import Mail
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
# Import momentjs
from momentjs import momentjs

# Create the Flask application object (of class Flask)
app = Flask(__name__)
# Tell Flask to read the config file and use it
app.config.from_object('config')

# Create db object that will be our database
db = SQLAlchemy(app)

# Flask-OpenID requires path to a temp folder where files can be stored
lm = LoginManager()
lm.init_app(app)
# Tells Flask-Login which function logs user in
lm.login_view = 'login'
oid = OpenID(app, os.path.join(basedir, 'tmp'))

# Initialize a Mail object, this will be the object that connects to
# the SMTP server and send the emails.
mail = Mail(app)

if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'lavelle-blog failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

if not app.debug and os.environ.get('HEROKU') is None:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/lavelleblog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('lavelle-blog startup')

if os.environ.get('HEROKU') is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('lavelle-blog startup')

# Tells Jinja2 to expose our class as a global variable to templates
app.jinja_env.globals['momentjs'] = momentjs

# Import views and models modules
from app import views, models

