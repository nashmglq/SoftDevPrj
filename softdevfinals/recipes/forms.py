from django import forms

class RatingCommentForm(forms.Form):
    score = forms.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        min_value=1, 
        max_value=5,
        widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    content = forms.CharField(widget=forms.Textarea)