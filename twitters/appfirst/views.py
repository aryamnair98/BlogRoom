
import random
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import BasicUserProfile
from utils.auth_utils import get_banned_words
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
# from django.core.email import send_mail
from django.conf import settings
from .models import PasswordResetToken
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.hashers import make_password


def signup(request):
    

    if "basic_user_email" in request.session:
        del request.session["basic_user_email"]
        del request.session["basic_user_username"]
        del request.session["basic_user_logged_in"]

    
    invalid_credentials = False
    credentials_taken = False
    contains_space_in_credentials = False

    banned_words = get_banned_words()

    if request.POST.get("signup_submit_button"):
        email = request.POST.get("email")
        
        password = request.POST.get("password")
        password_again = request.POST.get("password_again")
        username = request.POST.get("username")
        message = f'Hello {username}, you have logged in to our application.'
        send_mail(
            'Logged In',
             message,
            'settings.EMAIL_HOST_USER',
             [email],
             fail_silently=False
        )
    

        
        for char in email:
            if char == " ":
                contains_space_in_credentials = True

        for char in username:
            if char == " ":
                contains_space_in_credentials = True

        for char in password:
            if char == " ":
                contains_space_in_credentials = True

        if contains_space_in_credentials == True:
            
            pass
        else:
            
            if bool(username) == False or username == "" \
               or bool(email) == False or email == "" \
               or bool(password) == False or password == "" \
               or bool(password_again) == False or password_again == "":
                invalid_credentials = True
            else:
                
                if username == password:
                    invalid_credentials = True
                else:
                    
                    if password != password_again:
                        invalid_credentials = True
                    else:
                       
                        contains_banned_words = False
                        for word in banned_words:
                            if word == username:
                                contains_banned_words = True
                        if contains_banned_words == True:
                            invalid_credentials = True
                        else:
                            
                            try:
                                existing_username = User.objects.get(
                                    username=username
                                )
                            except ObjectDoesNotExist:
                                existing_username = None

                            try:
                                existing_email = User.objects.get(email=email)
                            except ObjectDoesNotExist:
                                existing_email = None

                            if existing_username != None or existing_email != None:
                                credentials_taken = True
                            else:
                                
                                if len(password) < 8:
                                    invalid_credentials = True
                                else:
                                   
                                    contains_digit = False
                                    for char in password:
                                        if char.isdigit():
                                            contains_digit = True

                                    if contains_digit == True:
                                        
                                        new_user = User.objects.create_user(
                                            username=username,
                                            email=email,
                                            password=password
                                        )
                                        
                                        new_user = User.objects.get(
                                            email=email,
                                            username=username
                                        )
                                        new_settings = BasicUserProfile()
                                        new_settings.email = email
                                        new_settings.user = new_user
                                        new_settings.save()
                                        
                                        request.session["basic_user_email"] = new_user.email
                                        request.session["basic_user_username"] = new_user.username
                                        request.session["basic_user_logged_in"] = True
                                        
                                        return HttpResponseRedirect("/")
                                    else:
                                        invalid_credentials = True

 
    if request.POST.get("auth_demo_submit_btn"):
        random_guest_num = random.randint(0, 10000000)
        random_username = "guest" + str(random_guest_num)
        random_full_name = "guest" + str(random_guest_num)
        random_password = random_guest_num + random_guest_num
        random_email = "guest"+str(random_guest_num)+"@foo.com"
        
        try:
            random_user = User.objects.get(username=random_username)
        except ObjectDoesNotExist:
            random_user = None

        if random_user == None:
            new_guest_user = User.objects.create_user(
                username=random_username,
                email=random_email,
            )
            new_guest_user.save()
            new_guest_user = User.objects.get(username=random_username)
           
            new_user_profile = BasicUserProfile(
                user=new_guest_user,
                email=random_email,
                full_name=random_full_name,
            )
            new_user_profile.save()
          
            request.session["basic_user_email"] = new_guest_user.email
            request.session["basic_user_username"] = new_guest_user.username
            request.session["basic_user_logged_in"] = True
           
            return HttpResponseRedirect("/")
        else:
            pass

    data = {
        "invalid_credentials": invalid_credentials,
        "credentials_taken": credentials_taken,
        "contains_space_in_credentials": contains_space_in_credentials,
    }

    return render(request, "auth/signup.html", data)


def login(request):
    
    if "basic_user_email" in request.session:
        del request.session["basic_user_email"]
        del request.session["basic_user_username"]
        del request.session["basic_user_logged_in"]

    
    invalid_credentials = False

    if request.POST.get("login_form_submit_btn"):
        username = request.POST.get("username")
        password = request.POST.get("password")

        # checking if the inputs are empty
        if bool(username) == False or bool(password) == False:
            invalid_credentials = True
        else:
           
            try:
                user = User.objects.get(username=username)
            except ObjectDoesNotExist:
                user = None

            if user == None:
                invalid_credentials = True
            else:
              
                is_valid = user.check_password(password)

                if is_valid == True:
                   
                    request.session["basic_user_email"] = user.email
                    request.session["basic_user_username"] = user.username
                    request.session["basic_user_logged_in"] = True
                    return HttpResponseRedirect("/")
                else:
                    invalid_credentials = True
    

    

    data = {
         "invalid_credentials": invalid_credentials,
    }

    return render(request, "auth/login.html", data)


def logout(request):
    """
    if users visit this page it logs her out.
    """
    
    if "basic_user_email" in request.session:
        del request.session["basic_user_email"]
        del request.session["basic_user_username"]
        del request.session["basic_user_logged_in"]

    return HttpResponseRedirect("/")


def terms(request):
    """in this page the users can see the terms of the site"""

    
    if "basic_user_email" in request.session:
        del request.session["basic_user_email"]
        del request.session["basic_user_username"]
        del request.session["basic_user_logged_in"]

    data = {}
    return render(request, "auth/terms.html", data)



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            PasswordResetToken.objects.create(user=user, token=token)
            reset_link = request.build_absolute_uri(
                reverse('reset_password', kwargs={'token': token})
            )
            send_mail(
                'Password Reset',
                f'Click the link to reset your password: {reset_link}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            return HttpResponse("Reset link has been sent to your email. Please check your inbox.",{'token': token})
            # Display a message to the user indicating that the reset link has been sent.
        else:
            return HttpResponse("No account found with the provided email.")
            # Display a message to the user indicating that no account with that email exists.
    return render(request, 'auth/forgot_password.html')


def reset_password(request, token):
    password_reset_token = PasswordResetToken.objects.filter(token=token).first()
    if password_reset_token and not password_reset_token.is_expired():
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            user = password_reset_token.user
            user.password = make_password(new_password)
            user.save()
            # Delete the password reset token after the password has been reset
            password_reset_token.delete()
            # Redirect the user to a page indicating that the password has been reset.
        return render(request, 'auth/reset_password.html',{'token': token})
    else:
        # Token is invalid or expired, display an appropriate error message
        pass