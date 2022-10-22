from datetime import datetime as dt

from django.contrib.auth import get_user_model
from django.db.models import F, Sum, Case, When, Value, IntegerField
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from api.filters import RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAdminOrAuthorOrReadOnly, AdminOrReadOnly
from api.serializers import (CustomUserSerializer, IngredientsSerializer,
                             RecipesSerializer, RecipesShortSerializer,
                             SubscribeSerializer, TagsSerializer)
from recipes.models import Ingredient, IngredientsInRecipe, Recipe, Tag

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет модели пользователя."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        methods=['get', ],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        """Список подписок на авторов."""

        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        authors = user.subscribe.all()
        pages = self.paginate_queryset(authors)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        """Подписка/отписка на/от авторов."""

        user = self.request.user
        author = get_object_or_404(User, id=kwargs.get('id'))
        if request.method == 'POST':
            if user.subscribe.filter(id=author.id).exists():
                return Response(
                    {'errors': 'Подписка на этого пользователя уже есть!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user.id == author.id:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribeSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            user.subscribe.add(author)
            response_status = status.HTTP_201_CREATED
            data = serializer.data
        elif request.method == 'DELETE':
            if not user.subscribe.filter(id=author.id).exists():
                return Response(
                    {'errors': 'Подписка на этого пользователя нет!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.subscribe.remove(author)
            response_status = status.HTTP_204_NO_CONTENT
            data = None
        return Response(data=data, status=response_status)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [AdminOrReadOnly, ]


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AdminOrReadOnly,)

    def get_queryset(self):
        """
        Фильтрация и сортировка ингредиентов по параметру запроса 'name'.
        В начале выводятся ингредиенты начинающиеся на 'name', затем остальные.
        """
        name = self.request.query_params.get('name')
        queryset = self.queryset
        if name:
            queryset = queryset.filter(name__icontains=name)
            queryset = queryset.annotate(
                ingr_order=Case(
                    When(name=name, then=Value(1)),
                    default=2,
                    output_field=IntegerField(),
                )
            ).order_by('ingr_order')
        return queryset


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthorOrReadOnly, )
    serializer_class = RecipesSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        """Создание рецепта."""

        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Работа со списком избранного."""

        return self.add_del(
            method=request.method,
            model_field='favorite',
            pk=pk
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Работа со списком покупок."""

        return self.add_del(
            method=request.method,
            model_field='cart',
            pk=pk
        )

    def add_del(self, method, model_field, pk):
        """
        Добавляет или удаляет переданный объект в список избранного,
        либо в список покупок.
        """

        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_fields = {
            'cart': recipe.cart,
            'favorite': recipe.favorite,
        }
        m_field = model_fields[model_field]

        if method == 'POST':
            if m_field.filter(id=user.id).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipesShortSerializer(recipe)
            m_field.add(user)
            response_status = status.HTTP_201_CREATED
            data = serializer.data
        elif method == 'DELETE':
            if not m_field.filter(id=user.id).exists():
                return Response(
                    {'errors': 'Рецепт уже удалён!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            m_field.remove(user)
            response_status = status.HTTP_204_NO_CONTENT
            data = None
        return Response(data=data, status=response_status)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивание файла со списком покупок."""

        user = request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientsInRecipe.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount'))

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n'
            f'Дата: {dt.today():%d-%m-%Y}\n\n'
        )
        for ing in ingredients:
            shopping_list += (
                f'{ing["ingredient"]}: {ing["amount"]} {ing["measure"]}\n'
            )
        shopping_list += '\nПриятного аппетита!'

        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


@receiver(pre_delete, sender=Recipe)
def recipe_image_delete(sender, instance, **kwargs):
    """Удаляет файл картинки, при удалении рецепта."""

    instance.image.delete(False)
