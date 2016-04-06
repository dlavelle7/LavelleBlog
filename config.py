"""Configuration file"""

import os
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# To handle web forms use the Flask-WTF extension (wraps WTForms)
# Activates cross-site request forgery prevention (makes app secure)
CSRF_ENABLED = True
# Required when CSRF is enabled
SECRET_KEY = 'you-will-never-guess'

# Define openid providers in array
OPENID_PROVIDERS = [
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'StackExchange', 'url': 'https://openid.stackexchange.com'}]

if os.environ.get('DATABASE_URL') is None:
    # Flask-SQLAlchemy extension for Database (local deployment only)
    # Path to our database file (each DB is stored in a single file)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'app.db')
else:
    # Heroku set an env var named $DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

# Folder where SQLAlchemy-migrate data files are stored
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASEDIR, 'db_repository')

# email server (for sending emails)
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'team.lavapp'
MAIL_PASSWORD = 'pythonapp'
# administrator list (for receiving emails)
ADMINS = ['team.lavapp@gmail.com']

# pagination (show posts in groups or pages - 3 posts per page).
POSTS_PER_PAGE = 3

# Whoosh DB for text search
WHOOSH_BASE = os.path.join(BASEDIR, 'search.db')
MAX_SEARCH_RESULTS = 50

# Whoosh does not work on Heroku
WHOOSH_ENABLED = os.environ.get('HEROKU') is None
