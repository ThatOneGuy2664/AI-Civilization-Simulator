from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
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

class Sidebar(VerticalScroll):
    def compose(self):
        yield Static(id="sidebar_text")

    def update_stats(self):
        gamestate = self.app.game.gamestate

        self.query_one("#sidebar_text", Static).update(
            f"""Population: {gamestate["empire_population"]}
Food: {gamestate["resources"]["food"]}
Wood: {gamestate["resources"]["wood"]}
Stone: {gamestate["resources"]["stone"]}"""
        )

    def on_mount(self):
        self.update_stats()

class Header(Static):
    pass

class Narrative(VerticalScroll):
    def compose(self):
        yield Static(id="narrative_text")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loading_frames = [
            "Generating Opening |",
            "Generating Opening /",
            "Generating Opening -",
            "Generating Opening \\"
        ]
        self.loading_index = 0
        self.loading = False
        self.loading_timer = None
        self.lines = [""]
        self.new_message = False

    def on_mount(self):
        self.refresh_text()

    def refresh_text(self):
        self.query_one("#narrative_text", Static).update(
            "\n\n".join(self.lines)
        )
        self.scroll_end(animate=False)

    def add_message(self, text):
        self.lines.append(text)
        self.refresh_text()

    def add_command(self, command):
        self.lines.append(f"> {command}")
        self.lines.append("")
        self.new_message = True
        self.refresh_text()

    def append(self, text):
        if self.new_message:
            self.lines[-1] = text
            self.new_message = False
        else:
            self.lines[-1] += text

        self.refresh_text()

    def start_loading(self):
        self.loading_active = True
        self.loading_index = 0

        self.lines.append(
            self.loading_frames[self.loading_index]
        )
        self.refresh_text()

        self.loading_timer = self.set_interval(
            0.5,
            self.update_loading
        )

    def update_loading(self):
        if not self.loading_active:
            return

        self.lines[-1] = self.loading_frames[self.loading_index]
        self.loading_index = (
            self.loading_index + 1
        ) % len(self.loading_frames)

        self.refresh_text()

    def stop_loading(self):
        self.loading_active = False

        if self.loading_timer:
            self.loading_timer.stop()

        if self.lines[-1].startswith("Generating Opening"):
            self.lines.pop()

        self.refresh_text()

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

    def on_mount(self):
        if self.savedata["new_game"]:
            self.start_intro()

    def start_intro(self):
        command = self.query_one("#command", Input)
        command.disabled = True
        narrative = self.query_one("#narrative", Narrative)
        narrative.start_loading()

        self.run_worker(
            self.stream_intro,
            exclusive=True,
            thread=True,
        )

    def stream_intro(self):
        narrative = self.query_one("#narrative", Narrative)

        for chunk in self.generate_intro():
            if narrative.loading_active:
                narrative.stop_loading()

            self.call_from_thread(
                narrative.append,
                chunk
            )

        self.call_from_thread(self.finish_intro)

    def generate_intro(self):
        return self.game.process_turn(None, True)

    def finish_intro(self):
        command = self.query_one("#command", Input)
        command.disabled = False
        command.focus()
        narrative = self.query_one("#narrative", Narrative)
        narrative.add_message("The Empire awaits your command...")

    @property
    def wartimestr(self):
        return "AT WAR" if self.savedata["wartime"] else "AT PEACE"

    @property
    def simTimeYr(self):
        calculated_year = math.floor(self.savedata["day"] / 365)
        return max(calculated_year, 1)

    @property
    def dayNumber(self):
        day = self.savedata['day'] - (self.simTimeYr * 365)
        if day < 1:
            return 1
        else:
            return day

    def compose(self):
        yield Header(
            f"{self.savedata['name']} {self.savedata['government']['type']} | "
            f"Day {self.dayNumber} of Year {self.simTimeYr} | {self.wartimestr}",
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

        self.call_from_thread(
            self.query_one("#sidebar", Sidebar).update_stats
        )
        #self.call_from_thread(self.refresh_ui) - refresh ALL ui besides Narrative
