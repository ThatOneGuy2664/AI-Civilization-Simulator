from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Static, Input
from textual.containers import Horizontal, Vertical
from textual.widgets import Input
from functools import partial
from textual.worker import get_current_worker
import sys
import math

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.gameloop import Game

UI_DIR = Path(__file__).resolve().parent

# Console theme assignment
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

class Header(Static):
    pass

class Narrative(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.buffer = "The empire awaits your decree..."
        self.new_message = True

    def add_command(self, command):
        self.buffer += f"\n\n> {command}\n\n"
        self.new_message = True
        self.update(self.buffer)

    def append(self, text):
        if self.new_message:
            self.buffer += text
            self.new_message = False
        else:
            self.buffer += text

        self.update(self.buffer)

class GameUI(App):
    def __init__(self, savedata, **kwargs):
        self.game = Game(savedata)
        self.savedata = savedata

        era = savedata["era"]
        theme_file = ERA_TO_THEME.get(era, "stone.tcss")

        super().__init__(
            css_path=[
                UI_DIR / "layout.tcss",
                UI_DIR / "ui_themes" / theme_file,
            ],
            **kwargs,
        )

    @property
    def wartimestr(self):
        return "AT WAR" if self.savedata["wartime"] else "AT PEACE"

    @property
    def simTimeYr(self):
        calculated_year = math.floor(self.savedata["day"] / 365)
        return max(calculated_year, 1)

    def compose(self):
        yield Header(
            f"{self.savedata['name']} {self.savedata['government']['type']} | "
            f"Day {self.savedata['day']} of Year {self.simTimeYr} | {self.wartimestr}",
            id="header",
        )

        with Horizontal(id="main"):
            yield Sidebar(id="sidebar")
            yield Narrative(
                id="narrative",
            )

        yield Input(
            placeholder="Enter your decree...",
            id="command",
        )

    def on_input_submitted(self, event: Input.Submitted):
        command = event.value
        event.input.clear()

        self.run_worker(
            partial(self.stream_response, command),
            exclusive=True,
            thread=True,
        )

    def stream_response(self, command):
        narrative = self.query_one("#narrative", Narrative)
        self.call_from_thread(narrative.add_command, command)

        for chunk in self.game.process_turn(command):
            worker = get_current_worker()
            if worker.is_cancelled:
                return

            self.call_from_thread(narrative.append, chunk)
