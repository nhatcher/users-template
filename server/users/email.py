from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext as _


def send_confirmation_email(recipient: str, username: str, email_token: str):
    """Sends confirmation email"""
    app_url = settings.APP_URL

    message = (
        _(
            """
    Hello %(username)s, we need to confirm your email.

    Please click in the link bellow:

    %(app_url)sapi/activate-account/%(email_token)s

    If you have not asked for an account in this platform you can ignore this message.

    Greetings,
    %(app_url)s
    """
        )
        % {"username": username, "app_url": app_url, "email_token": email_token}
    )

    subject = _("Confirm your email")

    send_mail(subject, _(message), None, [recipient])


def send_update_password_email(recipient: str, username: str, email_token):
    """Sends update password link"""
    app_url = settings.APP_URL

    message = (
        _(
            """
    Hi %(username)s, you have requested to reset your password.

    Please click in the link bellow:

    %(app_url)supdate_password.html#id=%(email_token)s

    If you have not asked for an account in this platform you can ignore this message.

    Greetings,
    %(app_url)s
    """
        )
        % {"username": username, "app_url": app_url, "email_token": email_token}
    )

    subject = _("Update password")

    send_mail(subject, message, None, [recipient])
