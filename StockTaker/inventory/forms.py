from django import forms
from django.contrib.auth.models import User
from .models import Food, Recipe, StockFood, StockInstance


class StockFoodForm(forms.ModelForm):
    "form for crud of stockFood model"
    food_display = forms.CharField(label="Food", disabled=True, required=False)

    class Meta:
        model = StockFood
        fields = ['food', 'quantity', 'expiry_date']
        widgets = {
            'food': forms.Select(attrs={'class': 'form-select form-control'}),
        }


class FoodForm(forms.ModelForm):
    "form for crud of Food model"
    class Meta:
        model = Food
        fields = ['name', 'category', 'shelf_life']
        widgets = {
            'user': forms.HiddenInput(),
            'category': forms.SelectMultiple(attrs={'class': 'form-select form-control'}),
        }


class RecipeForm(forms.ModelForm):
    "form for crud of Recipe model"
    class Meta:
        model = Recipe
        fields = ['user', 'name', 'ingredients', 'category',
                  'portion_size', 'portion_quantity', 'instructions', 'image']
        widgets = {
            'ingredients': forms.SelectMultiple(attrs={'class': 'form-select form-control'}),
            'category': forms.SelectMultiple(attrs={'class': 'form-select form-control'}),
            'portion_size': forms.Select(attrs={'class': 'form-select form-control'}),
        }


class RecipePromptForm(forms.Form):
    """form for AI-generated recipe"""
    inventory = forms.ModelChoiceField(
        queryset=StockInstance.objects.none(),
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'recipe_inventory'})
    )
    help_text = None

    ingredients = forms.ModelMultipleChoiceField(
        queryset=Food.objects.all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'form-control', 'id': 'recipe_ingredients'})
    )
    help_text = None

    prompt = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )
