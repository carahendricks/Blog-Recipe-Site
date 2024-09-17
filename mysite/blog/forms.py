from django import forms
from .models import Comment, RecipeComment, Recipe

# Existing form for sharing a post via email
class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


# Existing form for submitting comments on blog posts
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']


# New form for submitting comments on recipes
class RecipeCommentForm(forms.ModelForm):
    class Meta:
        model = RecipeComment
        fields = ['name', 'email', 'body']


# Search form for blog posts or recipes
class SearchForm(forms.Form):
    query = forms.CharField()


# New form for submitting recipe ratings
class RatingForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': '0', 'max': '5', 'step': '0.1'})
        }
        labels = {
            'rating': 'Rate this recipe (0.0 - 5.0)',
        }