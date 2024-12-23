import re

from django.core.exceptions import ValidationError


class ValidateUsername:
    def validate_username(self, username):
        pattern = re.compile(r'^[\w.@+-]+')

        if pattern.fullmatch(username) is None:
            error = re.split(pattern, username)
            raise ValidationError(f'Нельзя использовать {error}!')
        if username == 'me':
            raise ValidationError('Нельзя использовать me!')
        if len(username) >150:
            raise ValidationError('Слишком длинный ник!')
        return username
