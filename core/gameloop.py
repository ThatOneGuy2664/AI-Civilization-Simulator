from pathlib import Path
from core.outcome_handlers import (
    economy,
    diplomacy,
    settlements,
    research,
    military,
    construction,
    general,
    policy,
    population
)
import requests
import json
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from ai.narrator_ai import NarratorAI
from ai.parser_ai import ParserAI
from game_properties import *

def format_table(table, indent=0):
    output = ""
    for key, value in table.items():
        if isinstance(value, dict):
            output += " " * indent + key.capitalize() + ":\n"
            output += format_table(value, indent + 4)
        else:
            output += " " * indent + f"{key.capitalize()}: {value}\n"
    return output

# Player action handlers
ACTION_HANDLERS = {}

for module in (
    economy,
    diplomacy,
    settlements,
    research,
    military,
):
    ACTION_HANDLERS.update(module.HANDLERS)

def get_outcome(gamestate, player_action):
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": ai_model_id,
            "messages": [
                {
                    "role": "system",
                    "content": ParserAI.SYSTEM_INSTRUCTIONS,
                },
                {
                    "role": "user",
                    "content": player_action,
                },
            ],
            "think": False,
            "stream": False,
            "keep_alive": "30m",
        },
        stream=False,
    )

    parser_output = response.json()["message"]["content"]
    data = json.loads(parser_output)

    results = []

    for action in data["actions"]:
        handler = ACTION_HANDLERS.get(action["action"])

        if handler is None:
            print(f"Unknown action: {action['action']}")
            continue

        result = handler(gamestate, action)
        results.append(result)

    return results

# This is the generated summary for the AI of the player empire's state
def create_prompt(world, player_action, outcome):
    name = world["name"]
    gov_type = world["government"]["type"]
    era = world["era"]
    pop = world["empire_population"]
    resources = format_table(world["resources"])
    military = format_table(world["military"])
    modifiers = format_table(world["modifiers"])
    wartime = world["wartime"]
    day = world["day"]
    history = "\n".join(world["history"])

    prompt = f"""
Civilization:
{name}

Government:
{gov_type}

Era:
{era}

Total Population:
{pop}

Resources:
{resources}

Military:
{military}

Modifiers:
{modifiers}

History:
{history}

Day: {day}
At war: {wartime}

Ruler's Attempted Action:
{player_action}

Outcome:
{outcome}
"""
    return prompt

def send_prompt(prompt):
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": ai_model_id,
            "messages": [
                {
                    "role": "system",
                    "content": NarratorAI.SYSTEM_INSTRUCTIONS,
                },
                {
                    "role": "system",
                    "content": prompt,
                },
            ],
            "think": False,
            "stream": True,
            "keep_alive": "30m",
        },
        stream=True,
    )

    for line in response.iter_lines():
        if not line:
            continue

        chunk = json.loads(line)
        message = chunk.get("message", {})
        content = message.get("content", "")

        if content:
            yield content

class Game:
    def __init__(self, savedata):
        self.gamestate = savedata

    def process_turn(self, player_action):
        prompt = create_prompt(
            self.gamestate,
            player_action,
            get_outcome(self.gamestate, player_action)
        )

        print("AI prompt:\n" + prompt)

        return send_prompt(prompt)
