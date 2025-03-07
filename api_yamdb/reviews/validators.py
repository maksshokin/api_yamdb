import datetime
import re

from django.core.exceptions import ValidationError

from api.v1.constants import RESERVED_USERNAME, USERNAME_REGEX


class ValidateUsername:
    def __call__(self, username):
        validate_username(username)


def validate_username(username):
    if not re.fullmatch(USERNAME_REGEX, username):
        raise ValidationError(
            'Имя пользователя содержит недопустимые символы.'
        )
    if username == RESERVED_USERNAME:
        raise ValidationError(
            f'Нельзя использовать "{RESERVED_USERNAME}".'
        )


def validate_year(value):
    current_year = datetime.date.today().year
    if value > current_year:
        raise ValidationError('Год не может быть больше текущего.')
