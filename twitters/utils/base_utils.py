# Left Nav Tweet form processing
def left_nav_tweet_form_processing(request, Tweet, current_basic_user_profile):
    if request.POST.get("hidden_panel_tweet_submit_btn"):
        tweet_content = request.POST.get("tweet_content")
        tweet_image = request.FILES.get("tweet_image")

        new_tweet = Tweet(
            user=current_basic_user_profile, content=tweet_content,
            image=tweet_image
        )
        new_tweet.save()


# Mobile tweet form processing
def mobile_tweet_form_processing(request, Tweet, current_basic_user_profile):
    if request.POST.get("mobile_hidden_tweet_submit_btn"):
        tweet_content = request.POST.get("tweet_content")
        tweet_image = request.FILES.get("tweet_image")

        new_tweet = Tweet(
            user=current_basic_user_profile, content=tweet_content,
            image=tweet_image
        )
        new_tweet.save()



def get_who_to_follow(current_user_profile,BasicUserProfile, ObjectDoesNotExist, random):
    try:
        all_users = BasicUserProfile.objects.exclude(id=current_user_profile.id)
        if not all_users:
            return []
    except ObjectDoesNotExist:
        return []

    who_to_follow = list(all_users)
    return who_to_follow

def get_topics_to_follow(Topic, ObjectDoesNotExist, random):
    try:
        # Retrieve all topics
        all_topics = Topic.objects.all()

        # Check if there are any topics
        if not all_topics.exists():
            return []

        # Get the latest topic
        latest_topic = all_topics.last()

    except ObjectDoesNotExist:
        # Handle the case where the ObjectDoesNotExist exception occurs
        return []

    topics_to_follow = []

    # Choose random topics to follow
    for i in range(3):
        try:
            random_topic = random.choice(all_topics)
            topics_to_follow.append(random_topic)
        except IndexError:
            # Handle the case where the index is out of range
            pass

    return topics_to_follow


