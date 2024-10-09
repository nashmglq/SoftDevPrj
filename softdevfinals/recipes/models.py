from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(blank=True, null=True, upload_to='images/')
    ingredients = models.IntegerField(blank=True, null=True)
    minutes = models.IntegerField(blank=True, null=True)
    calories = models.IntegerField(blank=True, null=True)
    ingredientsList = models.TextField(blank=True, null=True)
    directions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.ManyToManyField(User, related_name='viewed_recipes', blank=True)
    view_count = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=False)
    favorites = models.ManyToManyField(User, related_name='favorite_recipes', blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('recipe', 'user')  

class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=4, decimal_places=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('recipe', 'user') 



