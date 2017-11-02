from Framework.apps.ambient.clock import Clock
from Framework.apps.ambient.GameOfLife import GameOfLife
from Framework.apps.ambient.dots import Dots
from Framework.apps.ambient.audio import Audio

apps = {
    "Audio": Audio,
    "Clock": Clock,
    "GOL": GameOfLife,
    "Dots": Dots
}

standby_apps = [
    Clock,
    GameOfLife,
    Dots
]
