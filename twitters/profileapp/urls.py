from django.urls import path
from . import views
# from appfirst import LoginView

urlpatterns = [
    
    path("profile/", views.profile, name="profile"),
    path("profile/<str:other_user_username>/",views.other_user_profile,name="other_user_profile"),
    path('follow/<str:other_user_username>/', views.follow_user, name='follow_user'),  
    path('unfollow_user/<str:other_user_username>/', views.unfollow_user, name='unfollow_user'),
    path('accept_follow_request/<int:follow_request_id>/', views.accept_follow_request, name='accept_follow_request'),
    path('decline_follow_request/<int:follow_request_id>/', views.decline_follow_request, name='decline_follow_request'),
     
   
    
]
