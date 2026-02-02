from django.http import HttpResponse
# This imports the Character model so the view can look at the data
from .models import Character
# 'get_object_or_404' to help us find a specific character or show an error if they don't exist
from django.shortcuts import get_object_or_404

# ===== CHARACTER LIST VIEW =====
def character_list(request):
    all_characters = Character.objects.all()
    
    response_text = "<h1>World Heroes</h1>"
    
    for hero in all_characters:
        # Use the tether 'items' to find all items belonging to this specific hero
        # .all() here gets every item attached to this one character
        inventory = hero.items.all()

        # Create a list of item names - like listing contents of a backpack
        item_names = ", ".join([item.name for item in inventory]) or "Empty Backpack"
        
        response_text += f"<p><strong>{hero.name}</strong> (HP: {hero.health})<br>"
        response_text += f"Inventory: {item_names}</p><hr>"
    
    return HttpResponse(response_text)

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