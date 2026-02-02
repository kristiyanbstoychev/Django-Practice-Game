from django.http import HttpResponse
# This imports the Character model so the view can look at the data
from .models import Character
# 'get_object_or_404' to help us find a specific character or show an error if they don't exist
from django.shortcuts import get_object_or_404

# ===== CHARACTER LIST VIEW =====
# This function handles the request to see all heroes
def character_list(request):
    # This asks the database: "Give me every character you have!"
    all_characters = Character.objects.all()
    
    # We will start by creating a simple text string of names
    # Like making a list of names on a piece of paper
    names = ", ".join([c.name for c in all_characters])
    
    # This sends the list back to the user's browser
    return HttpResponse(f"Heroes in this world: {names}")

# ===== COMBAT VIEW =====
# This function handles a "fight" for a specific character using their ID number
def basic_combat(request, char_id):
    # 1. Find the hero in the database using their unique ID number
    hero = get_object_or_404(Character, pk=char_id)
    
    # 2. Define the damage - like a monster hitting for 10 points
    damage = 10
    
    # 3. Update the health - taking away "hearts" from the hero
    hero.health -= damage
    
    # 4. Save the change - this is CRITICAL! It writes the new health back to the database
    hero.save()
    
    return HttpResponse(f"{hero.name} took {damage} damage! Current Health: {hero.health}")