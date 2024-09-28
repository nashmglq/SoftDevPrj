from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q  
from django.shortcuts import redirect
from .forms import RatingCommentForm
from django.views import View
from django.db.models import Count, Avg, Q
from django.utils.timezone import now
from datetime import timedelta

class RecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'home/home.html'
    context_object_name = 'recipes'
    login_url = 'login'

    def get_queryset(self):
        search_query = self.request.GET.get('search')
        ingredients_query = self.request.GET.get('fridge')
        order = self.request.GET.get('order') 
        queryset = Recipe.objects.all()

        # 1 week trending
        time_threshold = now() - timedelta(days=7)

        if ingredients_query:
            ingredients = [ingredient.strip().lower() for ingredient in ingredients_query.split(',')]
            queryset = queryset.filter(
                Q(ingredientsList__icontains=ingredients[0])
            ) if ingredients else queryset

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query.lower())
            )

        queryset = queryset.annotate(
            average_rating=Avg('ratings__score'), #get recipe rating
            views_count=Count('views'),  # Count all views on each recipe
            comments_count=Count('comments', filter=Q(comments__created_at__gte=time_threshold))  # Filter comments last 7 days
        )

        # COMPUTE THE RECIPE TRENDS BY WEIGHT
        queryset = queryset.annotate(
            trending_score=(
                Count('views') * 1 +  # Weight views by 1
                Count('comments', filter=Q(comments__created_at__gte=time_threshold)) * 2 +  # Weight recent comments by 2
                Avg('ratings__score') * 3  # Weight ratings by 3
            )
        )

        if order == 'highest':
            queryset = queryset.order_by('-average_rating', '-created_at')  
        elif order == 'lowest':
            queryset = queryset.order_by('average_rating', '-created_at')
        elif order == 'most_views':
            queryset = queryset.order_by('-views_count')
        elif order == 'trending': 
            queryset = queryset.order_by('-trending_score')
        elif order == 'newest':  
            queryset = queryset.order_by('-created_at')
        elif order == 'oldest':  
              queryset = queryset.order_by('created_at')
        else:
            queryset = queryset.order_by('?')  

        return queryset

class RecipeDetailView(LoginRequiredMixin, DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'  

    def get(self, request, *args, **kwargs):
        recipe = self.get_object()
        
        if not recipe.views.filter(id=request.user.id).exists():
            recipe.views.add(request.user)  
            recipe.view_count += 1  
            recipe.save() 

        return super().get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RatingCommentForm()
        context['comments'] = self.object.comments.all()
        context['rating'] = self.object.ratings.filter(user=self.request.user).first()

        total_ratings = self.object.ratings.count()
        if total_ratings > 0:
            average_rating = self.object.ratings.aggregate(models.Avg('score'))['score__avg']
        else:
            average_rating = None

        context['total_ratings'] = total_ratings
        context['average_rating'] = average_rating

        context['comments_with_ratings'] = [
            {
                'comment': comment,
                'rating': self.object.ratings.filter(user=comment.user).first()
            }
            for comment in context['comments']
        ]

        return context

    

class AddRatingCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        form = RatingCommentForm(request.POST)

        if request.user == recipe.user:
            return redirect(recipe.get_absolute_url())  

        if form.is_valid():
            if not recipe.ratings.filter(user=request.user).exists() and not recipe.comments.filter(user=request.user).exists():
                Rating.objects.create(
                    recipe=recipe,
                    user=request.user,
                    score=form.cleaned_data['score']
                )
                Comment.objects.create(
                    recipe=recipe,
                    user=request.user,
                    content=form.cleaned_data['content']
                )
                return redirect(recipe.get_absolute_url())
        
        return redirect(recipe.get_absolute_url())
    

class UpdateRatingCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        rating = get_object_or_404(Rating, recipe=comment.recipe, user=request.user)

        if request.user == comment.user:
            comment.content = request.POST.get('content', comment.content)  
            comment.save()

            if 'score' in request.POST:
                rating.score = request.POST['score']
                rating.save()

        return redirect(comment.recipe.get_absolute_url())

class DeleteRatingCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        rating = get_object_or_404(Rating, recipe=comment.recipe, user=request.user)

        if request.user == comment.user:
            comment.delete()  
            rating.delete()  

        return redirect(comment.recipe.get_absolute_url())
    

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


