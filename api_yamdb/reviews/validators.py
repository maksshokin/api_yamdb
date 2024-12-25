import re
import datetime

from django.core.exceptions import ValidationError
from api.constants import (
    USERNAME_REGEX, RESERVED_USERNAME, USERNAME_MAX_LENGTH
)


class ValidateUsername:
    def __call__(self, username):
        if username == RESERVED_USERNAME:
            raise ValidationError('Имя пользователя "me" зарезервировано.')
        if not re.fullmatch(USERNAME_REGEX, username):
            raise ValidationError(
                'Имя пользователя содержит недопустимые символы.'
            )
        if len(username) > USERNAME_MAX_LENGTH:
            raise ValidationError('Слишком длинный ник!')
        return username


class ValidateYear:
    def __call__(self, value):
        current_year = datetime.date.today().year
        if value > current_year:
            raise ValidationError('Год не может быть больше текущего.')
        return value
