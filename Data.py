from dataclasses import dataclass
import Enums
from Ship import Ship

@dataclass
class ShotOutcome:
    ShotResult:Enums.ShotResult
    Ship:Ship|None