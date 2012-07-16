from django.db import models
from django.contrib.auth.models import User
 
class Tweet(models.Model):
    message = models.CharField(max_length=140)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class Wish(models.Model):
    description = models.CharField(max_length=140)
    link = models.CharField(max_length=255)
    photo = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

class Likeit(models.Model):
    description = models.CharField(max_length=140)
    link = models.CharField(max_length=255)
    photo = models.CharField(max_length=255)
    wished = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)

    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()

    invitation_code = models.CharField(max_length=20)
    subsribeNewletter = models.BooleanField()
    subsribePromotion = models.BooleanField()

    phone = models.CharField(max_length=25)
    
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    # What is this?
    def __unicode__(self):
        return u"%s the place" % self.get_full_name()

