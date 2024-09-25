from django.urls import path
from .views import RecipeDetailView, RecipeCreateView, RecipeUpdateView, RecipeDeleteView

urlpatterns = [
    path('<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('new/', RecipeCreateView.as_view(), name='recipe-create'),
    path('<int:pk>/update/', RecipeUpdateView.as_view(), name='recipe-update'),
    path('<int:pk>/delete/', RecipeDeleteView.as_view(), name='recipe-delete'),
]