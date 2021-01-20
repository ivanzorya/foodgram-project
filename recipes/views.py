from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView

from recipes.forms import RecipeForm
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient


def index(request):
    # post_list = Post.objects.all()
    # paginator = Paginator(post_list, 10)
    # page_number = request.GET.get("page")
    # page = paginator.get_page(page_number)
    # add_ingredients()
    return render(
        request,
        "index.html",
        # {
        #     "page": page,
        #     "paginator": paginator
        # }
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
        marker = 0
        index = 1
        while marker < 10:
            name = request.POST.get('nameIngredient_' + str(index))
            if name:
                value = request.POST.get('valueIngredient_' + str(index))
                ingredients.append(
                    {
                        'name': name,
                        'value': int(value)
                    }
                )
            else:
                marker += 1
            index += 1
        recipe_ingredients = []
        for el in ingredients:
            ingredient = get_object_or_404(Ingredient, title=el.get('name'))
            recipe_ingredient = RecipeIngredient.objects.create(
                ingredient=ingredient,
                count=el.get('value')
            )
            recipe_ingredients.append(recipe_ingredient)

        data = {}
        data['title'] = request.POST.getlist('name')[0]
        data['time'] = request.POST.getlist('name')[1]
        data['description'] = request.POST.getlist('description')[0]
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
            # for tag in tags:
            #     # Tag.objects.create(title=tag)
            #     tag = get_object_or_404(Tag, title=tag)
            #     recipe.tag.add(tag)
            recipe.author = request.user
            recipe.save()
            for el in recipe_ingredients:
                el.recipe = recipe
                el.save()
            return redirect("index")
        else:
            print(form.errors)
        return render(request, "new.html", {"errors": form.errors})
    form = RecipeForm()
    return render(request, "new.html", {"form": form})
