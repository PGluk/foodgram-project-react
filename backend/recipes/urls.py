from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FavoriteViewSet,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    TagViewSet,
    download_shopping_cart,
    ListFollowViewSet,
    FollowViewSet
)

router = DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('users/subscriptions/',
         ListFollowViewSet.as_view(), name='subscriptions'),
    path('users/<int:author_id>/subscribe/',
         FollowViewSet.as_view(), name='subscribe'),
    path('recipes/download_shopping_cart/',
         download_shopping_cart,
         name='download'),
    path('recipes/<int:recipe_id>/favorite/',
         FavoriteViewSet.as_view(), name='favorite'),
    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppingCartViewSet.as_view(), name='shopping_cart'),
]
