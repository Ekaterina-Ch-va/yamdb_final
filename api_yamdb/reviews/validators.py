import re

from rest_framework.validators import ValidationError
from reviews.models import User


def validate_username(data):
    data = data.lower()
    if User.objects.filter(username__iexact=data):
        raise ValidationError(
            'Пользователь с таким имененм уже существует.'
        )
    if data == 'me':
        raise ValidationError(
            'Имя пользователя нe недопустимо. Используйте другое.'
        )
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9@+-_]+$', data):
        raise ValidationError("Неверный формат имени.")


def validate_email(data):
    if User.objects.filter(email__iexact=data):
        raise ValidationError(
            'Такой email уже существует.'
        )
