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
