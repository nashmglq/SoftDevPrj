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
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter recipe name', 'required': 'required'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file', 'required': 'required'}),
            'ingredients': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of ingredients', 'required': 'required'}),
            'minutes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preparation time in minutes', 'required': 'required'}),
            'calories': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Total calories', 'required': 'required'}),
            'directions': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Instructions', 'required': 'required'}),
            'ingredientsList': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ingredients in list format', 'required': 'required'}),
            'category': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        }