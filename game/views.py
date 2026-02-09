from django.http import HttpResponse
# This imports the Character model so the view can look at the data
from .models import Character, Quest, Item, Location, Enemy
# 'get_object_or_404' to help us find a specific character or show an error if they don't exist
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
import requests
from random import randrange
import json, re 
from django.contrib import messages

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
    hero.max_health += 20
    hero.strength += 10
    hero.save()
    
    # Instead of HttpResponse, we send them to the 'character_detail' view
    # We pass the hero's ID so it knows which profile to show
    return redirect('character_detail', char_id=hero.id)

# ===== REST VIEW =====
def rest(request, char_id):
    # 1. Find the hero
    hero = get_object_or_404(Character, pk=char_id)
    
    hero.health = hero.max_health
    
    # 3. Save the changes - making the "Level Up" permanent
    hero.save()
    
    return redirect('character_detail', char_id=hero.id)

def recover_health(request, char_id, quest_id):
    hero = get_object_or_404(Character, pk=char_id)
    quest = get_object_or_404(Quest, pk=quest_id)
    hero.health = hero.max_health

    hero.save()

    return redirect('quest_detail', char_id=hero.id, quest_id=quest.id)

def quest_log(request, char_id):
    hero = get_object_or_404(Character, pk=char_id)
    active_quests = Quest.objects.filter(assigned_to=hero, is_completed=False)
    completed_quests = Quest.objects.filter(assigned_to=hero, is_completed=True)
    available_quests = Quest.objects.filter(assigned_to__isnull=True)

    # Auto-generate if board is empty
    if not available_quests.exists():
        return refresh_quests(request, char_id)

    return render(request, 'game/quest_log.html', {
        'hero': hero,
        'active_quests': active_quests,
        'completed_quests': completed_quests,
        'available_quests': available_quests,
    })

def refresh_quests(request, char_id):
    hero = get_object_or_404(Character, pk=char_id)
    Quest.objects.filter(assigned_to__isnull=True).delete()
    
    try:
        response = requests.post(
            "http://localhost:8001/generate-quests/", 
            json={"player_level": hero.level},
            timeout=60
        )
        if response.status_code == 200:
            ai_raw = response.json().get("response", "[]")
            # Regex to ensure we only get the JSON array
            json_match = re.search(r'\[.*\]', ai_raw, re.DOTALL)
            if json_match:
                quests = json.loads(json_match.group())
                for q in quests:
                    Quest.objects.create(
                        title=q.get('title', 'Unknown Task'),
                        description=q.get('description', 'No description provided.'),
                        xp_reward=int(q.get('xp_reward', 50)),
                        assigned_to=None
                    )
    except Exception as e:
        print(f"Quest Generation Failed: {e}")
        
    return redirect('quest_log', char_id=hero.id)

def assign_quest(request, char_id, quest_id):
    hero = get_object_or_404(Character, pk=char_id)
    quest = get_object_or_404(Quest, pk=quest_id)
    
    if request.method == "POST":
        quest.assigned_to = hero
        quest.save()
        
        # We generate 3 separate enemies to ensure they are distinct DB records
        for _ in range(3):
            try:
                # Re-using the logic: Passing quest title as the 'context'
                response = requests.post(
                    "http://localhost:8001/generate-enemy/", 
                    json={
                        "player_level": hero.level,
                        "context": f"Quest: {quest.title}" # Guide the AI
                    },
                    timeout=90
                )
                
                if response.status_code == 200:
                    data = response.json()
                    Enemy.objects.create(
                        name=data['name'],
                        health=int(data['health']),
                        attack_power=int(data['attack_power']),
                        xp_reward=int(data['xp_reward']),
                        quest=quest # Crucial: Link to the quest
                    )
            except Exception as e:
                print(f"Failed to generate quest enemy: {e}")

        return redirect('quest_detail', char_id=hero.id, quest_id=quest.id)
    
def quest_detail(request, char_id, quest_id):
    hero = get_object_or_404(Character, pk=char_id)
    quest = get_object_or_404(Quest, pk=quest_id)
    
    enemies = quest.enemies.all()
    total_enemies = enemies.count()
    defeated_count = enemies.filter(is_defeated=True).count()
    
    # Calculate percentage for the progress bar
    progress_percent = (defeated_count / total_enemies * 100) if total_enemies > 0 else 0
    
    return render(request, 'game/quest_detail.html', {
        'hero': hero,
        'quest': quest,
        'enemies': enemies,
        'progress_percent': progress_percent,
        'defeated_count': defeated_count,
        'total_enemies': total_enemies,
    })

def complete_quest(request, char_id, quest_id):
    hero = get_object_or_404(Character, pk=char_id)
    quest = get_object_or_404(Quest, pk=quest_id)
    
    # Validation: Ensure all enemies are actually dead
    enemies = quest.enemies.all()
    if enemies.filter(is_defeated=False).exists():
        messages.error(request, "You haven't finished the job yet!")
        return redirect('quest_detail', char_id=hero.id, quest_id=quest.id)

    if not quest.is_completed:
        # 1. Award XP
        hero.xp += quest.xp_reward
        quest.is_completed = True
        
        # 2. Check for Level Up (Standard Logic)
        if hero.xp >= 100:
            hero.level += 1
            hero.xp -= 100
            hero.strength += 10
            hero.max_health += 15
            messages.success(request, f"LEVEL UP! You are now Level {hero.level}!")
            
        hero.save()
        quest.save()
        messages.success(request, f"Quest Complete! You earned {quest.xp_reward} XP.")

    return redirect('quest_log', char_id=hero.id)

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
    enemy = hero.current_enemy

    if request.method == "POST" and enemy:
        # 1. Hero Attacks
        hero_strength = getattr(hero, 'strength', 10)
        enemy.health -= hero_strength
        enemy.save()

        # 2. Check for Victory
        if enemy.health <= 0:
            enemy.health = 0
            enemy.is_defeated = True # Mark as persistent death
            enemy.save()

            # Reward Hero
            hero.xp += enemy.xp_reward
            gold_loot = randrange(5, 20)
            hero.gold_amount += gold_loot
            
            # Level Up Logic
            if hero.xp >= 100:
                hero.level += 1
                hero.xp -= 100
                hero.strength += 10
                hero.max_health += 15
            
            # Clear fight state
            hero.current_enemy = None
            hero.save()

            # --- INNOVATIVE REDIRECT LOGIC ---
            if enemy.quest:
                messages.success(request, f"Victory! {enemy.name} was defeated.")
                # Redirect back to the quest tracker
                return redirect('quest_detail', char_id=hero.id, quest_id=enemy.quest.id)
            else:
                # Fallback for random encounters
                request.session['last_victory'] = {
                    'enemy_name': enemy.name,
                    'xp_gained': enemy.xp_reward,
                    'gold_amount_reward': gold_loot
                }
                # If it's a random enemy, you CAN delete it or keep it marked as is_defeated
                # For quests, we definitely keep it.
                return redirect('battle_arena', char_id=hero.id, enemy_id=0)

        # 3. Enemy Attacks Back
        hero.health -= enemy.attack_power
        hero.save()

        # 4. Check for Hero Death
        if hero.health <= 0:
            hero.health = 0
            hero.current_enemy = None
            hero.save()
            messages.error(request, "You have been defeated and retreated to town.")
            return redirect('character_detail', char_id=hero.id)

        return redirect('battle_arena', char_id=hero.id, enemy_id=enemy.id)

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
        response = requests.post(ai_service_url, json={
            "player_level": hero.level, 
            "environment": "Arena", 
            "player_health": hero.max_health, 
            "player_strength": hero.strength
            }, timeout=90)
        data = response.json()
        
        # Create the enemy
        new_enemy = Enemy.objects.create(
            name=data['name'],
            level=data['level'],
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