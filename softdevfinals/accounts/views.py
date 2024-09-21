from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import CustomLoginForm 

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() 
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            Profile.objects.create(user=user) 
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        print(f"User already logged in: {request.user.username}")  # Debugging line
        return redirect('home')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                print(f"User authenticated: {user.username}")  # Debugging line
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                print("Invalid username or password.")  # Debugging line
                messages.error(request, 'Invalid username or password.')
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