from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Recipe
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.shortcuts import redirect

class RecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'home/home.html'  
    context_object_name = 'recipes'
    login_url = 'login' 

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)  
        return super().dispatch(request, *args, **kwargs)  


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'  

class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    fields = ['name', 'image', 'ingredients', 'minutes', 'calories', 'directions', 'ingredientsList']
    #template_name = 'home/recipe_detail.html'  #
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class RecipeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipe
    fields = ['name', 'image', 'ingredients', 'minutes', 'calories', 'directions', 'ingredientsList']
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        recipe = self.get_object()
        if self.request.user == recipe.user:
            return True
        return False
    
class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipe
    success_url = '/home/'
    def test_func(self):
        recipe = self.get_object()
        if self.request.user == recipe.user:
            return True
        return False

def home(request):
    context = {
        'recipes': Recipe.objects.all()
    }
    return render(request, 'home/home.html', context)


