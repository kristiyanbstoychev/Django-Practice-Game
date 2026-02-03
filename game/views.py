from django.http import HttpResponse
# This imports the Character model so the view can look at the data
from .models import Character, Quest, Item, Location, Enemy
# 'get_object_or_404' to help us find a specific character or show an error if they don't exist
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST

def main_menu(request):
    return render(request, 'game/main_menu.html')

def characters_listing(request):
    all_characters = Character.objects.all()
    # Ensure this filename is exactly correct
    return render(request, 'game/characters_listing.html', {'characters': all_characters})
  
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
def level_up(request, char_id):
    hero = get_object_or_404(Character, pk=char_id)
    hero.level += 1
    hero.health += 20
    hero.strength += 10
    hero.save()
    
    # Instead of HttpResponse, we send them to the 'character_detail' view
    # We pass the hero's ID so it knows which profile to show
    return redirect('character_detail', char_id=hero.id)

# ===== REST VIEW =====
def rest(request, char_id):
    # 1. Find the hero
    hero = get_object_or_404(Character, pk=char_id)
    
    hero.health = 100
    
    # 3. Save the changes - making the "Level Up" permanent
    hero.save()
    
    return redirect('character_detail', char_id=hero.id)

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
    
    return redirect('character_detail', char_id=hero.id)

def character_detail(request, char_id):
    hero = get_object_or_404(Character, pk=char_id)
    items = hero.items.all()

    request.session['active_char_id'] = hero.id

    return render(request, 'game/character_detail.html', {'hero': hero , 'items': items})

def rename_hero(request, char_id, new_name):
    hero = get_object_or_404(Character, pk=char_id)
    
    # Update the name
    hero.name = new_name
    hero.save()
    
    return redirect('character_detail', char_id=hero.id)

@require_POST # This ensures the API only responds to POST requests
def start_battle(request, char_id, enemy_id):
    # 1. Fetch both objects
    hero = get_object_or_404(Character, pk=char_id)
    enemy = get_object_or_404(Enemy, pk=enemy_id)

    # 2. Assign the 'tether'
    hero.current_enemy = enemy
    hero.save()

    # 3. Redirect or return a response
    return redirect('battle_arena', char_id=hero.id)

def attack_enemy(request, char_id):
    hero = get_object_or_404(Character, pk=char_id)
    enemy = hero.current_enemy

    if request.method == "POST" and enemy:
        # 1. Hero deals damage
        enemy.health -= hero.strength # Assuming you have a 'strength' field
        enemy.save()

        # 2. Check if enemy is still alive
        if enemy.health <= 0:
           if enemy.health <= 0:
            # 1. Award XP
            hero.xp += enemy.xp_reward
            enemy.health = 100
        # 2. Check for Level Up
            if hero.xp >= 100:
                hero.level += 1
                hero.health += 20
                hero.xp = 0 # Reset or carry over XP
                # You could also add a message here!
            # 3. Cleanup
            hero.current_enemy = None
            hero.save()
            return redirect('character_detail', char_id=hero.id)
        
        # 3. Enemy Retaliation (Only happens if enemy.health > 0)
        hero.health -= enemy.attack_power
        hero.save()

    return redirect('battle_arena', char_id=hero.id)

def select_enemy(request, char_id):
    hero = get_object_or_404(Character, pk=char_id)
    # Get all monsters currently in the database
    available_enemies = Enemy.objects.all() 
    
    return render(request, 'game/select_enemy.html', {
        'hero': hero,
        'enemies': available_enemies
    })

def battle_arena(request, char_id):
    hero = get_object_or_404(Character, pk=char_id)
    # Get the enemy linked to this hero
    enemy = hero.current_enemy 
    
    if not enemy:
        # If no enemy is assigned, send them back to pick one
        return redirect('select_enemy', char_id=hero.id)

    return render(request, 'game/battle_arena.html', {
        'hero': hero,
        'enemy': enemy
    })