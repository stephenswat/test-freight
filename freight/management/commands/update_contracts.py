from django.core.management.base import BaseCommand, CommandError

from freight.tasks import update_contracts


class Command(BaseCommand):
    help = 'Updates the contract list'

    def handle(self, *args, **options):
        update_contracts()
