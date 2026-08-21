import json

class Validator():
    def get_registry():
        with open("data/actions/action_registry.json", "r", encoding="utf-8") as file:
            return json.load(file)

    actions = get_registry()

    def validate_schema(schema):
        return True, None
