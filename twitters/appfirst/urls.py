from django.urls import path
from . import views

urlpatterns = [
    # signup Page
    path("auth/signup/", views.signup, name="signup"),
    # login page
    path("auth/login/", views.login, name="login"),
    # Terms
    path("auth/terms/", views.terms, name="terms"),
    # logout
    path("auth/logout/", views.logout, name="logout"),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
]
