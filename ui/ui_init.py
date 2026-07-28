from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Static, Input
from textual.containers import Horizontal, Vertical
from textual.widgets import Input
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.gameloop import Game

UI_DIR = Path(__file__).resolve().parent

ERA_TO_THEME = {
    "Stone Age": "stone.tcss",
    "Bronze Age": "bronze.tcss",
    "Medieval": "medieval.tcss",
    "Industrial": "industrial.tcss",
    "Space Age": "starship.tcss",
}

class Sidebar(Static):
    def update_stats(self, gamestate):
        self.update(
            f"""
Population: {gamestate["population"]}

Food: {gamestate["resources"]["food"]}

Wood: {gamestate["resources"]["wood"]}

Stone: {gamestate["resources"]["stone"]}
"""
        )

class Narrative(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buffer = ""

    def append(self, text):
        self.buffer += text
        self.update(self.buffer)

    def clear(self):
        self.buffer = ""
        self.update("")

class GameUI(App):
    def __init__(self, savedata, **kwargs):
        self.game = Game(savedata)

        era = savedata["era"]
        theme_file = ERA_TO_THEME.get(era, "stone.tcss")

        super().__init__(
            css_path=[
                UI_DIR / "layout.tcss",
                UI_DIR / "ui_themes" / theme_file,
            ],
            **kwargs,
        )

        def compose(self):
            with Horizontal(id="main"):
                yield Sidebar(id="sidebar")
                yield Narrative(
                    "EMPIRE NAME | 316TH DAY OF YEAR 10293 | AT PEACE",
                    id="narrative",
                )

            yield Input(
                placeholder="Enter your decree...",
                id="command",
            )

            yield Footer()

        def on_input_submitted(self, event: Input.Submitted):
            command = event.value
            event.input.clear()

            self.run_worker(
                self.stream_response(command),
                exclusive=True,
            )

        async def stream_response(self, command):
            narrative = self.query_one(Narrative)
            narrative.clear()

            for chunk in self.game.process_turn(command):
                narrative.append(chunk)
