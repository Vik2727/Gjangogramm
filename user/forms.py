from django import forms
from main.models import UserProfile, Post


class UserProfileForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'bio', 'avatar']


class PostForm(forms.ModelForm):
    caption = forms.CharField(widget=forms.Textarea(attrs={'rows': 1}), required=False)

    class Meta:
        model = Post
        fields = ['caption']
