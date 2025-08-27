from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class CreateUserForm(UserCreationForm):
    """form to instantiate a user model"""

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None


class UserForm(forms.ModelForm):
    """form to update a user model"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileForm(forms.ModelForm):
    """form to update a profile model"""
    class Meta:
        model = Profile
        fields = ['image']
        labels = {
            "image": "Image url"
        }
