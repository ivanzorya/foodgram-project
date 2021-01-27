import mimetypes
from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

from recipes.forms import RecipeForm
from recipes.models import (
    Recipe, Favorite, ShoppingList
)
from recipes.utils import (
    get_data_tags, shopping_counter, make_shopping_list,
    get_favorite_recipes_id, check_tags, make_ingredients, save_recipe,
    update_recipe, update_ingredients
)
from users.models import Subscription

User = get_user_model()

RECIPE_ON_PAGE = 6


def delete_recipe(request, recipe_id):
    """Удаление рецепта автором."""
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author:
        return redirect('index')
    recipe.delete()
    return redirect('index')


class RecipeListView(ListView):
    """Просмотр всех рецептов."""
    model = Recipe
    template_name = 'index.html'
    paginate_by = 6
    context_object_name = 'recipes'

    def get_queryset(self):
        recipes, _, _ = check_tags(
            Recipe.objects.all(),
            self.request.GET.get('tag')
        )
        return recipes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favorites'] = get_favorite_recipes_id(self.request)
        context['shopping_recipes'] = shopping_counter(self.request.user)
        context['index'] = True
        _, context['tag'], context['tags'] = check_tags(
            Recipe.objects.all(),
            self.request.GET.get('tag')
        )
        return context


class FavoriteListView(LoginRequiredMixin, ListView):
    """Просмотр избранных рецептов."""
    model = Recipe
    template_name = 'favorite.html'
    paginate_by = 6
    context_object_name = 'recipes'


    def filter_recipes(self):
        favorites = self.request.user.favorites.all()
        recipes = []
        for el in favorites:
            if el.recipe:
                recipes.append(el.recipe.pk)
        return recipes

    def get_queryset(self):
        recipes, _, _ = check_tags(
            Recipe.objects.filter(pk__in=self.filter_recipes()),
            self.request.GET.get('tag')
        )
        return recipes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favorites'] = get_favorite_recipes_id(self.request)
        context['shopping_recipes'] = shopping_counter(self.request.user)
        context['favorite'] = True
        _, context['tag'], context['tags'] = check_tags(
            Recipe.objects.filter(pk__in=self.filter_recipes()),
            self.request.GET.get('tag')
        )
        return context


def get_author(request, user_id):
    """Просмотр рецептов автора."""
    author = get_object_or_404(User, pk=user_id)
    recipes, tag, tags = check_tags(
        author.recipes.all(),
        request.GET.get('tag')
    )
    favorite_recipes_id = get_favorite_recipes_id(request)
    shopping_recipes = shopping_counter(request.user)
    follow = False
    if request.user.is_authenticated:
        is_follower = request.user.subscriptions.filter(author=author)
        if is_follower:
            follow = True
    paginator = Paginator(recipes, RECIPE_ON_PAGE)
    page_number = request.GET.get('page')
    recipes = paginator.get_page(page_number)
    return render(
        request,
        'author.html',
        {
            'recipes': recipes,
            'favorites': favorite_recipes_id,
            'author': author,
            'follow': follow,
            'paginator': paginator,
            'shopping_recipes': shopping_recipes,
            'tag': tag,
            'tags': tags,
        }
    )


def get_recipe(request, recipe_id):
    """Просмотр рецепта."""
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    ingredients = recipe.recipe_ingredients.all()
    favorite = []
    follow = False
    shopping_recipes = shopping_counter(request.user)
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
        'recipe.html',
        {
            'recipe': recipe,
            'ingredients': ingredients,
            'favorite': favorite,
            'follow': follow,
            'shopping_recipes': shopping_recipes,
        }
    )


def get_follows(request):
    """Просмотр страницы подписок на авторов."""
    if not request.user.is_authenticated:
        return redirect('index')
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
    page_number = request.GET.get('page')
    data = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {
            'follows': follows,
            'subscription': True,
            'data': data,
            'paginator': paginator
        }
    )


def get_shopping_list(request):
    """Просмотр листа покупок."""
    if not request.user.is_authenticated:
        return redirect('index')
    return render(
        request,
        'shopping.html',
        {
            'shopping': True
        }
    )


def delete_shopping_list(request, recipe_id):
    """Удаление рецепта из листа покупок."""
    if not request.user.is_authenticated:
        return redirect('index')
    shopping_list = ShoppingList.objects.filter(
        user=request.user,
        recipe__id=recipe_id
    )
    for el in shopping_list:
        el.delete()
    return redirect('shopping')


def get_txt(request):
    """Загрузка .txt файла со списком покупок."""
    if not request.user.is_authenticated:
        return redirect('index')
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
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def new_recipe(request):
    """Создание нового рецепта."""
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        errors, fields, ingredients = make_ingredients(request)
        data, tags = get_data_tags(request)
        for key in data:
            fields[key] = data[key]
        form = RecipeForm(data=data)
        image = request.FILES.get('file')
        if not image or 'image' not in image.content_type:
            errors['image'] = True
        else:
            errors['image'] = False
        if form.is_valid() and not errors['image'] and ingredients:
            pk = save_recipe(form.cleaned_data, request, ingredients, tags)
            return redirect('recipe', pk)
        for error in form.errors:
            errors[error] = True
        return render(
            request,
            'new.html',
            {
                'errors': errors,
                'new': True,
                'fields': fields
            }
        )
    return render(
        request,
        'new.html',
        {
            'new': True,
        }
    )


def edit_recipe(request, recipe_id):
    """Редактирование рецепта."""
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author:
        return redirect('index')
    if request.method == 'POST':
        errors, old_recipe_ingredients = update_ingredients(recipe, request)
        data, tags = get_data_tags(request)
        form = RecipeForm(data=data)
        image = request.FILES.get('file')
        if image and 'image' not in image.content_type:
            errors['image'] = True
        else:
            errors['image'] = False
        if form.is_valid() and old_recipe_ingredients and not errors['image']:
            update_recipe(recipe, form.cleaned_data, tags, request, image)
            return redirect('recipe', recipe.pk)
        for error in form.errors:
            errors[error] = True
        ingredients = recipe.recipe_ingredients.all()
        return render(
            request,
            'edit.html',
            {
                'recipe': recipe,
                'ingredients': ingredients,
                'errors': errors,
            }
        )
    ingredients = recipe.recipe_ingredients.all()
    return render(
        request,
        'edit.html',
        {
            'recipe': recipe,
            'ingredients': ingredients,
        }
    )
