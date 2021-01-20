from django import forms

from recipes.models import Recipe, RecipeIngredient


# class RecipeForm(forms.ModelForm):
#     class Meta:
#         model = Recipe
#         fields = '__all__'
#         # fields = ["title", "description", 'tag', 'time', "image"]


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["count"]


class RecipeForm(forms.Form):
    class Meta:
        model = Recipe

    title = forms.CharField(required=False)
    # breakfast = forms.BooleanField(required=False)
    # lunch = forms.BooleanField(required=False)
    # dinner = forms.BooleanField(required=False)
    description = forms.CharField(required=False)
    time = forms.IntegerField(required=False)
    # image = forms.ImageField(required=False)
