
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from appfirst.models import BasicUserProfile
from home.models import Tweet
from appfirst.models import FollowRequest



class NotificationLike(models.Model):
    notified = models.ForeignKey(BasicUserProfile,on_delete=models.CASCADE,blank=True,null=True,related_name="notified")
    creation_date = models.DateField(default=timezone.now)
    id = models.AutoField(primary_key=True)
    notifier = models.ForeignKey(BasicUserProfile,on_delete=models.CASCADE,blank=True,null=True,related_name="notifier")
    tweet = models.ForeignKey(Tweet,on_delete=models.CASCADE,blank=True,null=True)

    def __str__(self):
        return "Notification id: " + str(self.id)
    

class NotificationFollowRequest(models.Model):
    sender = models.ForeignKey(BasicUserProfile,on_delete=models.CASCADE,blank=True,null=True,related_name="follow_request_sender")
    receiver = models.ForeignKey(BasicUserProfile,on_delete=models.CASCADE,blank=True,null=True,related_name="follow_request_receiver")
    follow_request = models.ForeignKey(FollowRequest,on_delete=models.CASCADE,blank=True,null=True )
    creation_date = models.DateField(default=timezone.now)
    id = models.AutoField(primary_key=True)
    

    def delete_request(self):
        self.delete()

    def __str__(self):
        return f"Follow request notification from {self.sender} to {self.receiver}"