from django.contrib import admin
from .models import Character, Item, Quest, Location

# This tells Django to show the Character section in the Admin dashboard
admin.site.register(Character)
admin.site.register(Item)
admin.site.register(Quest)
admin.site.register(Location)