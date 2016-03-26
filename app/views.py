"""Apps Views

Views are the handlers that respond to requests from web browsers.Views are
written as Python functions. Each view is mapped to a URL
"""

from flask import render_template, flash, redirect, \
        session, url_for, request, g
from flask.ext.login import login_user, logout_user, \
        current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, EditForm, PostForm, SearchForm
from models import User, ROLE_USER, Post
from datetime import datetime
from emails import follower_notification
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS
from config import WHOOSH_ENABLED


@lm.user_loader
def load_user(id):
    """Loads user from the database"""
    return User.query.get(int(id))


@app.before_request
def before_request():
    """Before request function

    @app.before_request decorator, runs function before the view function each
    time a request is recieved. Good place to setup g.user variable.
    """
    # 'current_user' global is set by Flask-Login.
    # g global has easier access, even inside templates.
    g.user = current_user
    if g.user.is_authenticated():
        # Last time user logged in
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        # Create search_form and put it in Flask's g global
        g.search_form = SearchForm()
    # Put text search on/off status in g so templates can access it.
    g.search_enabled = WHOOSH_ENABLED


@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# Pagination url layout. Takes the page arg and declares it as an int
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
# Give pagination page number default value of 1.
def index(page=1):
    """Index function

    @login_required decorator requires user to be logged in before they can
    view this URL. Flask-Login will redirect user to login function if not
    already logged in (configured in __init__.py).
    """
    form = PostForm()
    # If post blog form is filled out, insert new post record in DB
    if form.validate_on_submit():
        post = Post(
            body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        # 'url_for' is a clean way for Flask to obtain the URL of a
        # given view function.
        # Redirect here to refresh page to show new post
        return redirect(url_for('index'))
    # Get posts from followed users from the DB.
    # Pagination takes 3 args: page number, posts per page (config)
    # and an error flag (if true out of range error
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    # render_template function takes the template name and template
    # arguments, and returns the rendered template with placeholders
    # replaced (using Jinja2 templating, as part of Flask).
    return render_template(
        'index.html', title='Home', form=form, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
# Tells Flask-OpenID that this is our login view function.
@oid.loginhandler
def login():
    """Login function"""
    # g global is setup by Flask as a place to store data during life
    # of a request. The logged in user is stored here.
    # If g.user is already logged in, redirect to index page
    if g.user is not None and g.user.is_authenticated():
        # 'redirect' tells the browser to go to a different page
        return redirect(url_for('index'))
    # Create a LoginForm object (forms.py), to send to login template
    form = LoginForm()
    # 'validate_on_submit' processes the form. If form hasn't been
    # submitted by user or contains errors, it will return false
    if form.validate_on_submit():
        # Save result of rember me box in a Flask session
        session['remember_me'] = form.remember_me.data
        # Triggers the user authentication through Flask-OpenID
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    # Render the login template and pass template arguments
    return render_template(
        'login.html', title='Sign In', form=form,
        providers=app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp):
    """After login function

    If authentication is successful, Flask-OpenID will call a function
    registered with the @oid.after_login decorator.
    """
    # The resp arg contains info returned by the OpenID provider
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    # Search for user in DB by their email
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
        # DB session DIFFERENT from a Flask session
        db.session.add(user)
        db.session.commit()
        # make the user follow him/herself
        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
    # Load 'remember_me' value from the Flask session
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    # Next page used to store page user tried to get to, but was not
    # logged in yet
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    """Logout function"""
    logout_user()
    return redirect(url_for('index'))


# <nickname> in @app.route decorator translates into an arg of the
# same name added to the view function (eg /user/Dave nickname = Dave).
@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    """User profile page function."""
    # Load user from DB via nickname that we receive as an argument
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    # user.posts member only gets posts from this user
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """About me profile form"""
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    elif request.method != "POST":
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    # Call email function (emails.py) and pass followed & follower
    follower_notification(user, g.user)
    return redirect(url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))


@app.route('/search', methods=['POST'])
@login_required
def search():
    """Search function

    Form sent here from action in search form (base.html). Search process not
    done here, redirected to search_results function
    """
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    # Redirect to search_results function and pass search query
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/<query>')
@login_required
def search_results(query):
    """Processes search query"""
    # Send query into Whoosh
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html', query=query, results=results)
