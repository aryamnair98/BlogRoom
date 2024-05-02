# Main Imports
import random

# Django Imports
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.contrib.auth.models import User

# My Module Imports
from appfirst.models import BasicUserProfile, Follower
from home.models import Tweet, TweetLike, TweetComment
from hashtag.models import Topic
from .models import NotificationLike,NotificationFollowRequest
from profileapp.models import *

from utils.session_utils import get_current_user, get_current_user_profile

from utils.base_utils import get_who_to_follow
from utils.base_utils import get_topics_to_follow
from .forms import NotificationForm


def notification(request):
    # Get current user and their profile
    current_basic_user = get_current_user(request, User, ObjectDoesNotExist)
    current_basic_user_profile = get_current_user_profile(request, User, BasicUserProfile, ObjectDoesNotExist)

    # Redirect if user is not authenticated or has no profile
    if current_basic_user is None or current_basic_user_profile is None:
        return HttpResponseRedirect("/auth/signup/")  

    # Get topics and users to follow
    topics_to_follow = get_topics_to_follow(Topic, ObjectDoesNotExist, random)
    who_to_follow = get_who_to_follow(current_basic_user_profile,BasicUserProfile, ObjectDoesNotExist, random)

    # Process form submission
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to prevent form resubmission
            return HttpResponseRedirect(request.path_info)
    else:
        form = NotificationForm()

    # Get all notifications for the current user profile
    try:
        all_notifications = NotificationLike.objects.filter(notified=current_basic_user_profile).order_by("-id")
    except ObjectDoesNotExist:
        all_notifications = None

    # Get follow request notifications for the current user profile
    try:
        follow_request_notifications = NotificationFollowRequest.objects.filter(receiver=current_basic_user_profile).order_by("-id")
    except ObjectDoesNotExist:
        follow_request_notifications = None

    # Prepare data to pass to the template
    data = {
        "current_basic_user": current_basic_user,
        "current_basic_user_profile": current_basic_user_profile,
        "who_to_follow": who_to_follow,
        "topics_to_follow": topics_to_follow,
        "all_notifications": all_notifications,
        "follow_request_notifications": follow_request_notifications,
        "form": form,  
    }

    # Render the notification template with the provided data
    return render(request, "notifications/notification.html", data)
