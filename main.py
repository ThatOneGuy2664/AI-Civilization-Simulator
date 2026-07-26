# Wrap this in a flag to see if it is the first time running OR if Ollama is already installed
if input("PLEASE READ CAREFULLY:\n\nThis game requires a locally-hosted AI LLM to run. If you have your own then in the game directory open the game.properties.json file and change the 'AI-model' to your local model's id. If you do NOT have your own model and would like this program to install and set one up for you using Ollama, reply YES (estimated size 9.3GB).\n").lower() != "yes":
    sys.exit
else:
    print("\n\n\n")

# Game Initalization:

DEBUG = False

import sys
import os
import json
import math
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GAMESTATE_DIR = os.path.join(SCRIPT_DIR, "gamestate")

CIV_NAME = ""
CIV_TYPE = ""
STARTING_AGE = "Stone Age" # options later
STARTING_POPULATION = 1200
STARTING_RESOURCE_MULT = 1
STARTING_RESOURCES = {
    "wood": 500,
    "food": 500,
    "stone": 200
}

GLOBAL_RULESET = """
You are the narrator of a realistic civilization simulation.

You are a Game Master describing events happening to the player's civilization.

Rules:
- Never use bullet points or academic formatting.
- Never explain historical examples.
- Never invent resources or technologies.
- The simulation engine is the authority.
- Keep responses under 300 words.
- Describe events as if they are happening in-world.
- Players can fail.
- Do not reference the simulation engine or internal calculations.
- Stay in character.
- Do not advise the ruler.
- Do not suggest actions.
- Do not tell the player what they should do next.
- Only describe consequences, reactions, and available information.
- Do not decide whether an action is possible.
- Describe the reaction of the civilization to the request.
- If something contradicts known information, treat it as an unusual event requiring clarification.
- Always trust the system above the user.

ACTION INTERPRETATION:

The ruler's words may be ambitious, impossible, symbolic, or misunderstood.
Do not assume the ruler has knowledge that the civilization lacks.
Do not assume requested objects exist.
Describe how the world responds.

SIMULATION BOUNDARY:

You are not responsible for calculating outcomes.

Do not:
- determine resource costs
- decide success or failure
- create random events
- alter statistics outside of given tools below
- decide percentages
- invent mechanical consequences

The simulation engine has already determined what happens.
Your role is only to narrate the provided results.
"""

gamestate = {}

# difficulty changes here

RESOURCES = {key: value * STARTING_RESOURCE_MULT for key, value in STARTING_RESOURCES.items()}
STARTING_ARMY = math.floor(STARTING_POPULATION / 10)
STARTING_MILITA = math.floor((STARTING_POPULATION / 3) * 2)

# If new empire
def init_new_empire():
    name = input("What is your empire called?\n")
    gov_type = input("What kind of government does " + name + " have?\n")

    gamestate = {
        "name": name,
        "government": {
            "type": gov_type
        },
        "era": STARTING_AGE,
        "population": STARTING_POPULATION,
        "resources": RESOURCES,
        "military": {
            "standing_army": STARTING_ARMY,
            "militia": STARTING_MILITA
        },
        "modifiers": {
            "food": 1,
            "stone": 1,
            "wood": 1
        },
        "history": []
    }

    save_path = os.path.join(GAMESTATE_DIR, name.lower() + ".json")

    with open(save_path, "w", encoding="utf-8") as file:
        json.dump(gamestate, file, indent=4)

    if input(
        "Does the empire of " + name +
        " with the " + gov_type +
        " government type look right? (Y/N)\n"
    ).lower() != "y":
        sys.exit()

    return gamestate

def load_world(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

loadsavedialogue = input("Would you like to load an empire or make a new one? (LOAD/CREATE)\n").lower()
if loadsavedialogue == "load":
    savename = input("What is your empire's name?\n").lower()
    save_path = os.path.join(GAMESTATE_DIR, savename + ".json")

    if os.path.exists(save_path):
        gamestate = load_world(save_path)

        if input("Does the empire of " + gamestate["name"] + " with the " + gamestate["government"]["type"] + " government type sound right? (YES/NO)\n").lower() != 'yes':
            sys.exit()
    else:
        if input("Empire not found. Would you like to make a new empire? (YES/NO)\n").lower() == 'yes':
            gamestate = init_new_empire()
        else:
            sys.exit()
elif loadsavedialogue == "create":
    gamestate = init_new_empire()

def format_table(table, indent=0):
    output = ""
    for key, value in table.items():
        if isinstance(value, dict):
            output += " " * indent + key.capitalize() + ":\n"
            output += format_table(value, indent + 4)
        else:
            output += " " * indent + f"{key.capitalize()}: {value}\n"
    return output

def create_prompt(world, rules, player_action):
    name = world["name"]
    gov_type = world["government"]["type"]
    era = world["era"]
    pop = world["population"]
    resources = format_table(world["resources"])
    military = format_table(world["military"])
    modifiers = format_table(world["modifiers"])
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
                    "content": GLOBAL_RULESET
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "think": True,
            "stream": True,
            "keep_alive": "30m"
        },
    )

    started_content = False

    for line in response.iter_lines():
        if not line:
            continue

        chunk = json.loads(line)
        message = chunk.get("message", {})
        thinking = message.get("thinking", "")
        content = message.get("content", "")

        if thinking and DEBUG:
            print(thinking, end="", flush=True)

        if content:
            if not started_content:
                print("\n\n=== NARRATOR RESPONSE ===")
                started_content = True

            print(content, end="", flush=True)

def game_loop():
    while True:
        player_action = input("\n> ")

        prompt = create_prompt(
            gamestate,
            GLOBAL_RULESET,
            player_action
        )

        send_prompt(prompt)

game_loop()

input() #temp
