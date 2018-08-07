import itertools
import logging
import datetime
import pprint

from django.conf import settings
from django.db.models import Q
from django.db import transaction

from huey import crontab
from huey.contrib.djhuey import db_periodic_task

from eve_auth.models import Character as AuthCharacter
from eve_esi import ESI
from freight.models import Contract, Entity


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

def parse_swagger_datetime(sdt):
    return datetime.datetime.strptime(
        str(sdt),
        r"%Y-%m-%dT%H:%M:%S+00:00"
    )

@db_periodic_task(crontab(minute='*/10'))
def update_contracts():
    client = ESI.get_client()

    for c in AuthCharacter.objects.filter(scope_read_contracts=True):
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
        except AuthCharacter.KeyDeletedException:
            logger.warning('Scraper %d revoked their key.', c.id)
            continue

        interesting = [
            x for x in contracts
            if x['type'] == 'courier'
            and x['assignee_id'] == settings.ALLIANCE_ID
        ]

        char_set = set()

        for i in interesting:
            char_set.add(i['issuer_id'])

            if i['acceptor_id'] != 0:
                    char_set.add(i['acceptor_id'])

        for unknown in char_set - set(Entity.objects.values_list('id', flat=True)):
            try:
                Entity.objects.get_from_db_or_esi(unknown)
            except KeyError:
                continue

        with transaction.atomic():
            for i in interesting:
                try:
                    issuer = Entity.objects.get(id=i['issuer_id'])

                    if i['acceptor_id'] != 0:
                        acceptor = Entity.objects.get(id=i['acceptor_id'])
                    else:
                        acceptor = None
                except Entity.DoesNotExist:
                    continue

                Contract.objects.update_or_create(
                    id=i['contract_id'],
                    defaults={
                        'title': i['title'],
                        'volume': i['volume'],
                        'status': Contract.STATUS_MAP[i['status']],
                        'issuer': issuer,
                        'acceptor': acceptor,
                        'collateral': i['collateral'],
                        'reward': i['reward'],
                        'date_accepted': parse_swagger_datetime(i['date_accepted']) if 'date_accepted' in i else None,
                        'date_completed': parse_swagger_datetime(i['date_completed']) if 'date_completed' in i else None,
                        'date_expired': parse_swagger_datetime(i['date_expired']),
                        'date_issued': parse_swagger_datetime(i['date_issued']),
                        'days_to_complete': i['days_to_complete'],
                        'start_location_id': i['start_location_id'],
                        'end_location_id': i['end_location_id']
                    }
                )

            Contract.objects.filter(
                ~Q(status=Contract.STATUS_DISAPPEARED),
                ~Q(id__in={x['contract_id'] for x in interesting})
            ).update(status=Contract.STATUS_DISAPPEARED)

        return
    else:
        logger.error('No suitable scraper was available!')
