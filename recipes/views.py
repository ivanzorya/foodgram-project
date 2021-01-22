from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404

from recipes.forms import RecipeForm
from recipes.models import Ingredient, Recipe, RecipeIngredient, Favorite, \
    ShoppingList
from users.models import Subscription


User = get_user_model()


def shopping_counter(user):
    shopping = user.shopping_lists.all()
    shopping_recipes = set()
    for el in shopping:
        shopping_recipes.add(el.recipe.pk)
    return len(shopping), shopping_recipes


def index(request):
    recipes = Recipe.objects.all()
    favorite_recipes_id = set()
    shopping_count, shopping_recipes = 0, set()
    if request.user.is_authenticated:
        favorites = request.user.favorites.all()
        for el in favorites:
            favorite_recipes_id.add(el.recipe.pk)
    # paginator = Paginator(post_list, 10)
    # page_number = request.GET.get("page")
    # page = paginator.get_page(page_number)
        shopping_count, shopping_recipes = shopping_counter(request.user)
    return render(
        request,
        "index.html",
        {
            "recipes": recipes,
            "favorites": favorite_recipes_id,
            'index': True,
            # "paginator": paginator,
            'shopping_count': shopping_count,
            'shopping_recipes': shopping_recipes,
        }
    )


def get_favorities(request):
    if not request.user.is_authenticated:
        return redirect("index")
    favorites = request.user.favorites.all()
    recipes = []
    for el in favorites:
        recipes.append(el.recipe)
    favorite_recipes_id = set()
    for el in favorites:
        favorite_recipes_id.add(el.recipe.pk)
    shopping_count, shopping_recipes = shopping_counter(request.user)
    return render(
        request,
        "favorite.html",
        {
            "recipes": recipes,
            "favorites": favorite_recipes_id,
            'favorite': True,
            #     "paginator": paginator,
            'shopping_count': shopping_count,
            'shopping_recipes': shopping_recipes,


        }
    )


def get_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    ingredients = recipe.recipe_ingredients.all()
    favorite = []
    follow = False
    shopping_count, shopping_recipes = 0, set()
    if request.user.is_authenticated:
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        is_follower = Subscription.objects.filter(user=request.user, author=recipe.author)
        if is_follower:
            follow = True
        shopping_count, shopping_recipes = shopping_counter(request.user)
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
    form = RecipeForm()
    return render(
        request,
        "new.html",
        {
            "form": form,
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


def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author:
        return redirect("index")
    recipe.delete()
    return redirect("index")


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
            #     "paginator": paginator,
            'shopping_count': shopping_count,
        }
    )


def get_author(request, user_id):
    author = get_object_or_404(User, pk=user_id)
    recipes = author.recipes.all()
    favorite_recipes_id = set()
    shopping_count, shopping_recipes = 0, set()
    if request.user.is_authenticated:
        favorites = request.user.favorites.all()
        for el in favorites:
            favorite_recipes_id.add(el.recipe.pk)
        shopping_count, shopping_recipes = shopping_counter(request.user)
    follow = False
    if request.user.is_authenticated:
        is_follower = request.user.subscriptions.filter(author=author)
        if is_follower:
            follow = True
    # paginator = Paginator(post_list, 10)
    # page_number = request.GET.get("page")
    # page = paginator.get_page(page_number)
    # add_ingredients()
    return render(
        request,
        "author.html",
        {
            "recipes": recipes,
            "favorites": favorite_recipes_id,
            'author': author,
            'follow': follow,
            #     "paginator": paginator,
            'shopping_count': shopping_count,
            'shopping_recipes': shopping_recipes,
        }
    )


def get_shopping_list(request):
    if not request.user.is_authenticated:
        return redirect("index")
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