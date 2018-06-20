from django.db import transaction
from django.contrib.auth.models import User

from eve_auth.models import Character


SCOPE_NAMES = {
    'read_contracts': 'esi-contracts.read_character_contracts.v1',
    'open_window': 'esi-ui.open_window.v1',
}


class EveAuthBackend:
    def authenticate(self, request, info=None, tokens=None):
        scopes = info['Scopes'].split(' ')

        with transaction.atomic():
            try:
                char = Character.objects.get(id=info['CharacterID'])
            except Character.DoesNotExist:
                char = Character(id=info['CharacterID'])

            if request.user.is_authenticated:
                char.owner = request.user
            elif not hasattr(char, 'owner') or char.owner is None:
                char.owner = User.objects.create_user(info['CharacterName'])

            char.name = info['CharacterName']
            char.scope_read_contracts = SCOPE_NAMES['read_contracts'] in scopes
            char.scope_open_window = SCOPE_NAMES['open_window'] in scopes

            char.tokens = tokens

            char.save()

        return char.owner

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
