"""Web form Classes"""

from flask.ext.wtf import Form, TextField, BooleanField, \
        TextAreaField, Required, Length
from app.models import User


class LoginForm(Form):
    """Login page form"""
    openid = TextField('openid', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class EditForm(Form):
    """About me profile form"""
    nickname = TextField('nickname', validators=[Required()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(
            nickname=self.nickname.data).first()
        if user is not None:
            self.nickname.errors.append(
                'This nickname is already in use. Please choose another one.')
            return False
        return True


class PostForm(Form):
    """Home page blog post form"""
    post = TextField('post', validators=[Required()])


class SearchForm(Form):
    """Text search form at top of nav bar"""
    search = TextField('search', validators=[Required()])
