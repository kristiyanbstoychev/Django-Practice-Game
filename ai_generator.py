# ai_generator.py
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json
import re

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
def generate_enemy(req: EnemyRequest):
    # The Prompt Engineering
    prompt = f"""
    You are a Game Master for an RPG. Create a new enemy for a Level {req.player_level} player in a {req.environment}.
    
    Return ONLY a JSON object with these keys:
    - "name": A creative name.
    - "health": Integer between {req.player_level * 15} and {req.player_level * 25}.
    - "attack_power": Integer between {req.player_level * 2} and {req.player_level * 5}.
    - "xp_reward": Integer between {req.player_level * 10} and {req.player_level * 20}.
    
    Do not write any intro text. JUST the JSON.
    """

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