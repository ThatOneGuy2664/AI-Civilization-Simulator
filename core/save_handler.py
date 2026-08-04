from pathlib import Path
import json
import sys
import os

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

GAMESTATE_DIR = "gamestate"

def save_game(gamestate):
    path = os.path.join(
        GAMESTATE_DIR,
        gamestate["name"].lower() + ".json"
    )

    if gamestate["new_game"]:
        gamestate["new_game"] = False

    with open(path, "w", encoding="utf-8") as file:
        json.dump(gamestate, file, indent=4)
