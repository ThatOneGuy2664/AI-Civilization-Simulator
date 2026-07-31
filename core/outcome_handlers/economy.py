from core.save_handler import save_game

def gather_resource(gamestate, action):
    resource = action["resource"]
    labor = action["labor"]
    tool = action["tool"]

    gathered = labor * 3 #temp, add sim logic
    gamestate["resources"][resource] += gathered

    if labor > gamestate["empire_population"]:
        return "Not enough population"

    if resource not in gamestate["resources"]:
        return "Unknown resource"

    save_game(gamestate)

    return f"""
        outcome: success;
        workers: {labor};
        tool(s) used: {tool};
        food gathered: {gathered}
    """

HANDLERS = {
    "gather_resource": gather_resource
}
