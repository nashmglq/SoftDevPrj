from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ('Chinese', 'Chinese'),
        ('American', 'American'),
        ('Filipino', 'Filipino'),
        ('Italian', 'Italian'),
        ('Mexican', 'Mexican'),
        ('Indian', 'Indian'),
        ('Japanese', 'Japanese'),
        # Add more categories as needed
    ]

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
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, blank=True, null=True)

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