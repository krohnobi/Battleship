from enum import Enum
class Orientation(Enum):
    Horizontal = 0
    Vertical = 1

class ShotResult(Enum):
    Water = 0
    Hit = 1
    Sunken = 2
    AlreadyShot = 3

class Player(Enum):
    One="Player One"
    Two="Player Two"