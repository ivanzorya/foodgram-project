from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from recipes.models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


@api_view(['get'])
@permission_classes((AllowAny,))
def get_ingredient(request):
    response = Ingredient.objects.filter(title__icontains=request.GET.get('query'))
    serializer = IngredientSerializer(data=response, many=True)
    serializer.is_valid()
    return Response(serializer.data, status=status.HTTP_200_OK)
