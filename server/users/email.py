from django.conf import settings
from django.core.mail import send_mail


def send_confirmation_email(recipient: str, username: str, email_token: str):
    """Sends confirmation email"""
    app_url = settings.APP_URL

    message = f"""
    Olá {username}, o Feirou.org precisa validar o seu email.

    Por favor, clique no link abaixo.

    {app_url}api/activate-account/{email_token}

    Se você não se cadastrou em nossa plataforma, você pode ignorar este email com segurança.

    Saudações,
    Equipe Feirou.org

    """

    subject = "Confirme o seu email"

    send_mail(subject, message, None, [recipient])


def send_update_password_email(recipient: str, username: str, email_token):
    """Sends update password link"""
    app_url = settings.APP_URL

    message = f"""
    Olá {username}, o Feirou.org precisa validar o seu email.

    Por favor, clique no link abaixo.

    {app_url}update_password.html#id={email_token}

    Se você não se cadastrou em nossa plataforma, você pode ignorar este email com segurança.

    Saudações,
    Equipe Feirou.org

    """

    subject = "Update password"

    send_mail(subject, message, None, [recipient])
