import sys
import os
import json
import math
import requests
import random

random.seed(os.urandom(8)) # Force random seed using hardware noise

# Wrap this in a flag to see if it is the first time running OR if Ollama is already installed
#if input("PLEASE READ CAREFULLY:\n\nThis game requires a locally-hosted AI LLM to run. If you have your own then in the game directory open the game_properties.py file and change the 'AI-model' to your local model's id. If you do NOT have your own model and would like this program to install and set one up for you using Ollama, reply YES (estimated size 9.3GB).\n").lower() != "yes":
#    sys.exit()
#else:
#    print("\n\n\n")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GAMESTATE_DIR = os.path.join(SCRIPT_DIR, "gamestate")

CIV_NAME = ""
CIV_TYPE = ""
STARTING_AGE = "Stone Age" # options later
STARTING_POPULATION = 700
STARTING_RESOURCE_MULT = 1
STARTING_RESOURCES = {
    "wood": 500,
    "food": 500,
    "stone": 200
}

# difficulty changes here

gamestate = {}

RESOURCES = {key: value * STARTING_RESOURCE_MULT for key, value in STARTING_RESOURCES.items()}
STARTING_ARMY = math.floor(STARTING_POPULATION / 10)
STARTING_MILITA = math.floor((STARTING_POPULATION / 3) * 2)

def get_starting_neighbors():
    with open("data/locations/starting.json", "r", encoding="utf-8") as file:
        possible_neighbors = json.load(file)

    selected_keys = random.sample(list(possible_neighbors.keys()), 3)

    neighbors = {
        key: possible_neighbors[key]
        for key in selected_keys
    }

    return neighbors

# If new empire
def init_new_empire():
    name = input("What is your empire called?\n")
    capital_name = input("What is the name of " + name + "'s capital city?\n")
    gov_type = input("What kind of government does " + name + " have?\n")

    gamestate = {
        "name": name,
        "government": {
            "type": gov_type
        },
        "era": STARTING_AGE,
        "empire_population": STARTING_POPULATION,
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
        "history": [],
        "wartime": False,
        "day": 1,
        "settlements": {
            "capital": {
                "population": STARTING_POPULATION,
                "key_buildings": {
                    "town_hall": {
                        "type": "government",
                        "bonus": "morale"
                    }
                },
                "name": capital_name,
                "neighbors": get_starting_neighbors()
            }
        },
        "new_game": True
    }

    os.makedirs(GAMESTATE_DIR, exist_ok=True)
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

print("\nLoading game...")

from ui.ui_init import GameUI
app = GameUI(gamestate)
app.run()
