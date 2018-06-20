import itertools
import datetime
from esipy.exceptions import APIException

from django.conf import settings
from django.db import models

from eve_esi import ESI


class Character(models.Model):
    id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    name = models.CharField(max_length=64, db_index=True, unique=True)

    scope_read_contracts = models.BooleanField()
    scope_open_window = models.BooleanField()

    access_token = models.CharField(max_length=128)
    refresh_token = models.CharField(max_length=128)
    token_expiry = models.DateTimeField()

    def __str__(self):
        return self.name

    @property
    def tokens(self):
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_in': (
                self.token_expiry -
                datetime.datetime.utcnow()
            ).total_seconds(),
            'token_type': 'Bearer',
        }

    @tokens.setter
    def tokens(self, token):
        self.access_token = token['access_token']
        self.refresh_token = token['refresh_token']
        self.token_expiry = (
            datetime.datetime.utcnow() +
            datetime.timedelta(seconds=token['expires_in'])
        )

    def get_security(self):
        res = ESI.get_security()
        res.update_token(self.tokens)

        if res.is_token_expired(offset=60):
            try:
                self.tokens = res.refresh()
                self.save()
            except APIException as e:
                if e.status_code == 400:
                    raise EveUser.KeyDeletedException(
                        "ESI refused to refresh our tokens."
                    )
                raise

        return res

    def get_client(self):
        return ESI.get_client(self.get_security())

    def get_contracts(self):
        results = []

        for page in itertools.count(start=1):
            op = ESI['get_characters_character_id_contracts'](
                character_id=self.character_id
            )

            req = self.get_client().request(op)

            results += req.data

            if page >= req.header['X-Pages'][0]:
                break

        return results

    class KeyDeletedException(Exception):
        pass
