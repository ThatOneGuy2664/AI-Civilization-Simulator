from core.save_handler import save_game

def gather_resource(gamestate, action):
    resource = action["resource"]
    labor = action["labor"]
    tool = action["tool"]

    errors = []

    if labor > gamestate["empire_population"]:
        errors.append("insufficient_population")

    if resource not in gamestate["resources"]:
        errors.append("unknown_resource")

    if errors:
        return {
            "success": False,
            "action": "gather",
            "resource": resource,
            "errors": errors,
        }

    gathered = labor * 3 #temp, add sim logic
    gamestate["resources"][resource] += gathered

    save_game(gamestate)

    return f"""
        outcome: success;
        workers: {labor};
        tool(s) used: {tool};
        food gathered: {gathered};
    """

HANDLERS = {
    "gather_resource": gather_resource
}
