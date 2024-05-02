from django.urls import path
from . import views

urlpatterns = [
    
    path("", views.index, name="index"),
    path("home/<int:page>/", views.home, name="home"),
    path("tweet/<int:tweet_id>/", views.tweet_single, name="tweet_single"),
]
