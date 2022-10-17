from django.urls import include, path
from rest_framework import routers
from api.views import (CustomUserViewSet, IngredientsViewSet, RecipesViewSet,
                       TagsViewSet)

app_name = 'api'

router = routers.DefaultRouter()

router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'users', CustomUserViewSet, 'users')
router.register(r'ingredients', IngredientsViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
