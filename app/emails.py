"""Module which handles the app's emails"""

from flask.ext.mail import Message
from app import mail
from flask import render_template
from config import ADMINS
from decorators import async


@async
def send_async_email(msg):
    """Asynchronous function which sends email as a background process."""
    mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    """Send email function

    Calls async function and returns immediately,no delay. Web server not
    blocked until email is sent.
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(msg)


def follower_notification(followed, follower):
    """ Compose notification of follower email"""
    send_email(
        "[lavelle-blog] %s is now following you!" % follower.nickname,
        ADMINS[0], [followed.email],
        # Use render_template to compose bodies of emails
        render_template(
            "follower_email.txt", user=followed, follower=follower),
        render_template(
            "follower_email.html", user=followed, follower=follower))
