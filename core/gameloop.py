from pathlib import Path
import requests
import json
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from ai.narrator_ai import NarratorAI

def format_table(table, indent=0):
    output = ""
    for key, value in table.items():
        if isinstance(value, dict):
            output += " " * indent + key.capitalize() + ":\n"
            output += format_table(value, indent + 4)
        else:
            output += " " * indent + f"{key.capitalize()}: {value}\n"
    return output

# This is the generated summary for the AI of the player empire's state
def create_prompt(world, player_action):
    name = world["name"]
    gov_type = world["government"]["type"]
    era = world["era"]
    pop = world["population"]
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

Population:
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

Ruler Action:
{player_action}
"""
    return prompt

def send_prompt(prompt):
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "qwen3:14b",
            "messages": [
                {
                    "role": "system",
                    "content": NarratorAI.SYSTEM_INSTRUCTIONS,
                },
                {
                    "role": "user",
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
        )

        return send_prompt(prompt)
