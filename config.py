"""Configuration file for flask extensions"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))

# To handle web forms use the Flask-WTF extension (wraps WTForms)
# Activates cross-site request forgery prevention (makes app secure)
CSRF_ENABLED = True
# Required when CSRF is enabled
SECRET_KEY = 'you-will-never-guess'

# Define openid providers in array
OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]

# Flask-SQLAlchemy extension for Database (local deployment only)   
# Path to our database file (each DB is stored in a single file) 
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
# Folder where SQLAlchemy-migrate data files are stored
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# email server (for sending emails)
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'info.microblog'
MAIL_PASSWORD = 'microblog'
# administrator list (for receiving emails)
ADMINS = ['davidlavelle1@gmail.com']

# pagination (show posts in groups or pages - 3 posts per page).
POSTS_PER_PAGE = 3

# Whoosh DB for text search
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50

# Whoosh does not work on Heroku
WHOOSH_ENABLED = os.environ.get('HEROKU') is None
