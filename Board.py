import Enums
from Data import ShotOutcome
from Ship import Ship

class Board:
    Columns:int
    Rows:int
    Ships:list
    ShotPositions:set

    def __init__(self,columns:int,rows:int):
        self.Columns = columns
        self.Rows = rows
        self.Ships = []
        self.ShotPositions = set()

    def receiveShot(self,coordinate:tuple)->ShotOutcome:
        if self.hasBeenShot(coordinate):
            return ShotOutcome(Enums.ShotResult.AlreadyShot,None)
        ship=self.findShipAt(coordinate)
        self.ShotPositions.add(coordinate)
        if ship is not None:
            ship.hit(coordinate)
            if ship.hasSunken():
                return ShotOutcome(Enums.ShotResult.Sunken,ship)
            else:
                return ShotOutcome(Enums.ShotResult.Hit,None)
        else:
            return ShotOutcome(Enums.ShotResult.Water, None)

    def allShipsSunk(self)->bool:
        for ship in self.Ships:
            if not ship.hasSunken():
                return False
        return True

    def hasBeenShot(self,coordinate:tuple)->bool:
        for position in self.ShotPositions:
            if coordinate == position:
                return True
        return False

    def placeShip(self,orientation:Enums.Orientation,coordinate:tuple,ship:Ship) -> bool:
        # horizontal: Koordinate ist immer links vom Schiff.
        # vertikal: Koordinate ist immer oben vom Schiff.

        # 1. Positionen berechnen.
        # 2. Prüfen, ob schiff so platziert werden darf.
        # 3. Schiff die Positionen zuweisen und True zurückgeben.

        if orientation is Enums.Orientation.Horizontal:
            start = coordinate[1]
        elif orientation is Enums.Orientation.Vertical:
            start = coordinate[0]
        else:
            return False

        end = start + ship.Size
        shipPositions=self.calculatePositions(start,end,coordinate,orientation)

        if self.canPlaceShip(orientation,shipPositions,end):
            ship.Positions = shipPositions
            self.Ships.append(ship)
            return True
        return False

    def canPlaceShip(self,orientation,positions, end)->bool:
        if orientation == Enums.Orientation.Horizontal:
            if end > self.Columns:
                # Schiff würde über die Kante des Boards ragen.
                return False

        elif orientation == Enums.Orientation.Vertical:
            if end > self.Rows:
                # Schiff würde über die Kante des Boards ragen.
                return False
        else:
            return False

        # Kollision mit anderen Schiffen prüfen
        if self.hasCollision(positions):
            return False
        return True

    def findShipAt(self,coordinate:tuple)->Ship | None:
        for ship in self.Ships:
            if ship.hasPosition(coordinate):
                return ship
        return None

    def hasCollision(self, newShipPositions:set)->bool:
        for ship in self.Ships:
            for position in newShipPositions:
                if position in ship.Positions:
                    return True
        return False

    @staticmethod
    def calculatePositions(start, end, coordinate, orientation:Enums.Orientation)->set:
        shipPositions = set()
        for position in range(start,end):
            if orientation == Enums.Orientation.Horizontal:
                shipPositions.add((coordinate[0], position))
            elif orientation == Enums.Orientation.Vertical:
                shipPositions.add((position, coordinate[1]))
        return shipPositions