from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CustomLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Adding the email field

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')  # Include email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']  # Save email to the user object
        if commit:
            user.save()
        return user