from django import forms

from recipes.models import Recipe, RecipeIngredient


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["count"]


class RecipeForm(forms.Form):
    class Meta:
        model = Recipe

    title = forms.CharField()
    description = forms.CharField()
    time = forms.IntegerField()
