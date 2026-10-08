from dataclasses import dataclass
from Battleship import Enums
from Battleship.Ship import Ship

@dataclass
class ShotOutcome:
    ShotResult:Enums.ShotResult
    Ship:Ship|None