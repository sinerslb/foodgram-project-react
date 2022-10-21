from django.contrib.auth.models import AbstractUser
from django.db import models
from users.managers import CustomUserManager


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField('Электронная почта', unique=True)
    subscribe = models.ManyToManyField(
        'self',
        blank=True,
        verbose_name='Подписки',
        related_name='subscribers',
        symmetrical=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name
