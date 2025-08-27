from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from accounts.models import Profile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        if Profile.objects.get(user=instance) is None:
            Profile.objects.create(
                user=instance, image="https://ui-avatars.com/api/?name="+instance.username)
    else:
        profile = Profile.objects.get(user=instance)
        profile.image = "https://ui-avatars.com/api/?name="+instance.username
