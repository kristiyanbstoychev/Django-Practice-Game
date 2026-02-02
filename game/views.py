from django.http import HttpResponse
# This imports the Character model so the view can look at the data
from .models import Character, Quest, Item, Location
# 'get_object_or_404' to help us find a specific character or show an error if they don't exist
from django.shortcuts import get_object_or_404
from django.shortcuts import render # We use 'render' for templates

# ===== CHARACTER LIST VIEW =====
def character_list(request):
    all_characters = Character.objects.all()
    
    response_text = "<h1>World Heroes</h1>"
    
    for hero in all_characters:
        response_text += f"<hr><strong>{hero.name}</strong> (HP: {hero.health})<br>Location: {hero.current_location}<br> <hr>Inventory: <hr>"

        # Use the tether 'items' to find all items belonging to this specific hero
        # .all() here gets every item attached to this one character
        inventory = hero.items.all()
        for items in inventory:
            item_name = items.name
            item_power = items.power
            if inventory:
                response_text += f"{item_name} power/quantiy: {item_power} <br>"
            else:    
                response_text += 'Empty backpack'
                        
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

# ===== QUEST COMPLETION WITH REQUIREMENTS =====
def complete_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    hero = quest.assigned_to

    # 1. The Requirement: Hero must be at least Level 2
    if hero.level < 2:
        return HttpResponse(f"{hero.name}, you are too weak! You must be Level 2 to complete this quest.")

    # 2. If they meet the requirement, finish the quest
    if not quest.is_completed:
        quest.is_completed = True
        quest.save()
        
        # Reward
        reward = Item.objects.create(name="Gold", power=5, owner=hero)
        
        return HttpResponse(f"Quest Complete! {hero.name} received {reward.power} {reward.name}!")
    else:
        return HttpResponse("This quest was already finished!")
    
    # ===== BUY ITEM VIEW =====
def buy_item(request, char_id, item_id):
    # 1. Find the Hero and the Item
    hero = get_object_or_404(Character, pk=char_id)
    item = get_object_or_404(Item, pk=item_id)
    
    # 2. Check if the item actually belongs to a Merchant (or someone else)
    old_owner_name = item.owner.name
    
    # 3. Change the owner tether to our Hero
    item.owner = hero
    
    # 4. Save the change to the database
    item.save()
    
    return HttpResponse(f"{hero.name} bought {item.name} from {old_owner_name}!")

# ===== TRAVEL VIEW =====
def travel(request, char_id, loc_id):
    # 1. Fetch the hero and the destination
    hero = get_object_or_404(Character, pk=char_id)
    destination = get_object_or_404(Location, pk=loc_id)
    
    # 2. Update the hero's position
    hero.current_location = destination
    hero.save()
    
    return HttpResponse(f"{hero.name} traveled to the {destination.name}!")

def character_detail(request, char_id):
    hero = get_object_or_404(Character, pk=char_id)
    # This sends the 'hero' data to the HTML file
    return render(request, 'game/character_detail.html', {'hero': hero})