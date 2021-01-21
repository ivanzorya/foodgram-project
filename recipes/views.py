from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView

from recipes.forms import RecipeForm
from recipes.models import Ingredient, Recipe, RecipeIngredient, Favorite


def index(request):
    recipes = Recipe.objects.all()
    favorite_recipes_id = set()
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user)
        for el in favorites:
            favorite_recipes_id.add(el.recipe.pk)
    # paginator = Paginator(post_list, 10)
    # page_number = request.GET.get("page")
    # page = paginator.get_page(page_number)
    # add_ingredients()
    return render(
        request,
        "index.html",
        {
            "recipes": recipes,
            "favorites": favorite_recipes_id,
        #     "paginator": paginator
        }
    )

def get_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    ingredients = recipe.recipe_ingredients.all()
    return render(
        request,
        "recipe.html",
        {
            "recipe": recipe,
            # "favorites": favorite_recipes_id,
            'ingredients': ingredients,
            #     "paginator": paginator
        }
    )

class RecipeListView(ListView):
    model = Recipe
    template_name = 'index.html'


class CreateRecipeView(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'formRecipe.html'


def new(request):
    if request.method == "POST":
        ingredients = []
        for key in request.POST:
            if 'nameIngredient' in key:
                name = request.POST.get(key)
                value = request.POST.get('valueIngredient_' + key[15:])
                ingredients.append(
                    {
                        'name': name,
                        'value': int(value)
                    }
                )
        recipe_ingredients = []
        for el in ingredients:
            ingredient = get_object_or_404(Ingredient, title=el.get('name'))
            recipe_ingredient = RecipeIngredient.objects.create(
                ingredient=ingredient,
                count=el.get('value')
            )
            recipe_ingredients.append(recipe_ingredient)

        data = {
            'title': request.POST.getlist('name')[0],
            'time': request.POST.getlist('name')[1],
            'description': request.POST.getlist('description')[0]
        }
        # data['image'] = request.FILES.get('file')
        tags = {
            'breakfast': False,
            'lunch': False,
            'dinner': False
                }
        for eat in ['breakfast', 'lunch', 'dinner']:
            if request.POST.getlist(eat):
                tags[eat] = True

        form = RecipeForm(data=data)

        if form.is_valid():

            recipe = Recipe.objects.create(
                    title=form.cleaned_data.get('title'),
                    description=form.cleaned_data.get('description'),
                    time=form.cleaned_data.get('time')
                )
            recipe.image = request.FILES.get('file')
            if tags['breakfast']:
                recipe.is_breakfast = True
            if tags['dinner']:
                recipe.is_dinner = True
            if tags['lunch']:
                recipe.is_lunch = True
            recipe.author = request.user
            recipe.save()
            for el in recipe_ingredients:
                el.recipe = recipe
                el.save()
            return redirect("index")
        return render(request, "new.html", {"errors": form.errors})
    form = RecipeForm()
    return render(request, "new.html", {"form": form})


def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author:
        return redirect("index")

    return None