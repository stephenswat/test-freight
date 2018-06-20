from django.db import models

from eve_esi import ESI


class CharacterManager(models.Manager):
    def get_from_db_or_esi(self, character_id):
        try:
            return Character.objects.get(id=character_id)
        except Character.DoesNotExist:
            character_data = ESI.get_client().request(
                ESI['get_characters_character_id'](character_id=character_id)
            ).data

            character = Character(
                id=character_id,
                name=character_data['name']
            )

            character.save()

            return character


class Character(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=64, db_index=True, unique=True)

    objects = CharacterManager()

    def __str__(self):
        return self.name


class Location(models.Model):
    id = models.BigIntegerField(primary_key=True)
    full_name = models.CharField(max_length=64)
    short_name = models.CharField(max_length=64)

    def __str__(self):
        return self.short_name


class Contract(models.Model):
    STATUS_OUTSTANDING = 0
    STATUS_IN_PROGRESS = 1
    STATUS_FINISHED_ISSUER = 2
    STATUS_FINISHED_CONTRACTOR = 3
    STATUS_FINISHED = 4
    STATUS_CANCELLED = 5
    STATUS_REJECTED = 6
    STATUS_FAILED = 7
    STATUS_DELETED = 8
    STATUS_REVERSED = 9
    STATUS_DISAPPEARED = 10

    STATUS_CHOICES = (
        (STATUS_OUTSTANDING, 'Outstanding'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_FINISHED_ISSUER, 'Finished (issuer)'),
        (STATUS_FINISHED_CONTRACTOR, 'Finished (contractor)'),
        (STATUS_FINISHED, 'Finished'),
        (STATUS_CANCELLED, 'Canceled'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_DELETED, 'Deleted'),
        (STATUS_REVERSED, 'Reversed'),
        (STATUS_DISAPPEARED , 'Disappeared'),
    )

    # TODO: Hey do you smell any technical debt here?

    STATUS_MAP = {
        'outstanding': 0,
        'in_progress': 1,
        'finished_issuer': 2,
        'finished_contractor': 3,
        'finished': 4,
        'cancelled': 5,
        'rejected': 6,
        'failed': 7,
        'deleted': 8,
        'reversed': 9

    }

    id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=256)
    volume = models.DecimalField(max_digits=32, decimal_places=5)
    status = models.SmallIntegerField(db_index=True, choices=STATUS_CHOICES)

    issuer = models.ForeignKey(
        Character,
        models.CASCADE,
        related_name='issued_contracts'
    )
    acceptor = models.ForeignKey(
        Character,
        models.CASCADE,
        related_name='accepted_contracts',
        null=True
    )

    collateral = models.DecimalField(max_digits=32, decimal_places=2)
    reward = models.DecimalField(max_digits=32, decimal_places=2)

    date_accepted = models.DateTimeField(null=True)
    date_completed = models.DateTimeField(null=True)
    date_expired = models.DateTimeField()
    date_issued = models.DateTimeField()

    days_to_complete = models.SmallIntegerField()

    start_location = models.ForeignKey(
        Location,
        models.CASCADE,
        related_name='start_contracts',
        db_constraint=False
    )
    end_location = models.ForeignKey(
        Location,
        models.CASCADE,
        related_name='end_contracts',
        db_constraint=False
    )

    @property
    def start(self):
        try:
            return self.start_location
        except Location.DoesNotExist:
            return None

    @property
    def end(self):
        try:
            return self.end_location
        except Location.DoesNotExist:
            return None

    def __str__(self):
        return "{org} to {dst} ({volume} m3)".format(
            org=self.start.short_name if self.start is not None else 'Unknown',
            dst=self.end.short_name if self.end is not None else 'Unknown',
            volume=self.volume
        )


class Route(models.Model):
    start = models.ForeignKey(
        Location,
        models.CASCADE,
        related_name='+',
        db_index=True
    )
    end = models.ForeignKey(
        Location,
        models.CASCADE,
        related_name='+',
        db_index=True
    )

    price_per_m3 = models.IntegerField()

    def __str__(self):
        return "{org} to {dst}".format(
            org=self.start.short_name,
            dst=self.end.short_name
        )
