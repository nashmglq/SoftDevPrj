from django.urls import path, include
from . import views
from recipes .views import RecipeListView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),  
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    path('home/', RecipeListView.as_view(), name='home'),
    path('recipes/', include('recipes.urls')), 
]
