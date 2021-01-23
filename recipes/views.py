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
from users.models import Subscription

User = get_user_model()

RECIPE_ON_PAGE = 6


def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author:
        return redirect("index")
    recipe.delete()
    return redirect("index")


def shopping_counter(user):
    if not user.is_authenticated:
        return 0, set()
    shopping = user.shopping_lists.all()
    shopping_recipes = set()
    for el in shopping:
        shopping_recipes.add(el.recipe.pk)
    return len(shopping), shopping_recipes


def get_favorite_recipes_id(request):
    if not request.user.is_authenticated:
        return set()
    favorite_recipes_id = set()
    favorites = request.user.favorites.all()
    for el in favorites:
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
            # "favorites": favorite_recipes_id,
            'ingredients': ingredients,
            'favorite': favorite,
            'follow': follow,
            # "paginator": paginator,
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
            # "recipe": recipe,
            # "favorites": favorite_recipes_id,
            # 'ingredients': ingredients,
            # 'favorite': favorite,
            # 'follow': follow,
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
            # "favorites": favorite_recipes_id,
            'shopping': True,
            #     "paginator": paginator,
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
            return redirect("recipe", recipe.pk)
        return render(
            request,
            "new.html",
            {
                "errors": form.errors,
                'new': True,
                'shopping_count': shopping_count
            }
        )
    # form = RecipeForm()
    return render(
        request,
        "new.html",
        {
            # "form": form,
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
            recipe_ingredient = RecipeIngredient.objects.create(
                ingredient=ingredient,
                count=el.get('value'),
                recipe=recipe
            )

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
            recipe.title = form.cleaned_data.get('title')
            recipe.description = form.cleaned_data.get('description')
            recipe.time = form.cleaned_data.get('time')
            if request.FILES.get('file'):
                recipe.image = request.FILES.get('file')
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
            recipe.author = request.user
            recipe.save()
            return redirect("recipe", recipe.pk)
        return render(request, "edit.html", {"errors": form.errors})
    form = RecipeForm()
    ingredients = recipe.recipe_ingredients.all()
    return render(
        request,
        "edit.html",
        {
            "form": form,
            'recipe': recipe,
            'ingredients': ingredients,
            'shopping_count': shopping_count,
        }
    )