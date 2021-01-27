from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Favorite, ShoppingList
from recipes.serializers import IngredientSerializer
from users.models import Subscription

User = get_user_model()


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_ingredient(request):
    response = Ingredient.objects.filter(
        title__icontains=request.GET.get('query')
    )
    serializer = IngredientSerializer(data=response, many=True)
    serializer.is_valid()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_favorite(request):
    recipe = get_object_or_404(Recipe, pk=request.data.get('id'))
    obj, created = Favorite.objects.get_or_create(
        user=request.user,
        recipe=recipe
    )
    return Response({}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def delete_favorite(request, recipe_id):
    favorites = Favorite.objects.filter(
        user=request.user,
        recipe__id=recipe_id
    )
    for el in favorites:
        el.delete()
    return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_subscription(request):
    author = get_object_or_404(User, pk=request.data.get('id'))
    obj, created = Subscription.objects.get_or_create(
        user=request.user,
        author=author
    )
    return Response({}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def delete_subscription(request, user_id):
    subscriptions = Subscription.objects.filter(
        user=request.user,
        author__id=user_id
    )
    for el in subscriptions:
        el.delete()
    return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_purchase(request):
    recipe = get_object_or_404(Recipe, pk=request.data.get('id'))
    obj, created = ShoppingList.objects.get_or_create(
        user=request.user,
        recipe=recipe
    )
    return Response({}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def delete_purchase(request, recipe_id):
    shopping_list = ShoppingList.objects.filter(
        user=request.user,
        recipe__id=recipe_id
    )
    for el in shopping_list:
        el.delete()
    return Response({}, status=status.HTTP_200_OK)
