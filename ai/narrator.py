# This is what the AI's base ruleset is
SYSTEM_INSTRUCTIONS = """
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
                    "content": SYSTEM_INSTRUCTIONS,
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
