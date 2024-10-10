from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q  
from django.shortcuts import redirect
from .forms import RatingCommentForm
from django.views import View
from django.db.models import Q, Avg, Count, Case, When, IntegerField
from django.utils.timezone import now
from datetime import timedelta

def get_recommendations(user):

    favorite_recipes = user.favorite_recipes.all()

    if not favorite_recipes.exists():
        return Recipe.objects.none()

    categories = favorite_recipes.values_list('category', flat=True)


    recommended_recipes = Recipe.objects.filter(
        category__in=categories
    )

    return recommended_recipes.distinct()


class RecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'home/home.html'
    context_object_name = 'recipes'
    login_url = 'login'

    def get_queryset(self):
        search_query = self.request.GET.get('search')
        ingredients_query = self.request.GET.get('fridge')
        order = self.request.GET.get('order')
        category_filter = self.request.GET.get('category')
        user = self.request.user  # Get the current user
        queryset = Recipe.objects.all()

        time_threshold = now() - timedelta(days=7)

        # Filter by ingredients
        if ingredients_query:
            ingredients = [ingredient.strip().lower() for ingredient in ingredients_query.split(',')]
            queryset = queryset.filter(
                Q(ingredientsList__icontains=ingredients[0])
            ) if ingredients else queryset

        # Filter by search query
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query.lower())
            )

        # Filter by category
        if category_filter:
            queryset = queryset.filter(category__name__iexact=category_filter)

        # Get recommended recipes
        recommended_recipes = get_recommendations(user)

        # Annotate with recommendations
        queryset = queryset.annotate(
            is_recommended=Case(
                When(id__in=recommended_recipes.values_list('id', flat=True), then=1),
                default=0,
                output_field=IntegerField()
            )
        )

        # Annotate with ratings and counts
        queryset = queryset.annotate(
            average_rating=Avg('ratings__score'),
            views_count=Count('views'),
            comments_count=Count('comments', filter=Q(comments__created_at__gte=time_threshold)),
            trending_score=(
                Count('views') * 1 + 
                Count('comments', filter=Q(comments__created_at__gte=time_threshold)) * 2 + 
                Avg('ratings__score') * 3
            )
        )

        # Sort based on the selected order
        queryset = queryset.order_by('-is_recommended')  

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
            queryset = queryset.order_by('-is_recommended', '?') 

        # Calculate integer and fractional parts for average rating
        for recipe in queryset:
            if recipe.average_rating is not None:
                recipe.integer_part = int(recipe.average_rating)
                recipe.fractional_part = recipe.average_rating - recipe.integer_part
            else:
                recipe.integer_part = 0
                recipe.fractional_part = 0.0

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('name')
        context['recommended_recipes'] = get_recommendations(self.request.user)  
        return context


def get_top_trending_recipes():
    time_threshold = now() - timedelta(days=7)
    
    top_trending_recipes = Recipe.objects.annotate(
        views_count=Count('views'),
        comments_count=Count('comments', filter=Q(comments__created_at__gte=time_threshold)),
        trending_score=(
            Count('views') * 1 +
            Count('comments', filter=Q(comments__created_at__gte=time_threshold)) * 2 +
            Avg('ratings__score') * 3
        )
    ).order_by('-trending_score')[:5]  # Get the top 5 trending recipes

    return top_trending_recipes

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

        # Process ingredientsList and directions into lists, removing empty strings
        context['ingredientsList'] = [ingredient.strip() for ingredient in self.object.ingredientsList.split('\n') if ingredient.strip()] if self.object.ingredientsList else []
        context['directions'] = [direction.strip() for direction in self.object.directions.split('\n') if direction.strip()] if self.object.directions else []

        # Existing context data code
        context['form'] = RatingCommentForm()
        context['comments'] = self.object.comments.all()
        context['rating'] = self.object.ratings.filter(user=self.request.user).first()

        total_ratings = self.object.ratings.count()
        if total_ratings > 0:
            average_rating = self.object.ratings.aggregate(models.Avg('score'))['score__avg']
            integer_part = int(average_rating)  # Get the integer part
            fractional_part = average_rating - integer_part  # Get the fractional part
        else:
            average_rating = None
            integer_part = None
            fractional_part = None

        context['total_ratings'] = total_ratings
        context['average_rating'] = average_rating
        context['integer_part'] = integer_part
        context['fractional_part'] = fractional_part

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

        # If the user is a superuser, they can delete any rating associated with the comment's recipe
        if request.user.is_superuser:
            rating = get_object_or_404(Rating, recipe=comment.recipe)
        else:
            # Regular users can only delete their own ratings
            rating = get_object_or_404(Rating, recipe=comment.recipe, user=request.user)

        if request.user == comment.user or request.user.is_superuser:
            comment.delete()
            rating.delete()

        return redirect(comment.recipe.get_absolute_url())

    

class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    fields = ['name', 'image', 'ingredients', 'minutes', 'calories', 'directions', 'ingredientsList', 'category']
    #template_name = 'home/recipe_detail.html'  #

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Sort the categories alphabetically
        form.fields['category'].queryset = Category.objects.all().order_by('name')
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    
class RecipeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipe
    fields = ['name', 'image', 'ingredients', 'minutes', 'calories', 'directions', 'ingredientsList', 'category']
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
        # Allow superuser to delete any recipe
        if self.request.user.is_superuser or self.request.user == recipe.user:
            return True
        return False
    
def home(request):
    context = {
        'recipes': Recipe.objects.all()
    }
    return render(request, 'home/home.html', context)

class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe.favorites.add(request.user)
        return redirect(recipe.get_absolute_url())

class RemoveFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe.favorites.remove(request.user)
        return redirect(recipe.get_absolute_url())

class FavoriteListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'recipes/favorites.html'
    context_object_name = 'favorite_recipes'

    def get_queryset(self):
        return self.request.user.favorite_recipes.all()


