from django.contrib import admin

from freight.models import Character, Location, Contract, Route


admin.site.register(Character)
admin.site.register(Location)
admin.site.register(Contract)
admin.site.register(Route)
