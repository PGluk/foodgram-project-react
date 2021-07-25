import datetime

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import viewsets, mixins, status, generics
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter, IngredientFilter
from .models import (Tag,
                     Ingredient,
                     Recipe,
                     Favorite,
                     ShoppingCart,
                     RecipeIngredients,
                     Follow
                     )
from .permissions import AdminOrAuthorOrReadOnly
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          ShowRecipeSerializer,
                          CreateRecipeSerializer,
                          FavoriteSerializer,
                          ShoppingCartSerializer,
                          ShowFollowSerializer,
                          FollowSerializer
                          )

User = get_user_model()


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AdminOrAuthorOrReadOnly, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ShowRecipeSerializer
        else:
            return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class FavoriteViewSet(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, recipe_id):
        user = request.user
        data = {
            "user": user.id,
            "recipe": recipe_id,
        }
        if Favorite.objects.filter(user=user, recipe__id=recipe_id).exists():
            return Response(
                {"message": "Рецепт уже добавлен в избранное"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FavoriteSerializer(
            data=data,
            context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)

        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        Favorite.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, recipe_id):
        data = {"user": request.user, "recipe": recipe_id}

        shopping_cart_exist = ShoppingCart.objects.filter(
            user=request.user,
            recipe__id=recipe_id).exists()
        if shopping_cart_exist:
            return Response({"message": "Уже в корзине"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = ShoppingCartSerializer(data=data,
                                            context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):

        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.get(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def download_shopping_cart(request):
    user = request.user
    shopping_cart = user.shopping_cart.all()
    buying_list = {}
    for record in shopping_cart:
        recipe = record.recipe
        ingredients = RecipeIngredients.objects.filter(recipe=recipe)
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name not in buying_list:
                buying_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                buying_list[name]['amount'] = (buying_list[name]['amount']
                                               + amount)
    file_name = 'buying_list'
    now = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = (f'attachment;'
                                  f' filename="{file_name}_{now}.pdf"')
    p = canvas.Canvas(response)
    p.setFont('DejaVuSerif', 15)
    height = 800
    for name, data in buying_list.items():
        p.drawString(
            50,
            height,
            f"{name} ({data['measurement_unit']}) - {data['amount']}"
        )
        height -= 25
    p.showPage()
    p.save()
    return response


class ListFollowViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = ShowFollowSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class FollowViewSet(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, author_id):
        user = request.user
        follow_exist = Follow.objects.filter(user=user,
                                             author__id=author_id).exists()
        if user.id == author_id or follow_exist:
            return Response(
                {"message": "Невозможно подписаться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST)

        data = {
            'user': user.id,
            'author': author_id
        }

        serializer = FollowSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        record = get_object_or_404(Follow, user=request.user, author=author)
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
