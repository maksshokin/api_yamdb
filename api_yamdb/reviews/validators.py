import re
import datetime

from django.core.exceptions import ValidationError
from api.v1.constants import (
    USERNAME_REGEX, RESERVED_USERNAME
)


class ValidateUsername:
    def __call__(self, username):
        if username == RESERVED_USERNAME:
            raise ValidationError('Нельзя использовать "{RESERVED_USERNAME}".')
        if not re.fullmatch(USERNAME_REGEX, username):
            raise ValidationError(
                'Имя пользователя содержит недопустимые символы.'
            )


class ValidateYear:
    def __call__(self, value):
        current_year = datetime.date.today().year
        if value > current_year:
            raise ValidationError('Год не может быть больше текущего.')
        return value
