class Game:
    def __init__(self, savedata):
        self.gamestate = savedata

    def process_turn(self, player_action):
        prompt = create_prompt(
            self.gamestate,
            SYSTEM_INSTRUCTIONS,
            player_action,
        )

        return send_prompt(prompt)
