from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token 
from .models import Profile
from .forms import CustomLoginForm, CustomUserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import password_validation
from django.contrib.auth.decorators import login_required

def register(request):
    if request.user.is_authenticated:
        return redirect('home')  

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'This email is already in use.')
            else:
                user = form.save(commit=False)
                user.is_active = False 
                user.save()

                Profile.objects.create(user=user)

                current_site = get_current_site(request)
                mail_subject = 'Activate your account'
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = account_activation_token.make_token(user)
                activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
                activation_url = f"http://{current_site.domain}{activation_link}"
                
                message = f"Hi {user.username},\n\nPlease click the link below to activate your account:\n{activation_url}\n\nThank you!"
                send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

                messages.success(request, 'Account created! Please check your email to activate your account.')
                return redirect('resend_verification') 
    else:
        form = CustomUserCreationForm()  

    return render(request, 'accounts/register.html', {'form': form})


def activate(request, uidb64, token):
    if request.user.is_authenticated:
        return redirect('home')  

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated. You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return render(request, 'accounts/invalid.html')

def login_view(request):
    if request.user.is_authenticated:
        print("User is already logged in") 
        return redirect('home') 

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)  
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            try:
                user = User.objects.get(email=email)

                if user.is_active and user.check_password(password):
                    login(request, user)
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid email or password.', extra_tags='login')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.', extra_tags='login')
                print("User does not exist.")
    else:
        form = CustomLoginForm()

    return render(request, 'accounts/login.html', {'form': form})




def logout_view(request):
    logout(request) 
    messages.success(request, 'You have been logged out.')
    return redirect('login') 


def resend_verification_email(request):
    if request.user.is_authenticated:
        return redirect('home')  

    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user and not user.is_active:
                current_site = get_current_site(request)
                mail_subject = 'Activate your account'
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = account_activation_token.make_token(user)
                activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
                activation_url = f"http://{current_site.domain}{activation_link}"
                
                message = f"Hi {user.username},\n\nPlease click the link below to activate your account:\n{activation_url}\n\nThank you!"
                send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

                messages.success(request, 'Verification email has been resent. Please check your inbox.', extra_tags='resend_email')
            else:
                messages.error(request, 'This email is already activated.', extra_tags='resend_email')
        except User.DoesNotExist:
            messages.error(request, 'The email address you entered does not exist in our records.', extra_tags='resend_email')

    return render(request, 'accounts/resend_verification.html')



def password_reset_request(request):
    if request.user.is_authenticated:
        return redirect('home')  


    if request.user.is_authenticated:
        print("User is already logged in") 
        return redirect('home') 

    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            current_site = get_current_site(request)
            mail_subject = 'Password Reset Requested'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_url = f"http://{current_site.domain}{reset_link}"

            message = f"Hi {user.username},\n\nPlease click the link below to reset your password:\n{reset_url}\n\nThank you!"
            send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            messages.success(request, 'Password reset email has been sent. Please check your inbox.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'This email is not registered.')
    return render(request, 'accounts/password_reset.html')


def password_reset_request(request):

    if request.user.is_authenticated:
        print("User is already logged in") 
        return redirect('home') 

    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            current_site = get_current_site(request)
            mail_subject = 'Password Reset Requested'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_url = f"http://{current_site.domain}{reset_link}"

            message = f"Hi {user.username},\n\nPlease click the link below to reset your password:\n{reset_url}\n\nThank you!"
            send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            messages.success(request, 'Password reset email has been sent. Please check your inbox.', extra_tags='password_reset')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'This email is not registered.', extra_tags='password_reset')
    return render(request, 'accounts/password_reset.html')


def password_reset_confirm(request, uidb64, token):
    if request.user.is_authenticated:
        print("User is already logged in") 
        return redirect('home') 

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if user.check_password(new_password):
                messages.error(request, 'The new password cannot be the same as the old password. Please choose a different password.', extra_tags='password_reset_confirm')
            else:
                try:
                    password_validation.validate_password(password=new_password, user=user)

                    if new_password == confirm_password:
                        user.set_password(new_password)
                        user.save()
                        messages.success(request, 'Your password has been successfully reset. You can now log in.', extra_tags='password_reset_confirm')
                        return redirect('login')
                    else:
                        messages.error(request, 'Passwords do not match. Please try again.', extra_tags='password_reset_confirm')

                except Exception as e:
                    messages.error(request, str(e), extra_tags='password_reset_confirm')  

        return render(request, 'accounts/password_reset_confirm.html', {'valid_link': True})
    else:
        messages.error(request, 'The password reset link is invalid.', extra_tags='password_reset_confirm')
        return render(request, 'accounts/invalid.html', {'valid_link': False})

@login_required    
def profile(request):
    return render(request, 'accounts/profile.html')
 