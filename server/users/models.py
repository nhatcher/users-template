from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.forms import ValidationError


class UserProfile(models.Model):
    """Extends the internal django User Model with extra data"""

    user = models.OneToOneField(
        User,
        related_name="userprofile",
        related_query_name="userprofile",
        on_delete=models.CASCADE,
    )

    nickname = models.CharField(max_length=254, blank=True)


class PendingUser(models.Model):
    """
    A pending-user has not yet confirmed the email link.

    We use a real User with `is_active = False`. This ensures things like
    unique username, valid password, etc...

    Once the link is confirmed `is_active` will be set to True and the pending-user deleted
    """

    # In principle there can be many "pending-users" pointing to the same user
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    email_token = models.CharField(max_length=120, default="")


class RecoverPassword(models.Model):
    """This is a list of folks that have requested a recover password link"""

    email_token = models.CharField(max_length=120, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_date = models.DateTimeField()
    expiration_date = models.DateTimeField()


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    """Create a profile anytime a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()


@receiver(pre_save, sender=User)
def check_email(sender, instance, **kwargs):
    email = instance.email
    if sender.objects.filter(email=email).exclude(username=instance.username).exists():
        raise ValidationError("Email Already Exists")
