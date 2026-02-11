# ai_generator.py
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json
import re
import random

app = FastAPI()

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b" # Update this to your specific model name

class EnemyRequest(BaseModel):
    player_level: int
    environment: str

def clean_json(text):
    """Helper to extract JSON from the AI's chatty response"""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return "{}"

@app.post("/generate-enemy/")
def generate_enemy(req: dict):
    level = req.get('player_level', 1)
    health = req.get('player_health', 100)
    power = req.get('player_strength', 50)
    context = req.get('context', 'a dark forest')

    enemy_health = round(random.uniform(health * 1.5, health * 1.8), 2)
    enemy_power = round(random.uniform(power * 0.4, power * 0.6), 2)
    enemy_xp_reward = round(random.uniform(power * 0.2, power * 0.4), 2)
    
    prompt = (
        "You are a Game Master for an RPG. Create a new enemy. "
        f"The context is: {context}. "
        f"Return ONLY a JSON object with this exact keys, no additional text : name, health({enemy_health}), level({level}) attack_power({enemy_power}), xp_reward({enemy_xp_reward})"
    )

    print(f"--- PROMPT SENT TO OLLAMA ---\n{prompt}")

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response_json = response.json()
        raw_text = response_json.get("response", "")
        print(f"--- RAW AI RESPONSE ---\n{raw_text}")
        
        # Clean and Parse
        data = json.loads(clean_json(raw_text))
        return data
    except Exception as e:
        return {"error": str(e), "name": "Glitch Ghost", "health": 50, "attack_power": 5, "xp_reward": 10}

# Run with: uvicorn ai_generator:app --reload --port 8001

@app.post("/generate-quests/")
def generate_quests(req: dict):
    player_level = req.get('player_level', 1)
    base_xp = int((player_level ** 1.5) * 50)
    
    # Innovative prompt engineering to force specific quest types
    prompt = (
        f"You are a Quest Board for a fantasy RPG. Generate 3 unique COMBAT quests for a level {player_level} hero. "
        "The theme MUST be killing monsters or clearing dangerous areas. "
        "Each quest must have: 'title', 'description', and 'xp_reward'. "
        "Example Titles: 'Slay 3 Dire Wolves', 'Exterminate the Goblin Nest', 'Hunt the Elder Slime'. "
        f"XP rewards should be near {base_xp}. "
        "Return ONLY a JSON list of objects. One sentence max for descriptions."
    )
    
    print(f"--- PROMPT SENT TO AI --- \n {prompt}")

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.8,  # Slightly higher for more monster variety
            "num_predict": 400
        }
    }, timeout=90)
    
    return response.json()

@app.post("/generate-quest-enemies/")
def generate_quest_enemies(req: dict):
    quest_title = req.get('quest_title', 'Monster Hunting')
    player_level = req.get('player_level', 1)
    
    # We ask the LLM to provide a specific count and type based on the title
    prompt = (
        f"Based on the quest title '{quest_title}', generate a JSON list of 3 enemies. "
        f"Enemies should be appropriate for a Level {player_level} hero. "
        "Each object must have: 'name', 'health', 'attack_power', and 'xp_reward'. "
        "Return ONLY the JSON list."
    )
    print(f"--- PROMPT SENT TO OLLAMA --- \n {prompt}")

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }, timeout=90)
    
    print(f"--- RESPONSE FROM OLLAMA --- \n {response.json().get("response", "")}")

    return response.json()

@app.post("/generate-shop-items/")
def generate_shop_items(req: dict):
    level = req.get('player_level', 1)
    types = "HEAD, CHEST, FEET, GLOVES, RING, AMULET, WEAPON"

    prompt = (
        f"Generate 3 unique RPG items for a Level {level} character. "
        f"Each item must have a type from this list: [{types}]. "
        "Return a JSON list with: 'name', 'item_type', 'health_bonus', 'power_bonus', 'price(10g)'."
        "Return ONLY the JSON list."
    )
    
    print(f"---- PROMPT SENT TO AI ---- \n {prompt}")

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }, timeout=120)

    print(f"---- RESPONSE FROM AI ---- \n {response.json().get("response", "")}")
    
    return response.json()