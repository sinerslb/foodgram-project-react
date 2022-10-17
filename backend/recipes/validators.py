from django.core.exceptions import ValidationError


def validate_min_amount(value):
    """Проверка - количество ингридиентов должно быть положительным числом."""
    if value <= 0:
        raise ValidationError(
            'Количество ингридиентов должно быть больше нуля!'
        )
