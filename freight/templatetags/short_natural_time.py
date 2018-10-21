"""

STOLEN FROM:

https://github.com/ollieglass/django-shortnaturaltime

"""


from django import template
from django.utils.timezone import utc

import time
from datetime import datetime, timedelta, date

register = template.Library()

def _now():
    # return datetime.utcnow().replace(tzinfo=utc)
    return datetime.now()

def abs_timedelta(delta):
    if delta.days < 0:
        now = _now()
        return now - (now + delta)
    return delta

def date_and_delta(value):
    now = _now()
    if isinstance(value, datetime):
        date = value
        delta = now - value
    elif isinstance(value, timedelta):
        date = now - value
        delta = value
    else:
        try:
            value = int(value)
            delta = timedelta(seconds=value)
            date = now - delta
        except (ValueError, TypeError):
            return (None, value)
    return date, abs_timedelta(delta)

def shortnaturaldelta(value):
    now = _now()
    date, delta = date_and_delta(value)

    if date is None:
        return value

    days = abs(delta.days)
    hours = (abs(delta.seconds) // (60 * 60)) % 24

    minutes = (abs(delta.seconds) // (60)) % 60

    if days >= 1:
        return "%d day, %d hours" % (days, hours)
    elif hours >= 1:
        return "%d hours" % (hours)
    else:
        return "%d minutes" % (minutes)

@register.filter
def short_natural_time(value):
    now = _now()
    date, delta = date_and_delta(value)
    if date is None:
        return value

    delta = shortnaturaldelta(delta)

    if delta == "a moment":
        return "now"

    return delta
