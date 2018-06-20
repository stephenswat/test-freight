from django.contrib.auth.models import User

from eve_auth.models import Character


SCOPE_NAMES = {
    'read_contracts': 'esi-contracts.read_character_contracts.v1',
    'open_window': 'esi-ui.open_window.v1',
}


class EveAuthBackend:
    def authenticate(self, request, info=None, tokens=None):
        scopes = info['Scopes'].split(' ')

        try:
            char = Character.objects.get(character_id=info['CharacterID'])
        except EveUser.DoesNotExist:
            user = User.objects.create_user(info['CharacterName'])
            char = Character(
                character_id=info['CharacterID']
                owner = user
            )

        char.name = info['CharacterName']
        char.scope_read_contracts = SCOPE_NAMES['read_contracts'] in scopes
        char.scope_open_window = SCOPE_NAMES['open_window'] in scopes

        char.tokens = tokens

        char.save()

        return char.owner
