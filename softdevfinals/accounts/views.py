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

def register(request):

    if request.user.is_authenticated:
        return redirect('home')  

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Custom form with email field
        if form.is_valid():
            user = form.save(commit=False)  # Don't save the user yet
            user.is_active = False  # User needs to verify email
            user.save()

            # Create Profile
            Profile.objects.create(user=user)

            # Generate email verification link
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
            activation_url = f"http://{current_site.domain}{activation_link}"
            
            # Simple email message
            message = f"Hi {user.username},\n\nPlease click the link below to activate your account:\n{activation_url}\n\nThank you!"
            send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            
            messages.success(request, 'Account created! Please check your email to activate your account.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()  # Use the custom form with email
    return render(request, 'accounts/register.html', {'form': form})


def activate(request, uidb64, token):
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
        return redirect('register')

def login_view(request):
    if request.user.is_authenticated:
        print("User is already logged in")  # Debugging line
        return redirect('home') 

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)  # Correct form initialization
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {username}!')
                    return redirect('home')
                else:
                    messages.error(request, 'Your account is not activated yet. Please check your email.')
                    print("qwe")
            else:
                messages.error(request, 'Invalid username or password.')
                print("qwe")
    else:
        form = CustomLoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request) 
    messages.success(request, 'You have been logged out.')
    return redirect('login') 

@login_required(login_url='login')
def home(request):
    print("Accessed home view by:", request.user.username)  # Debugging line
    return render(request, 'home/home.html')