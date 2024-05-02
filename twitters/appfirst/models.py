from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class BasicUserProfile(models.Model):
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    creation_date = models.DateField(default=timezone.now)
    id = models.AutoField(primary_key=True)

    
    profile_photo = models.ImageField(
        upload_to="profile_photo/", blank=True, null=True
    )
    banner_photo = models.ImageField(
        upload_to="banner_photo/", blank=True, null=True
    )
    email = models.CharField(max_length=200, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return "User: " + str(self.user.username)
    


class FollowRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_follow_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_follow_requests', on_delete=models.CASCADE)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    def delete_request(self):
        self.delete()

class Follower(models.Model):
    creation_date = models.DateField(default=timezone.now)
    id = models.AutoField(primary_key=True)
    following = models.ForeignKey(
        BasicUserProfile,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="following"
    )
    follower = models.ForeignKey(
        BasicUserProfile,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="follower"
    )

    def __str__(self):
        return "Following: " + str(self.following.user.username) + \
                " | Follower: " + str(self.follower.user.username)



class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        # Define your logic for token expiration here, for example, 1 hour expiry time
        return timezone.now() > self.created_at + timezone.timedelta(hours=1)

