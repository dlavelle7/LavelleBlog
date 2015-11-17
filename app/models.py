"""MOdel Classes"""
from hashlib import md5
from app import db
from app import app
import flask.ext.whooshalchemy as whooshalchemy
from config import WHOOSH_ENABLED

ROLE_USER = 0
ROLE_ADMIN = 1

# Association table to remove M-M reationship between followers and
# followed users. Not a class as its an auxillary table with only FKs.
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    """User class"""
    
    """Class variables created as instances of db.Column class, which take field type as an argument and optional extras (e.g. PK)
    """
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    # Not a DB field. One to Many relationship denoted on 'one' side
    # with db.relationship, which gets a user.posts member, which
    # gives lists of post from that user. First arg is 'many' class,
    # backref points back 'one' class (post.author will get user who
    # created post).
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    # Define M-M relationship (followers/followed users).
    # 'User' is being followed by this class (left follows right side).
    followed = db.relationship('User', 
	# Indicate the association table that is used        
	secondary = followers, 
	# Indicates the condition that links the follower user with the
	# association table.
        primaryjoin = (followers.c.follower_id == id), 
	# Indicates the condition that links the followed user with
	# the association table.        
	secondaryjoin = (followers.c.followed_id == id),
	# Indicates how this relationship will be accessed from the
	# right side entity (the followed user). 
        backref = db.backref('followers', lazy = 'dynamic'), 
        lazy = 'dynamic')

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname
        
# Flask-Login extension requires certain methods to be implemented
# in the User class
    
    # Returns false if the User object is a user that should not be
    # allow to authenticate for some reason.
    def is_authenticated(self):
        return True

    # Returns false if user is banned (i.e. inactive)
    def is_active(self):
        return True

    # Returns true only for fake users who are not supposed to log in
    def is_anonymous(self):
        return False

    # Return a unique identifier for the user
    def get_id(self):
        return unicode(self.id)

# Get avatar of user from gravatar.com, scaled to requested size.
    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)
        
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self
            
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self
    
    # Takes the 'followed' relationship query which returns all
    # the (follwer, followed) pairs that have our user as the 
    # follower, and we filter it by the followed user. followed
    # has a lazy mode of dynamic, so instead of being the
    # result of the query, its the query object before execute        
    def is_following(self, user):
	# count() executes the query (1 = link, 0 = none).
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

# Efficient query which gets and sorts the posts of the followed users.
    def followed_posts(self):
	# Join Post and followers table, creating a new temp table 
	# according to the given condition (id from followers table 
	# to match id from Post table).
	# Filter this table that have this user as a follower
	# Order by post date descending
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())
       
    # Tells Python how to print object of this class (debugging) 
    def __repr__(self):
        return '<User %r>' % (self.nickname)    

# Blog posts class        
class Post(db.Model):
    # Array field with all the database fields that will be in
    # the searchable index (only the body field of our posts).
    __searchable__ = ['body']
    # Fields 
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    # user_id initiated as a Foreign Key, so DB will link to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)

# Dont create text search if app is running on Heroku (see config.py)
if WHOOSH_ENABLED:
    import flask.ext.whooshalchemy as whooshalchemy
    whooshalchemy.whoosh_index(app, Post)
