from django.urls import path, include
from . import views
from recipes.views import RecipeListView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.landing_page, name='landing_page'),
    path('login/', views.login_view, name='login'),  
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    path('password-reset/', views.password_reset_request, name='password_reset'), 
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),  
    path('home/', RecipeListView.as_view(), name='home'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.update_user_profile, name='update_user_profile'),
    # path('profile/update-user/', views.update_user, name='update_user'),
    # path('profile/update-profile/', views.update_profile, name='update_profile'),
    path('contact/', views.contact_us, name='contact_us'),
    path('about/', views.about_us, name='about_us'),
    path('change-password/', views.change_password, name='change_password'),
    path('user/<int:user_id>/', views.user_profile, name='user_profile'),
    path('pannel/users/', views.user_list, name='user-list'),
    path('pannel/users/edit/<int:user_id>/', views.edit_user, name='edit-user'),
    path('pannel/users/delete/<int:user_id>/', views.delete_user, name='delete-user'),
    path('pannel/add-category/', views.add_category, name='add-category'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete-category'),

]