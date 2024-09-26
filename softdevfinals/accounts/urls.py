from django.urls import path, include
from . import views
from recipes.views import RecipeListView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),  
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    path('password-reset/', views.password_reset_request, name='password_reset'), 
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),  
    path('home/', RecipeListView.as_view(), name='home') 
]