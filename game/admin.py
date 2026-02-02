from django.contrib import admin
# This imports Character "blueprint" from models file
from .models import Character, Item

# This tells Django to show the Character section in the Admin dashboard
admin.site.register(Character)
admin.site.register(Item)