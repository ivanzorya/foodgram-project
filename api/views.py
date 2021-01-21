from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Favorite
from recipes.serializers import IngredientSerializer


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
def add_favorite(request):
    favorite = Favorite.objects.filter(
        user=request.user,
        recipe__id=request.data.get('id')
    )
    if not favorite:
        recipe = get_object_or_404(Recipe, pk=request.data.get('id'))
        Favorite.objects.create(user=request.user, recipe=recipe)
    return Response({}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def delete_favorite(request, recipe_id):
    favorites = Favorite.objects.filter(
        user=request.user,
        recipe__id=recipe_id
    )
    for el in favorites:
        el.delete()
    return Response({}, status=status.HTTP_200_OK)
