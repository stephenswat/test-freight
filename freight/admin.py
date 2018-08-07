from django.contrib import admin

from freight.models import Entity, Location, Contract, Route


admin.site.register(Entity)
admin.site.register(Location)
admin.site.register(Contract)
admin.site.register(Route)
