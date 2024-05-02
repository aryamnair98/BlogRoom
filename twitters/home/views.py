
import random
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.contrib.auth.models import User
from appfirst.models import BasicUserProfile, Follower
from .models import Tweet, TweetLike, TweetComment
from hashtag.models import Topic
from notify.models import NotificationLike
from utils.session_utils import get_current_user, get_current_user_profile
from utils.base_utils import left_nav_tweet_form_processing
from utils.base_utils import mobile_tweet_form_processing
from utils.base_utils import get_who_to_follow
from utils.base_utils import get_topics_to_follow
from django.shortcuts import render, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.views import View



def index(request):
    
    current_basic_user = get_current_user(request, User, ObjectDoesNotExist)

    current_basic_user_profile = get_current_user_profile(
        request,
        User,
        BasicUserProfile,
        ObjectDoesNotExist
    )

    if current_basic_user == None:
        return HttpResponseRedirect("/auth/signup/")
    else:
        return HttpResponseRedirect("/home/0/")
    



def home(request, page):
    current_basic_user = get_current_user(request, User, ObjectDoesNotExist)
    current_basic_user_profile = get_current_user_profile(request, User, BasicUserProfile, ObjectDoesNotExist)

    if current_basic_user is None or current_basic_user_profile is None:
        return HttpResponseRedirect("/auth/signup/")  

    left_nav_tweet_form_processing(request, Tweet, current_basic_user_profile)
    mobile_tweet_form_processing(request, Tweet, current_basic_user_profile)

    try:
        topics_to_follow = get_topics_to_follow(Topic, ObjectDoesNotExist,random)
        who_to_follow = get_who_to_follow(current_basic_user_profile,BasicUserProfile, ObjectDoesNotExist,random)
    except ObjectDoesNotExist:
        topics_to_follow = []
        who_to_follow = []

    if request.method == "POST":
        
        
        if request.POST.get("right_nav_search_submit_btn"):
            
            search_input = request.POST.get("search_input")
            return HttpResponseRedirect("/search/" + str(search_input) + "/")

        if request.POST.get("base_who_to_follow_submit_btn"):
            
            hidden_user_id = request.POST.get("hidden_user_id")
            followed_user = BasicUserProfile.objects.get(id=hidden_user_id)
            
            
            try:
                Follower.objects.get(following=followed_user, follower=current_basic_user_profile)
            except ObjectDoesNotExist:
                new_follow = Follower(following=followed_user, follower=current_basic_user_profile)
                new_follow.save()

            return HttpResponseRedirect("/profile/" + followed_user.user.username + "/")

        if request.POST.get("home_page_tweet_form_submit_btn"):
            tweet_content = request.POST.get("tweet_content")
            tweet_image = request.FILES.get("tweet_image")
            
            new_tweet = Tweet(user=current_basic_user_profile, content=tweet_content, image=tweet_image)
            new_tweet.save()
            
            return HttpResponseRedirect("/")

        if request.POST.get("tweet_cell_comment_submit_btn"):
            current_tweet_id = request.POST.get("hidden_tweet_id")
            current_tweet = Tweet.objects.get(id=current_tweet_id)
            return HttpResponseRedirect("/tweet/" + str(current_tweet.id) + "/")

        if request.POST.get("tweet_cell_like_submit_btn"):
            current_tweet_id = request.POST.get("hidden_tweet_id")
            current_tweet = Tweet.objects.get(id=current_tweet_id)
            
            try:
                TweetLike.objects.get(tweet=current_tweet, liker=current_basic_user_profile)
            except ObjectDoesNotExist:
                new_like = TweetLike(tweet=current_tweet, liker=current_basic_user_profile)
                new_like.save()
                new_notification = NotificationLike(notified=current_tweet.user, notifier=current_basic_user_profile, tweet=current_tweet)
                new_notification.save()
                
            return HttpResponseRedirect("/tweet/" + str(current_tweet.id) + "/")

    
    try:
        all_followings = Follower.objects.filter(follower=current_basic_user_profile)
        tweet_feed = Tweet.objects.filter(user__in=[following.following for following in all_followings]).order_by("-id")
        current_user_tweets = Tweet.objects.filter(user=current_basic_user_profile)
        tweet_feed = (tweet_feed | current_user_tweets).order_by("-id")

    except ObjectDoesNotExist:
        tweet_feed = []
    
    page = 0

    if tweet_feed:
        
        page = max(page, 1)  

        
        posts_per_page = 45
        post_records_starting_point = (page - 1) * posts_per_page
        post_records_ending_point = page * posts_per_page

        
        post_records_ending_point = min(post_records_ending_point, len(tweet_feed))
        tweet_feed = tweet_feed[post_records_starting_point:post_records_ending_point]
        tweet_comment_amounts = {tweet.id: TweetComment.objects.filter(tweet=tweet).count() for tweet in tweet_feed}
        tweet_like_amounts = {tweet.id: TweetLike.objects.filter(tweet=tweet).count() for tweet in tweet_feed}
    else:
        tweet_comment_amounts = {}
        tweet_like_amounts = {}


    previous_page = max(page - 1, 1)  
    next_page = page + 1
    data = {
        "current_basic_user": current_basic_user,
        "current_basic_user_profile": current_basic_user_profile,
        "who_to_follow": who_to_follow,
        "topics_to_follow": topics_to_follow,
        "tweet_feed": tweet_feed,
        "tweet_comment_amounts": tweet_comment_amounts,
        "tweet_like_amounts": tweet_like_amounts,
        "current_page": page,
        "previous_page": previous_page,
        "next_page": next_page,
    }

    return render(request, "home/home.html", data)



def tweet_single(request, tweet_id):
    current_basic_user = get_current_user(request, User, ObjectDoesNotExist)
    current_basic_user_profile = get_current_user_profile(request, User, BasicUserProfile, ObjectDoesNotExist)

    topics_to_follow = get_topics_to_follow(Topic, ObjectDoesNotExist, random)
    who_to_follow = get_who_to_follow(current_basic_user_profile,BasicUserProfile, ObjectDoesNotExist, random)

    try:
        current_tweet = Tweet.objects.get(id=tweet_id)
    except ObjectDoesNotExist:
        current_tweet = None

    try:
        current_tweet_likes = TweetLike.objects.filter(tweet=current_tweet)
    except ObjectDoesNotExist:
        current_tweet_likes = None

    try:
        current_tweet_comments = TweetComment.objects.filter(tweet=current_tweet).order_by("-id")
    except ObjectDoesNotExist:
        current_tweet_comments = None

    if request.method == "POST" and request.POST.get("single_tweet_like_submit_btn"):
        current_tweet = Tweet.objects.get(id=tweet_id)
        existing_like = TweetLike.objects.filter(tweet=current_tweet, liker=current_basic_user_profile).first()
        if not existing_like:
            new_like = TweetLike(tweet=current_tweet, liker=current_basic_user_profile)
            new_like.save()
            current_tweet.tweet_like_amount += 1
            current_tweet.save()
            new_notification = NotificationLike(notified=current_tweet.user, notifier=current_basic_user_profile, tweet=current_tweet)
            new_notification.save()
          
        else:
            existing_like.delete()
            current_tweet.tweet_like_amount = max(current_tweet.tweet_like_amount - 1, 0)
            current_tweet.save()
            
        return HttpResponseRedirect("/tweet/" + str(current_tweet.id) + "/")
    
    if request.POST.get("single_tweet_reply_submit_btn"):
        reply_content = request.POST.get("reply_content")
        if bool(reply_content) == False or reply_content == "":
            pass
        else:
            new_comment = TweetComment(
                tweet=current_tweet,
                content=reply_content,
                commentor=current_basic_user_profile,
            )
            new_comment.save()
            current_tweet.tweet_comment_amount += 1
            current_tweet.save()
            return HttpResponseRedirect("/tweet/"+str(current_tweet.id)+"/")

    
    if request.POST.get("single_tweet_comment_like_submit_btn"):
        comment_id = request.POST.get("comment_id")
        comment = TweetComment.objects.get(id=comment_id)
        comment.like_amount += 1
        comment.save()
        return HttpResponseRedirect("/tweet/"+str(current_tweet.id)+"/")
    try:
        current_tweet = Tweet.objects.get(id=tweet_id)
    except ObjectDoesNotExist:
        current_tweet = None

    is_owner = False
    if current_basic_user_profile == current_tweet.user:
        is_owner = True

    if request.method == "POST":
        if request.POST.get("edit_tweet_submit_btn"):
            new_content = request.POST.get("new_content")
            current_tweet.edit_tweet(new_content)
            return HttpResponseRedirect("/tweet/"+str(current_tweet.id)+"/")

        if request.POST.get("delete_tweet_submit_btn"):
            current_tweet.delete_tweet()
            return HttpResponseRedirect("/home/0/")

    data = {
        "current_basic_user": current_basic_user,
        "current_basic_user_profile": current_basic_user_profile,
        "who_to_follow": who_to_follow,
        "topics_to_follow": topics_to_follow,
        "current_tweet": current_tweet,
        "current_tweet_likes": current_tweet_likes,
        "current_tweet_like_amount": len(current_tweet_likes),
        "current_tweet_comments": current_tweet_comments,
        "is_owner": is_owner,
    }

    if current_basic_user == None:
        return HttpResponseRedirect("/auth/signup/")
    else:
        return render(request, "home/single_tweet.html", data)
    

class GoogleLoginCallbackView(View):
    def get(self, request):
        # Handle the callback from Google OAuth
        return HttpResponse("Callback from Google received")
