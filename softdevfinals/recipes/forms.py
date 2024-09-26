from django import forms

class RatingCommentForm(forms.Form):
    score = forms.IntegerField(min_value=1, max_value=5) 
    content = forms.CharField(widget=forms.Textarea)