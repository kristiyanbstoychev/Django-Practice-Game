from django.http import HttpResponse
# This imports the Character model so the view can look at the data
from .models import Character, Quest, Item, Location, Enemy
# 'get_object_or_404' to help us find a specific character or show an error if they don't exist
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
import requests

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

# game/views.py
def quest_log(request, char_id):
    hero = get_object_or_404(Character, pk=char_id)
    
    active_quests = Quest.objects.filter(assigned_to=hero, is_completed=False)
    completed_quests = Quest.objects.filter(assigned_to=hero, is_completed=True)
    
    # We also need available quests that haven't been assigned yet
    # Assuming 'assigned_to' is null for unaccepted quests
    available_quests = Quest.objects.filter(assigned_to__isnull=True)

    context = {
        'hero': hero,
        'active_quests': active_quests,
        'completed_quests': completed_quests,
        'available_quests': available_quests,
    }
    
    return render(request, 'game/quest_log.html', context)

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

def create_character(request):
    if request.method == "POST":
        name = request.POST.get('name')
        if name:
            # Create the character and save to DB
            Character.objects.create(name=name)
            return redirect('characters_listing')
    
    return render(request, 'game/create_character.html')

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
    
    # Use the hero's current_enemy relationship
    enemy = hero.current_enemy

    if request.method == "POST" and enemy:
        # 1. Hero Attacks
        enemy.health -= getattr(hero, 'strength', 10)
        enemy.save()

        # 2. Check for Victory
        if enemy.health <= 0:
            hero.xp += enemy.xp_reward
            request.session['last_victory'] = {
                'enemy_name': enemy.name,
                'xp_gained': enemy.xp_reward
            }
            # Handle Level Up
            if hero.xp >= 100:
                hero.level += 1
                hero.xp -= 100
            
            hero.current_enemy = None # Clear the fight
            hero.save()
            enemy.delete() # Cleanup the AI monster
            return redirect('battle_arena', char_id=hero.id, enemy_id=0)

        # 3. Enemy Attacks Back (Only if still alive)
        hero.health -= enemy.attack_power
        hero.save()

        # 4. Check for Hero Death
        if hero.health <= 0:
            hero.health = 0
            hero.current_enemy = None
            hero.save()
            return redirect('character_list') # Or a game over page

        # SUCCESS: Stay in the arena with the current enemy
        return redirect('battle_arena', char_id=hero.id, enemy_id=enemy.id)

    # FAILURE: If the code reaches here, 'enemy' was None.
    # We redirect back to the arena which will handle the "no enemy" state.
    return redirect('battle_arena', char_id=hero.id, enemy_id=0)

def select_enemy(request, char_id):
    hero = get_object_or_404(Character, pk=char_id)
    # Get all monsters currently in the database
    available_enemies = Enemy.objects.all() 
    
    return render(request, 'game/select_enemy.html', {
        'hero': hero,
        'enemies': available_enemies
    })

# game/views.py
def battle_arena(request, char_id, enemy_id):
    hero = get_object_or_404(Character, pk=char_id)
    victory_data = None
    enemy = None

    if enemy_id == 0:
        # Check if we just won
        victory_data = request.session.pop('last_victory', None)
        # If there's no victory data and no enemy, the page will look empty
    else:
        # Fetch the specific enemy
        enemy = get_object_or_404(Enemy, pk=enemy_id)
        
        # Sync the hero's current_enemy field just in case
        if hero.current_enemy != enemy:
            hero.current_enemy = enemy
            hero.save()

    return render(request, 'game/battle_arena.html', {
        'hero': hero,
        'enemy': enemy,
        'victory': victory_data
    })

def generate_new_enemy(request, char_id):
    if request.method != "POST":
        return redirect('character_detail', char_id=char_id)

    hero = get_object_or_404(Character, pk=char_id)
    ai_service_url = "http://localhost:8001/generate-enemy/"
    
    try:
        print(f"Requesting AI for Hero {hero.id}...")
        response = requests.post(ai_service_url, json={"player_level": hero.level, "environment": "Arena"}, timeout=10)
        data = response.json()
        
        # Create the enemy
        new_enemy = Enemy.objects.create(
            name=data['name'],
            health=int(data['health']),
            attack_power=int(data['attack_power']),
            xp_reward=int(data.get('xp_reward', 10))
        )
        
        print(f"Enemy Created: {new_enemy.name} (ID: {new_enemy.id})")
        print(f"Attempting redirect to battle_arena with char_id={hero.id} and enemy_id={new_enemy.id}")

        # CRITICAL: Ensure 'battle_arena' matches the 'name' in urls.py exactly
        return redirect('battle_arena', char_id=hero.id, enemy_id=new_enemy.id)

    except Exception as e:
        print(f"ERROR OCCURRED: {e}")
        return redirect('character_detail', char_id=char_id)