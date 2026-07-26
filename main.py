# Wrap this in a flag to see if it is the first time running OR if Ollama is already installed
if input("PLEASE READ CAREFULLY:\n\nThis game requires a locally-hosted AI LLM to run. If you have your own then in the game directory open the game.properties.json file and change the 'AI-model' to your local model's id. If you do NOT have your own model and would like this program to install and set one up for you using Ollama, reply YES (estimated size 9.3GB).\n").lower() != "yes":
    sys.exit
else:
    print("\n\n\n")

# Game Initalization:

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GAMESTATE_DIR = os.path.join(SCRIPT_DIR, "gamestate")

CIV_NAME = ""
CIV_TYPE = ""

# If new empire
def init_new_empire():
    name = input("What is your empire called?\n")
    gov_type = input("What kind of government does " + name + " have?\n")
    return name, gov_type

if CIV_NAME == "" and CIV_TYPE == "":
    CIV_NAME, CIV_TYPE = init_new_empire()

    with open(os.path.join(GAMESTATE_DIR, "empire.txt"), "a", encoding="utf-8") as file:
        file.write("NAME:" + CIV_NAME + "\nTYPE:" + CIV_TYPE + "\n")

if input("Does the empire of " + CIV_NAME + " with the " + CIV_TYPE + " government type look right? (Y/N)\n").lower() != "y":
    sys.exit()

input()