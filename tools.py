import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GAMESTATE_DIR = os.path.join(SCRIPT_DIR, "gamestate")

def rename_empire(NEW_NAME):
    civ_type = ""
    # read civ name for file to change
    FILE_PATH = os.path.join(GAMESTATE_DIR, "THE-SAVE-FILE")
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("TYPE:"):
                    civ_type = line.replace("TYPE:", "").strip()
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        file.write("NAME:" + NEW_NAME + "\n")
        file.write("TYPE:" + civ_type + "\n")