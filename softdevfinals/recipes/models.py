from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.pk})
