from django.http import HttpResponse
# This imports the Character model so the view can look at the data
from .models import Character, Quest
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

# ===== COMBAT VIEW WITH SESSION TRACKING =====
def basic_combat(request, char_id):
    hero = get_object_or_404(Character, pk=char_id)
    
    # 1. Get the current battle count from the "Visitor's Badge" (Session)
    # If it doesn't exist yet, we start at 0
    total_battles = request.session.get('battle_count', 0)
    
    # 2. Perform combat logic
    damage = 20
    hero.health -= damage
    hero.save()
    
    # Check the hero's status
    if hero.health <= 0:
        status_message = f"{hero.name} has been defeated! Game Over."
        # Reset health for the next attempt
        hero.health = 100
        hero.save()
    else:
        status_message = f"{hero.name} took {damage} damage. <br>Remaining HP: {hero.health}.<br> <br>"

    # 3. Increase the count and save it back to the session
    request.session['battle_count'] = total_battles + 1
    
    status_message += f"Total battles fought this session: {request.session['battle_count']}"
    
    return HttpResponse(status_message)

# ===== LEVEL UP VIEW =====
# This function makes a specific hero stronger
def level_up(request, char_id):
    # 1. Find the hero
    hero = get_object_or_404(Character, pk=char_id)
    
    # 2. Increase stats - adding to the existing numbers
    hero.level += 1
    hero.health += 20 # Give them more health for leveling up
    
    # 3. Save the changes - making the "Level Up" permanent
    hero.save()
    
    return HttpResponse(f"{hero.name} reached Level {hero.level}! Health increased to {hero.health}.")

# ===== REST VIEW =====
def rest(request, char_id):
    # 1. Find the hero
    hero = get_object_or_404(Character, pk=char_id)
    
    hero.health = 100
    
    # 3. Save the changes - making the "Level Up" permanent
    hero.save()
    
    return HttpResponse(f"{hero.name} reached Level {hero.level}! Health increased to {hero.health}.")

# ===== QUEST LOG VIEW =====
def quest_log(request, char_id):
    hero = get_object_or_404(Character, pk=char_id)
    
    # 1. Filter for quests that belong to THIS hero and are NOT done
    # 'assigned_to=hero' checks the owner
    # 'is_completed=False' checks the status
    active_quests = Quest.objects.filter(assigned_to=hero, is_completed=False)
    
    # 2. Filter for quests that ARE done
    completed_quests = Quest.objects.filter(assigned_to=hero, is_completed=True)
    
    # 3. Build the display
    response = f"<h1>{hero.name}'s Quest Log</h1>"
    
    response += "<h3>Active Quests:</h3><ul>"
    for q in active_quests:
        response += f"<li>{q.title} (ID: {q.id})</li>"
    response += "</ul>"
    
    response += "<h3>Completed Quests:</h3><ul>"
    for q in completed_quests:
        response += f"<li>{q.title}</li>"
    response += "</ul>"
    
    return HttpResponse(response)

# ===== ASSIGN QUEST VIEW =====
def assign_quest(request, char_id, quest_id):
    hero = get_object_or_404(Character, pk=char_id)
    quest = get_object_or_404(Quest, pk=quest_id)
    
    quest.assigned_to = hero
    
    return HttpResponse(f"Quest '{quest.title}' assigned to {hero.name}!")

# ===== COMPLETE QUEST VIEW =====
def complete_quest(request, quest_id):
    # Find the quest by its own unique ID
    quest = get_object_or_404(Quest, pk=quest_id)
    
    # Flip the switch to True
    quest.is_completed = True
    quest.save()
    
    # Give the hero a reward for finishing!
    hero = quest.assigned_to
    hero.level += 1
    hero.save()
    
    return HttpResponse(f"{quest.title} completed! {hero.name} reached Level {hero.level}.")