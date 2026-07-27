from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Static, Input
from textual.containers import Horizontal, Vertical

UI_DIR = Path(__file__).resolve().parent

ERA_TO_THEME = {
    "Stone Age": "stone.tcss",
    "Bronze Age": "bronze.tcss",
    "Medieval": "medieval.tcss",
    "Industrial": "industrial.tcss",
    "Space Age": "starship.tcss",
}

class Sidebar(Static): # Change these values to actually mean something
    def compose(self) -> ComposeResult:
        yield Static("Population: 1200")
        yield Static("Food: Plenty")
        yield Static("Wood: Alright")
        yield Static("Stone: Pretty Low")

class Narrative(Static):
    pass

class GameUI(App):
    def __init__(self, era: str, **kwargs):
        theme_file = ERA_TO_THEME.get(era, "stone.tcss")
        super().__init__(
            css_path=[UI_DIR / "layout.tcss", UI_DIR / "themes" / theme_file],
            **kwargs,
        )

    def compose(self) -> ComposeResult:
        with Horizontal(id="main"):
            yield Sidebar()
            yield Narrative("EMPIRE NAME | 316TH DAY OF YEAR 10293 | AT PEACE")

        yield Input(
            placeholder="Enter your decree..."
        )

if __name__ == "__main__":
    GameUI("Industrial").run()
