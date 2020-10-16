from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from django.conf import settings
import logging

log = logging.getLogger(__name__)


@receiver(post_delete, sender=FriendshipRequest)
def friend_request_delete_handler(sender, instance, **kwargs):
    pass


@receiver(post_save, sender=FriendshipRequest)
def friend_request_save_handler(sender, instance, created, **kwargs):
    pass


@receiver(post_delete, sender=Friend)
def friend_delete_handler(sender, instance, **kwargs):
   pass