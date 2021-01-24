import mimetypes
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from recipes.forms import RecipeForm
from recipes.models import (
    Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingList
)
from recipes.utils import (
    get_data_tags, update_tags, shopping_counter, make_shopping_list,
    get_favorite_recipes_id, check_tags
)
from users.models import Subscription

User = get_user_model()

RECIPE_ON_PAGE = 6


def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author:
        return redirect("index")
    recipe.delete()
    return redirect("index")


def index(request):
    recipes, tag, tags = check_tags(
        Recipe.objects.all(),
        request.GET.get("tag")
    )
    favorite_recipes_id = get_favorite_recipes_id(request)
    shopping_count, shopping_recipes = shopping_counter(request.user)
    paginator = Paginator(recipes, RECIPE_ON_PAGE)
    page_number = request.GET.get("page")
    recipes = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {
            "recipes": recipes,
            "favorites": favorite_recipes_id,
            'index': True,
            "paginator": paginator,
            'shopping_count': shopping_count,
            'shopping_recipes': shopping_recipes,
            'tags': tags,
            'tag': tag
        }
    )


def get_favorities(request):
    if not request.user.is_authenticated:
        return redirect("index")
    favorites = request.user.favorites.all()
    recipes = []
    for el in favorites:
        recipes.append(el.recipe.pk)
    recipes, tag, tags = check_tags(
        Recipe.objects.filter(pk__in=recipes),
        request.GET.get("tag")
    )
    favorite_recipes_id = get_favorite_recipes_id(request)
    shopping_count, shopping_recipes = shopping_counter(request.user)
    paginator = Paginator(recipes, RECIPE_ON_PAGE)
    page_number = request.GET.get("page")
    recipes = paginator.get_page(page_number)
    return render(
        request,
        "favorite.html",
        {
            "recipes": recipes,
            "favorites": favorite_recipes_id,
            'favorite': True,
            "paginator": paginator,
            'shopping_count': shopping_count,
            'shopping_recipes': shopping_recipes,
            'tags': tags,
            'tag': tag,

        }
    )


def get_author(request, user_id):
    author = get_object_or_404(User, pk=user_id)
    recipes, tag, tags = check_tags(
        author.recipes.all(),
        request.GET.get("tag")
    )
    favorite_recipes_id = get_favorite_recipes_id(request)
    shopping_count, shopping_recipes = shopping_counter(request.user)
    follow = False
    if request.user.is_authenticated:
        is_follower = request.user.subscriptions.filter(author=author)
        if is_follower:
            follow = True
    paginator = Paginator(recipes, RECIPE_ON_PAGE)
    page_number = request.GET.get("page")
    recipes = paginator.get_page(page_number)
    return render(
        request,
        "author.html",
        {
            "recipes": recipes,
            "favorites": favorite_recipes_id,
            'author': author,
            'follow': follow,
            "paginator": paginator,
            'shopping_count': shopping_count,
            'shopping_recipes': shopping_recipes,
            'tag': tag,
            'tags': tags,
        }
    )


def get_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    ingredients = recipe.recipe_ingredients.all()
    favorite = []
    follow = False
    shopping_count, shopping_recipes = shopping_counter(request.user)
    if request.user.is_authenticated:
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        is_follower = Subscription.objects.filter(
            user=request.user,
            author=recipe.author
        )
        if is_follower:
            follow = True
    return render(
        request,
        "recipe.html",
        {
            "recipe": recipe,
            'ingredients': ingredients,
            'favorite': favorite,
            'follow': follow,
            'shopping_count': shopping_count,
            'shopping_recipes': shopping_recipes,
        }
    )


def get_follows(request):
    if not request.user.is_authenticated:
        return redirect("index")
    shopping_count, _ = shopping_counter(request.user)
    follows = request.user.subscriptions.all()
    data = []
    for follow in follows:
        recipes = follow.author.recipes.all()
        temp_data = {
            'author': follow.author,
            'recipes': recipes[:3],
            'count': len(recipes) - 3
        }
        data.append(temp_data)
    paginator = Paginator(data, RECIPE_ON_PAGE)
    page_number = request.GET.get("page")
    data = paginator.get_page(page_number)
    return render(
        request,
        "follow.html",
        {
            'follows': follows,
            'subscription': True,
            'data': data,
            "paginator": paginator,
            'shopping_count': shopping_count,
        }
    )


def get_shopping_list(request):
    if not request.user.is_authenticated:
        return redirect("index")
    make_shopping_list(request)
    shopping_count, _ = shopping_counter(request.user)
    shopping_lists = request.user.shopping_lists.all()
    recipes = []
    for el in shopping_lists:
        recipes.append(el.recipe)
    return render(
        request,
        "shopping.html",
        {
            "recipes": recipes,
            'shopping': True,
            'shopping_count': shopping_count
        }
    )


def delete_shopping_list(request, recipe_id):
    if not request.user.is_authenticated:
        return redirect("index")
    shopping_list = ShoppingList.objects.filter(
        user=request.user,
        recipe__id=recipe_id
    )
    for el in shopping_list:
        el.delete()
    return redirect("shopping")


def get_txt(request):
    if not request.user.is_authenticated:
        return redirect("index")
    data = make_shopping_list(request)
    date = datetime.now().date()
    f = open('shopping_list.txt', 'w', encoding='utf-8')
    f.write(
        '\n'
        f'Список покупок {request.user.username}. Дата {date}.\n\n'
        '\n'
    )
    i = 1
    for item in data:
        if i < 10:
            j = ' '
        else:
            j = ''
        f.write(
            f'{j}{i}. [ ]  {item} {data.get(item)[0]} {data.get(item)[1]}.\n\n'
        )
        i += 1

    f.close()
    fl_path = 'shopping_list.txt'
    filename = f'shopping_list_{request.user.username}_{date}.txt'

    fl = open(fl_path, 'r')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = f"attachment; filename={filename}"
    return response


def new(request):
    if not request.user.is_authenticated:
        return redirect("index")
    shopping_count, _ = shopping_counter(request.user)
    if request.method == "POST":
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
        data, tags = get_data_tags(request)
        for key in data:
            fields[key] = data[key]

        form = RecipeForm(data=data)
        image = request.FILES.get('file')
        if not image or 'image' not in image.content_type:
            errors['image'] = True
        else:
            errors['image'] = False
        if form.is_valid() and not errors['image'] and recipe_ingredients:
            recipe = Recipe.objects.create(
                title=form.cleaned_data.get('title'),
                description=form.cleaned_data.get('description'),
                time=form.cleaned_data.get('time')
            )
            recipe.image = request.FILES.get('file')
            recipe = update_tags(tags, recipe)
            recipe.author = request.user
            recipe.save()
            for el in recipe_ingredients:
                el.recipe = recipe
                el.save()
            return redirect("recipe", recipe.pk)
        for error in form.errors:
            errors[error] = True
        return render(
            request,
            "new.html",
            {
                "errors": errors,
                'new': True,
                'shopping_count': shopping_count,
                'fields': fields
            }
        )
    return render(
        request,
        "new.html",
        {
            'new': True,
            'shopping_count': shopping_count,
        }
    )


def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author:
        return redirect("index")
    shopping_count, _ = shopping_counter(request.user)
    if request.method == "POST":
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
        data, tags = get_data_tags(request)
        form = RecipeForm(data=data)
        image = request.FILES.get('file')
        if image and 'image' not in image.content_type:
            errors['image'] = True
        else:
            errors['image'] = False
        if form.is_valid() and old_recipe_ingredients and not errors['image']:
            recipe.title = form.cleaned_data.get('title')
            recipe.description = form.cleaned_data.get('description')
            recipe.time = form.cleaned_data.get('time')
            recipe = update_tags(tags, recipe)
            recipe.author = request.user
            recipe.save()
            return redirect("recipe", recipe.pk)
        for error in form.errors:
            errors[error] = True
        ingredients = recipe.recipe_ingredients.all()
        return render(
            request,
            "edit.html",
            {
                'recipe': recipe,
                'ingredients': ingredients,
                "errors": errors,
                'shopping_count': shopping_count,
            }
        )
    ingredients = recipe.recipe_ingredients.all()
    return render(
        request,
        "edit.html",
        {
            'recipe': recipe,
            'ingredients': ingredients,
            'shopping_count': shopping_count,
        }
    )