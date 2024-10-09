from django import forms
from .models import Recipe
class RatingCommentForm(forms.Form):
    score = forms.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        min_value=1, 
        max_value=5,
        widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    content = forms.CharField(widget=forms.Textarea)

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'image', 'ingredients', 'minutes', 'calories', 'directions', 'ingredientsList', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter recipe name'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'ingredients' : forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of ingredients'})),
            'minutes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preparation time in minutes'}),
            'calories': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Total calories'}),
            'directions': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Instructions'}),
            'ingredientsList': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ingredients in list format'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }