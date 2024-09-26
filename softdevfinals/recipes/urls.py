from django.urls import path
from .views import *

urlpatterns = [
    path('<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('new/', RecipeCreateView.as_view(), name='recipe-create'),
    path('<int:pk>/add-rating-comment/', AddRatingCommentView.as_view(), name='add-rating-comment'),
    path('recipe/comment/<int:pk>/update/', UpdateRatingCommentView.as_view(), name='update-rating-comment'),
    path('recipe/comment/<int:pk>/delete/', DeleteRatingCommentView.as_view(), name='delete-rating-comment'),
    path('<int:pk>/update/', RecipeUpdateView.as_view(), name='recipe-update'),
    path('<int:pk>/delete/', RecipeDeleteView.as_view(), name='recipe-delete'),
]