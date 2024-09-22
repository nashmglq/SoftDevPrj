from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),  
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('home/', views.home, name='home')
]
