from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
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
from recipes.models import Category
from .forms import CustomLoginForm, CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm, ContactForm, CategoryForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import password_validation
from django.contrib.auth.decorators import login_required
from recipes.models import Recipe
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError 
from django.core import validators 
from django.contrib.auth.decorators import user_passes_test


from recipes.views import RecipeListView
from recipes.models import Recipe
from django.db.models import Q, Avg, Count, Case, When, IntegerField
from datetime import timedelta
from django.utils import timezone
import random

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

                # Check if the profile already exists before creating a new one
                if not hasattr(user, 'profile'):
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
        return redirect('home') 

    error_message = ""  # Initialize an error message variable

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)  
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            try:
                user = User.objects.get(email=email)

                if user.is_active:
                    if user.check_password(password):
                        login(request, user)
                        return redirect('home')
                    else:
                        error_message = 'Invalid email or password.'
                else:
                    error_message = 'Your account is not active. Please check your email to activate it.'

            except User.DoesNotExist:
                error_message = 'Invalid email or password.'
        else:
            error_message = 'Please correct the errors below.'

    else:
        form = CustomLoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'error_message': error_message})




def logout_view(request):
    logout(request) 
    messages.success(request, 'You have been logged out.')
    return redirect('landing_page') 


def resend_verification_email(request):
    if request.user.is_authenticated:
        return redirect('home')  

    error_message_resend_email = ""  # Initialize an error message variable
    success_message_resend_email = ""  # Initialize a success message variable

    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:  # Check if email is provided
            error_message_resend_email = 'Please enter your email address.'
        else:
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

                    success_message_resend_email = 'Verification email has been resent. Please check your inbox.'
                else:
                    error_message_resend_email = 'This email is already activated.'
            except User.DoesNotExist:
                error_message_resend_email = 'The email address you entered does not exist in our records.'

    # Pass messages to the template only for this specific function
    return render(request, 'accounts/resend_verification.html', {
        'error_message_resend_email': error_message_resend_email,
        'success_message_resend_email': success_message_resend_email,
    })


def password_reset_request(request):
    if request.user.is_authenticated:
        return redirect('home')

    # Initialize message variables
    error_message_reset_password = ""
    success_message_reset_password = ""

    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)

            # Check if the user is active
            if not user.is_active:
                error_message_reset_password = 'This account is not active. Please contact support.'
            else:
                current_site = get_current_site(request)
                mail_subject = 'Password Reset Requested'
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                reset_url = f"http://{current_site.domain}{reset_link}"

                message = f"Hi {user.username},\n\nPlease click the link below to reset your password:\n{reset_url}\n\nThank you!"
                send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

                # Set success message and render the same page
                success_message_reset_password = 'Password reset email has been sent. Please check your inbox.'

        except User.DoesNotExist:
            error_message_reset_password = 'This email is not registered. Please check the email you entered.'
        except Exception as e:
            error_message_reset_password = f'An error occurred: {str(e)}'

    # Render the password reset page with messages
    return render(request, 'accounts/password_reset.html', {
        'error_message_reset_password': error_message_reset_password,
        'success_message_reset_password': success_message_reset_password,
    })


def password_reset_confirm(request, uidb64, token):
    if request.user.is_authenticated:
        print("User is already logged in") 
        return redirect('home') 

    error_message_confirm_reset_password = ""  # Initialize an error message variable 
    success_message_confirm_reset_password = ""  # Initialize a success message variable

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
                error_message_confirm_reset_password = 'The new password cannot be the same as the old password. Please choose a different password.'
            else:
                try:
                    # Validate the password, this will raise an exception if it's common or invalid
                    password_validation.validate_password(password=new_password, user=user)

                    if new_password == confirm_password:
                        user.set_password(new_password)
                        user.save()
                        success_message_confirm_reset_password = 'Your password has been successfully reset. You can now log in.'
                        messages.success(request, success_message_confirm_reset_password, extra_tags='password_reset_confirm')
                        return redirect('login')
                    else:
                        error_message_confirm_reset_password = 'Passwords do not match. Please try again.'

                except validators.ValidationError as e:
                    # Handle common password or other validation errors
                    error_message_confirm_reset_password = ' '.join(e.messages)  # Join error messages into a single string

                except Exception as e:
                    error_message_confirm_reset_password = str(e)

        return render(request, 'accounts/password_reset_confirm.html', {
            'valid_link': True,
            'error_message_confirm_reset_password': error_message_confirm_reset_password,
            'success_message_confirm_reset_password': success_message_confirm_reset_password,
        })
    else:
        error_message_confirm_reset_password = 'The password reset link is invalid.'
        messages.error(request, error_message_confirm_reset_password, extra_tags='password_reset_confirm')
        return render(request, 'accounts/invalid.html', {
            'valid_link': False,
            'error_message_confirm_reset_password': error_message_confirm_reset_password,
        })
    
    

@login_required
def profile(request):
    user_recipes = Recipe.objects.filter(user=request.user)  # Filter recipes by user
    # Calculate average rating for each user's recipe
    for recipe in user_recipes:
        if recipe.ratings.exists():
            recipe.average_rating = recipe.ratings.aggregate(Avg('score'))['score__avg']
            recipe.integer_part = int(recipe.average_rating)
            recipe.fractional_part = recipe.average_rating - recipe.integer_part
        else:
            recipe.average_rating = None
            recipe.integer_part = 0
            recipe.fractional_part = 0.0

    context = {
        'user_recipes': user_recipes,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def update_user_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your information has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'accounts/profile_edit_profile.html', context)




def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            send_mail(
                f'Contact Us Form Submission: {subject}',
                message,
                email,  
                [settings.EMAIL_HOST_USER], 
                fail_silently=False,
            )

            user_message = f"Thank you for contacting us!\n\nSubject: {subject}\n\nYour Message:\n{message}\n\nWe have received your message and will get back to you soon."
            send_mail(
                'Thank You for Contacting Us',
                user_message,
                settings.EMAIL_HOST_USER, 
                [email],  
                fail_silently=False,
            )

            return redirect('contact_us') 
    else:
        form = ContactForm()

    return render(request, 'contact/contact_us.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            new_password = form.cleaned_data.get('new_password1')
            old_password = request.POST.get('old_password')
        
            if request.user.check_password(old_password):
                if old_password == new_password:
                    form.add_error('new_password1', 'The new password cannot be the same as the old password.')
                else:
                    user = form.save()
                    update_session_auth_hash(request, user)  
                    messages.success(request, 'Your password has been changed successfully!')
                    return redirect('home')  
            else:
                messages.error(request, 'The old password is incorrect.')

        else:
            messages.error(request, 'Please correct the error below.')

    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})



def landing_page(request):
    if request.user.is_authenticated:
        return redirect('home')

    # Define a time threshold for recent comments (e.g., last 30 days)
    time_threshold = timezone.now() - timedelta(days=30)

    # Fetch the top 5 trending recipes with annotations
    queryset = Recipe.objects.all().annotate(
        average_rating=Avg('ratings__score'),
        views_count=Count('views'),
        comments_count=Count('comments', filter=Q(comments__created_at__gte=time_threshold)),
        trending_score=(
            Count('views') * 1 + 
            Count('comments', filter=Q(comments__created_at__gte=time_threshold)) * 2 + 
            Avg('ratings__score') * 3
        )
    ).order_by('-trending_score')[:5]  # Get the top 5 trending recipes

    # Randomly select 2 recipes from the top 5
    trending_recipes = random.sample(list(queryset), k=min(2, len(queryset)))

    return render(request, 'accounts/landing.html', {'trending_recipes': trending_recipes})



@login_required
def user_profile(request, user_id):
    # Get the user object for the specified user_id
    user = get_object_or_404(User, id=user_id)
    user_recipes = Recipe.objects.filter(user=user)  # Get recipes created by this user

    context = {
        'user': user,
        'user_recipes': user_recipes,
    }
    
    return render(request, 'accounts/user_profile.html', context)



# Admin Pannel

def is_superuser_check(user):
    if not user.is_superuser:
        return False
    return True

@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    query = request.GET.get('q', '')  # Get search query from the request
    if query:
        users = User.objects.filter(username__icontains=query)  # Filter users by username
    else:
        users = User.objects.all()  # Get all users if no query
    
    categories = Category.objects.all()  # Fetch all categories

    context = {
        'users': users,
        'query': query,
        'categories': categories,  # Add categories to the context
    }
    return render(request, 'admin/user_list.html', context)

@user_passes_test(lambda u: u.is_superuser)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']  # Get the email from the form
        is_active = request.POST.get('is_active', 'off') == 'on'
        is_superuser = request.POST.get('is_superuser', 'off') == 'on'
        is_staff = request.POST.get('is_staff', 'off') == 'on'  # Add is_staff handling

        user.username = username
        user.email = email  # Update the email
        user.is_active = is_active
        user.is_superuser = is_superuser
        user.is_staff = is_staff  # Update is_staff as well
        user.save()

        messages.success(request, 'User updated successfully')
        return redirect('user-list')

    context = {
        'user': user,
    }
    return render(request, 'admin/edit_user.html', context)


@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully')
        return redirect('user-list')

    context = {
        'user': user,
    }
    return render(request, 'admin/delete_user.html', context)

@user_passes_test(lambda u: u.is_superuser)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new category
            messages.success(request, 'Category added successfully')
            return redirect('home')  # Redirect to the home page after success
    # If the request method is not POST or the form is invalid, redirect to home without rendering anything.
    return redirect('home')

@user_passes_test(lambda u: u.is_superuser)
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted successfully')
    return redirect('user-list')

def about_us(request):
    return render(request, 'accounts/about_us.html')