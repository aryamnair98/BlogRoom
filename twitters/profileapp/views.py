# Main Imports
import random
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.contrib.auth.models import User
from appfirst.models import BasicUserProfile, Follower,FollowRequest
from home.models import Tweet, TweetLike, TweetComment
from hashtag.models import Topic
from notify.models import NotificationLike,NotificationFollowRequest
from utils.session_utils import get_current_user, get_current_user_profile
# from utils.base_utils import left_nav_tweet_form_processing
# from utils.base_utils import mobile_tweet_form_processing
from utils.base_utils import get_who_to_follow
from utils.base_utils import get_topics_to_follow
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required




def profile(request):
    current_basic_user = get_current_user(request, User, ObjectDoesNotExist)
    current_basic_user_profile = get_current_user_profile(request, User, BasicUserProfile, ObjectDoesNotExist)

    if current_basic_user is None:
        return HttpResponseRedirect("/auth/signup/")

    topics_to_follow = get_topics_to_follow(Topic, ObjectDoesNotExist, random)
    who_to_follow = get_who_to_follow(current_basic_user_profile,BasicUserProfile, ObjectDoesNotExist, random)

    if request.method == "POST":
        tweet_id_to_delete = request.POST.get("tweet_id_to_delete")
        if tweet_id_to_delete:
            try:
                tweet_to_delete = Tweet.objects.get(id=tweet_id_to_delete, user=current_basic_user_profile)
                tweet_to_delete.delete()
            except ObjectDoesNotExist:
                pass  

        tweet_id_to_edit = request.POST.get("tweet_id_to_edit")
        tweet_content = request.POST.get("edited_tweet_content")
        if tweet_id_to_edit and tweet_content:
            try:
                tweet_to_edit = Tweet.objects.get(id=tweet_id_to_edit, user=current_basic_user_profile)
                tweet_to_edit.content = tweet_content
                tweet_to_edit.save()
            except ObjectDoesNotExist:
                pass  
    
    try:
        all_tweets = Tweet.objects.filter(user=current_basic_user_profile).order_by("-id")
    except ObjectDoesNotExist:
        all_tweets = None

    try:
        all_followers = Follower.objects.filter(following=current_basic_user_profile).count()
    except ObjectDoesNotExist:
        all_followers = 0

    try:
        all_followings = Follower.objects.filter(follower=current_basic_user_profile).count()
    except ObjectDoesNotExist:
        all_followings = 0

    if request.POST.get("profile_tweet_comment_submit_btn"):
        current_tweet_id = request.POST.get("hidden_tweet_id")
        return HttpResponseRedirect("/tweet/" + str(current_tweet_id) + "/")

    if request.POST.get("profile_tweet_like_submit_btn"):
        current_tweet_id = request.POST.get("hidden_tweet_id")
        current_tweet = Tweet.objects.get(id=current_tweet_id)
        new_like = TweetLike(tweet=current_tweet, liker=current_basic_user_profile)
        new_like.save()
        current_tweet.tweet_like_amount += 1
        current_tweet.save()
        new_notification = NotificationLike(notified=current_tweet.user, notifier=current_basic_user_profile, tweet=current_tweet)
        new_notification.save()
        return HttpResponseRedirect("/tweet/" + str(current_tweet.id) + "/")

    data = {
        "current_basic_user": current_basic_user,
        "current_basic_user_profile": current_basic_user_profile,
        "who_to_follow": who_to_follow,
        "topics_to_follow": topics_to_follow,
        "all_tweets": all_tweets,
        "tweet_amount": len(all_tweets) if all_tweets is not None else 0,
        "follower_amount": all_followers ,
        "following_amount": all_followings
    }

    return render(request, "profile/profile.html", data)




    
def other_user_profile(request, other_user_username):
    current_basic_user = get_current_user(request, User, ObjectDoesNotExist)
    current_basic_user_profile = get_current_user_profile(request, User, BasicUserProfile, ObjectDoesNotExist)

    if current_basic_user is None:
        return HttpResponseRedirect("/auth/signup/")

    try:
        other_user = User.objects.get(username=other_user_username)
        other_user_profile = BasicUserProfile.objects.get(user=other_user)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/")

    all_tweets = Tweet.objects.filter(user=other_user_profile).order_by("-id")
    all_followers = Follower.objects.filter(following=other_user_profile)
    all_followings = Follower.objects.filter(follower=other_user_profile)
    already_follower = Follower.objects.filter(follower=current_basic_user_profile, following=other_user_profile).exists()
    is_following = already_follower

    if request.method == "POST":
        if "other_user_profile_follow_submit_btn" in request.POST:
            if current_basic_user:
                # Get the user associated with the current_basic_user_profile
                sender_user = current_basic_user_profile.user
            
                # Get the user associated with the other_user_profile
                receiver_user = other_user_profile.user

                # Create follow request
                follow_request = FollowRequest.objects.create(sender=sender_user, receiver=receiver_user, status='pending')

                # Create notification
                NotificationFollowRequest.objects.create(
                    sender=current_basic_user_profile,
                    receiver=other_user_profile,
                    follow_request=follow_request
                )

                is_following = True

                return HttpResponseRedirect(request.path)
        
        # Handle follow request acceptance
        elif "accept_follow_request_btn" in request.POST:
            follow_request_id = request.POST.get("follow_request_id")
            follow_request = FollowRequest.objects.get(id=follow_request_id)
            if follow_request.receiver == current_basic_user_profile.user:
                # Create follower relationship
                Follower.objects.create(follower=current_basic_user_profile, following=other_user_profile)
                # Delete the follow request
                follow_request.delete()
                # Redirect back to the profile page
                return HttpResponseRedirect(request.path)

    data = {
        "current_basic_user": current_basic_user,
        "current_basic_user_profile": current_basic_user_profile,
        "who_to_follow": get_who_to_follow(current_basic_user_profile,BasicUserProfile, ObjectDoesNotExist, random),
        "topics_to_follow": get_topics_to_follow(Topic, ObjectDoesNotExist, random),
        "other_user_profile": other_user_profile,
        "all_tweets": all_tweets,
        "tweet_amount": len(all_tweets),
        "follower_amount": all_followers.count(),
        "following_amount": all_followings.count(),
        "already_follower": already_follower,
        "other_user_username": other_user_username,
        "is_following": is_following,
    }

    return render(request, "profile/other_profile.html", data)



def follow_user(request, other_user_username):
    # Retrieve sender (current user) and receiver (the user to follow)
    
    sender = get_current_user(request, User, ObjectDoesNotExist)
    current_user_profile = get_current_user_profile(request, User, BasicUserProfile, ObjectDoesNotExist)
    
    # Retrieve the user object corresponding to the other_user_username
    try:
        receiver_user = User.objects.get(username=other_user_username)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error'})

    # Retrieve the BasicUserProfile associated with the receiver user
    receiver_profile = get_object_or_404(BasicUserProfile, user=receiver_user)

    if not receiver_profile:
        return JsonResponse({'status': 'error'})
    if FollowRequest.objects.filter(sender=sender, receiver=receiver_user).exists():
    # Check if already following
        if Follower.objects.filter(following=receiver_profile, follower=current_user_profile).exists():
        # User is already following
            return JsonResponse({'status': 'following'})
        else:
        # Follow request exists but user is not following yet
            return JsonResponse({'status': 'pending'})
    
   
    follow_request = FollowRequest.objects.create(sender=sender, receiver=receiver_user, status='pending')
    
    
    NotificationFollowRequest.objects.create(
        sender=current_user_profile,
        receiver=receiver_profile,
        follow_request=follow_request
    )

    return JsonResponse({'status': 'success'})



def unfollow_user(request, other_user_username):
    # Get the current user
    sender = get_current_user(request, User, ObjectDoesNotExist)
    current_user = get_current_user_profile(request, User, BasicUserProfile, ObjectDoesNotExist)

    # Find the user to unfollow
    try:
        receiver_user = User.objects.get(username=other_user_username)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'})
    receiver_profile = get_object_or_404(BasicUserProfile, user=receiver_user)

    # Check if the current user is following the other user
    try:
        follower = Follower.objects.get(follower=current_user, following=receiver_profile)
        follow_request=FollowRequest.objects.filter(sender=sender, receiver=receiver_user)
    except Follower.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'You are not following this user'})

    # Unfollow the user
    follow_request.delete()
    follower.delete()


    # Update is_following to False
    is_following = False

    # Render the template with updated is_following status
    return render(request, 'profile/other_profile.html', {'is_following': is_following,'other_user_username':receiver_user})




def accept_follow_request(request, follow_request_id):
    try:
        follow_request_notification = NotificationFollowRequest.objects.get(id=follow_request_id)
        current_basic_user = get_current_user(request, User, ObjectDoesNotExist)
        if follow_request_notification.receiver.user == current_basic_user:
            # Accept the follow request
            Follower.objects.create(following=follow_request_notification.sender, follower=follow_request_notification.receiver)
            
            # Update notification
            
            follow_request_notification.follow_request.status = 'accepted'
            follow_request_notification.follow_request.save()
            
            
            follow_request_notification.delete()  
            
            # Delete the notification
            return HttpResponseRedirect('/notification/')
        else:
            print("Unauthorized user:", current_basic_user)  
            print("Intended recipient:", follow_request_notification.receiver.user)  
            return JsonResponse({'status': 'error', 'message': 'You are not authorized to accept this follow request.'})
    except NotificationFollowRequest.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Follow request notification does not exist.'})
    



def decline_follow_request(request, follow_request_id):
    try:
        # Retrieve the follow request notification
        follow_request_notification = NotificationFollowRequest.objects.get(id=follow_request_id)
        
        # Get the current user
        current_user = get_current_user(request, User, ObjectDoesNotExist)
        
        # Ensure the current user is the receiver of the follow request
        if follow_request_notification.receiver.user == current_user:
            # Update the status of the follow request
            follow_request = follow_request_notification.follow_request
            # follow_request.status = 'declined'
            follow_request.delete()
            
            # Delete the notification
            follow_request_notification.delete()
            
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'You are not authorized to decline this follow request.'})
    except NotificationFollowRequest.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Follow request notification does not exist.'})
    


