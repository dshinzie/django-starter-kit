import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from friendship.exceptions import AlreadyExistsError, AlreadyFriendsError, AlreadyRejectedError
from friendship.signals import (
    friendship_request_created, friendship_request_rejected,
    friendship_request_canceled, friendship_request_accepted,
    friendship_removed
)

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class FriendshipRequestManager(models.Manager):
    """
    Manager for Friend Requests
    Currently supports using uuid and pk
    """

    def _valid_uuid(self, id):
        try:
            return uuid.UUID(id, version=4)
        except ValueError:
            return False

    def cancel_invite(self, id, user):
        if self._valid_uuid(id):
            invite = self.get(uuid=id, from_user=user)
        else:
            invite = self.get(id=id, from_user=user)
        invite.cancel()

    def update_invite(self, id, user, action):
        if self._valid_uuid(id):
            invite = self.get(uuid=id, to_user=user)
        else:
            invite = self.get(id=id, to_user=user)

        if action == FriendshipRequest.ACCEPT_ACTION:
            invite.accept()
        elif action == FriendshipRequest.REJECT_ACTION:
            invite.reject()

    def send_invite(self, app, from_user, email):
        """
        Invite a user to become friends on an app.
        """
        try:
            to_user = User.objects.get(email=email)
            if from_user == to_user:
                raise ValidationError("Users cannot be friends with themselves")

            if Friend.objects.are_friends(from_user, to_user, app):
                raise AlreadyFriendsError("Users are already friends")

            invite, created = self.get_or_create(from_user=from_user, to_user=to_user, app=app)

        except User.DoesNotExist:
            invite, created = self.get_or_create(
                from_user=from_user,
                to_email=email,
                app=app
            )

        if not created:
            if invite.rejected:
                raise AlreadyRejectedError("Friendship already rejected")
            else:
                raise AlreadyExistsError("Friendship already requested")

        friendship_request_created.send(sender=invite)
        return invite

    def get_invites(self, app, user, state, sent=True):
        invites = self.all_invites(app, user, sent).order_by('created_at')

        if state == FriendshipRequest.REJECTED_STATE:
            invites = invites.filter(rejected__isnull=False)
        elif state == FriendshipRequest.PENDING_STATE:
            invites = invites.filter(rejected__isnull=True)

        return invites

    def all_invites(self, app, user, sent):
        if sent:
            return self.filter(from_user=user, app=app)
        else:
            return self.filter(to_user=user, app=app)


class FriendshipRequest(models.Model):
    """ Model to represent friendship requests """
    ACCEPT_ACTION = 'accept'
    REJECT_ACTION = 'reject'
    PENDING_STATE = 'pending'
    REJECTED_STATE = 'rejected'
    INVITE_ACTIONS = (ACCEPT_ACTION, REJECT_ACTION)
    INVITE_STATES = (PENDING_STATE, REJECTED_STATE, None)

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    from_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invites_sent')
    to_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invites_received', null=True)
    to_email = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rejected = models.DateTimeField(blank=True, null=True)
    relationship = models.CharField(max_length=30, blank=True, null=True)

    objects = FriendshipRequestManager()

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return "User #%s friend requested #%s" % (self.from_user_id, self.to_user_id)

    def accept(self):
        Friend.objects.create(
            from_user=self.from_user,
            to_user=self.to_user,
            app=self.app
        )

        Friend.objects.create(
            from_user=self.to_user,
            to_user=self.from_user,
            app=self.app
        )

        friendship_request_accepted.send(
            sender=self,
            from_user=self.from_user,
            to_user=self.to_user
        )

        self.delete()

        FriendshipRequest.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user,
            app=self.app
        ).delete()

    def reject(self):
        self.rejected = timezone.now()
        self.save()
        friendship_request_rejected.send(sender=self)

    def cancel(self):
        self.delete()
        friendship_request_canceled.send(sender=self)


class FriendshipManager(models.Manager):
    """ Friendship manager """

    def friends(self, user, app):
        qs = Friend.objects.select_related('from_user', 'to_user').filter(to_user=user, app=app).all()
        friends = [u.from_user for u in qs]

        return friends

    def remove_friend(self, from_user, to_user, app):
        try:
            qs = Friend.objects.filter(
                Q(to_user=to_user, from_user=from_user, app=app) |
                Q(to_user=from_user, from_user=to_user, app=app)
            ).distinct().all()

            if qs:
                sender = qs[0]
                qs.delete()
                friendship_removed.send(
                    sender=sender,
                    from_user=from_user,
                    to_user=to_user
                )
                return True
            else:
                return False
        except Friend.DoesNotExist:
            return False

    def are_friends(self, user1, user2, app):
        try:
            to_filter = dict(to_user=user1, from_user=user2, app=app)
            from_filter = dict(to_user=user2, from_user=user1, app=app)
            qs = Friend.objects.filter(Q(**to_filter) | Q(**from_filter))
            if qs:
                return True
        except Friend.DoesNotExist:
            return False

    def make_friends(self, user1, user2, app):
        Friend.objects.create(from_user=user1, to_user=user2, app=app)
        Friend.objects.create(to_user=user1, from_user=user2, app=app)


class Friend(models.Model):
    """ Model to represent Friendships """

    to_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='all_friends')
    from_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='_unused_relation')
    created_at = models.DateTimeField(auto_now_add=True)
    relationship = models.CharField(max_length=30, blank=True, null=True)

    objects = FriendshipManager()

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return "User #%s is friends with #%s" % (self.to_user_id, self.from_user_id)

    def save(self, *args, **kwargs):
        if self.to_user == self.from_user:
            raise ValidationError("Users cannot be friends with themselves.")
        super(Friend, self).save(*args, **kwargs)
