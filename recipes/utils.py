from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, RecipeIngredient, Recipe


def shopping_counter(user):
    if not user.is_authenticated:
        return set()
    shopping = user.shopping_lists.all()
    shopping_recipes = set()
    for el in shopping:
        shopping_recipes.add(el.recipe.pk)
    return shopping_recipes


def get_favorite_recipes_id(request):
    if not request.user.is_authenticated:
        return set()
    favorite_recipes_id = set()
    favorites = request.user.favorites.all()
    for el in favorites:
        if el.recipe:
            favorite_recipes_id.add(el.recipe.pk)
    return favorite_recipes_id


def check_tags(queryset, tag):
    tags = {
        'breakfast': False,
        'lunch': False,
        'dinner': False
    }
    if not tag:
        return queryset, None, tags
    tags[tag] = True
    if tag == 'breakfast':
        queryset = queryset.filter(is_breakfast=True)
    if tag == 'dinner':
        queryset = queryset.filter(is_dinner=True)
    if tag == 'lunch':
        queryset = queryset.filter(is_lunch=True)
    return queryset, tag, tags


def make_shopping_list(request):
    shopping = request.user.shopping_lists.all()
    recipes = []
    for el in shopping:
        recipes.append(el.recipe)
    recipes_ingredients = []
    for el in recipes:
        recipes_ingredients += el.recipe_ingredients.all()
    data = {}
    for el in recipes_ingredients:
        if el.ingredient.title in data:
            data[el.ingredient.title][0] += el.count

        else:
            data[el.ingredient.title] = [el.count, el.ingredient.dimension]
    return data


def get_data_tags(request):
    data = {
        'title': request.POST.getlist('name')[0],
        'time': request.POST.getlist('name')[1],
        'description': request.POST.getlist('description')[0]
    }
    tags = {
        'breakfast': False,
        'lunch': False,
        'dinner': False
    }
    for eat in ['breakfast', 'lunch', 'dinner']:
        if request.POST.getlist(eat):
            tags[eat] = True
    return data, tags


def update_tags(tags, recipe):
    if tags['breakfast']:
        recipe.is_breakfast = True
    else:
        recipe.is_breakfast = False
    if tags['dinner']:
        recipe.is_dinner = True
    else:
        recipe.is_dinner = False
    if tags['lunch']:
        recipe.is_lunch = True
    else:
        recipe.is_lunch = False
    return recipe


def make_ingredients(request):
    errors = {}
    fields = {'ingredients': []}
    ingredients = []
    for key in request.POST:
        if 'nameIngredient' in key:
            name = request.POST.get(key)
            ing_to_back = {'pk': key[15:], 'name': name}
            value = request.POST.get('valueIngredient_' + key[15:])
            ing_to_back['value'] = value
            ing_to_back['units'] = request.POST.get('unitsIngredient_' + key[15:])
            ingredients.append(
                {
                    'name': name,
                    'value': int(value)
                }
            )
            fields['ingredients'].append(ing_to_back)
    recipe_ingredients = []
    for el in ingredients:
        ingredient = get_object_or_404(Ingredient, title=el.get('name'))
        recipe_ingredient = RecipeIngredient.objects.create(
            ingredient=ingredient,
            count=el.get('value')
        )
        recipe_ingredients.append(recipe_ingredient)
    if not recipe_ingredients:
        errors['ingredient'] = True
    return errors, fields, recipe_ingredients


def save_recipe(cleaned_data, request, recipe_ingredients, tags):
    recipe = Recipe.objects.create(
        title=cleaned_data.get('title'),
        description=cleaned_data.get('description'),
        time=cleaned_data.get('time')
    )
    recipe.image = request.FILES.get('file')
    recipe = update_tags(tags, recipe)
    recipe.author = request.user
    recipe.save()
    for el in recipe_ingredients:
        el.recipe = recipe
        el.save()
    return recipe.pk


def update_ingredients(recipe, request):
    errors = {}
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
    old_recipe_ingredients = recipe.recipe_ingredients.all()
    for el in old_recipe_ingredients:
        el.delete()
    for el in ingredients:
        ingredient = get_object_or_404(Ingredient, title=el.get('name'))
        RecipeIngredient.objects.create(
            ingredient=ingredient,
            count=el.get('value'),
            recipe=recipe
        )
    old_recipe_ingredients = recipe.recipe_ingredients.all()
    if not old_recipe_ingredients:
        errors['ingredient'] = True
    return errors, old_recipe_ingredients


def update_recipe(recipe, cleaned_data, tags, request, image):
    recipe.title = cleaned_data.get('title')
    recipe.description = cleaned_data.get('description')
    recipe.time = cleaned_data.get('time')
    recipe = update_tags(tags, recipe)
    recipe.author = request.user
    if image:
        recipe.image = request.FILES.get('file')
    recipe.save()
    return
