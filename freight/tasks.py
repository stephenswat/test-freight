import itertools
import logging

from django.conf import settings

from huey import crontab
from huey.contrib.djhuey import db_periodic_task

from eve_auth.models import Character
from eve_esi import ESI


logger = logging.getLogger(__name__)


def get_corporation_contracts(corporation_id, client):
        results = []

        for page in itertools.count(start=1):
            op = ESI['get_corporations_corporation_id_contracts'](
                corporation_id=corporation_id,
                page=page
            )

            req = client.request(op)
            results += req.data

            if page >= req.header['X-Pages'][0]:
                break

        return results

@db_periodic_task(crontab(minute='*/10'))
def update_contracts():
    client = ESI.get_client()

    for c in Character.objects.filter(scope_read_contracts=True):
        allegiance = client.request(
            ESI['get_characters_character_id'](character_id=c.id)
        ).data

        if allegiance.get('alliance_id', -1) != settings.ALLIANCE_ID:
            logger.warning('Scraper %d is in the wrong alliance.', c.id)
            continue

        try:
            contracts = get_corporation_contracts(
                allegiance['corporation_id'],
                c.get_client()
            )
        except Character.KeyDeletedException:
            logger.warning('Scraper %d revoked their key.', c.id)
            continue

        print(contracts)
        return
    else:
        logger.error('No suitable scraper was available!')
