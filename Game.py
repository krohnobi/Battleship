import random
from Board import Board
import Enums
from Data import ShotOutcome
from Ship import Ship



class Game:
    Boards:dict
    RemainingShipsToPlace:dict
    CurrentPlayer:Enums.Player

    def __init__(self):
        self.Boards = {
            Enums.Player.One: Board(10, 10),
            Enums.Player.Two: Board(10, 10)
        }
        self.RemainingShipsToPlace = {
            Enums.Player.One: self.createFleet(),
            Enums.Player.Two: self.createFleet(),
        }

        self.CurrentPlayer = random.choice(list(Enums.Player))

    def placeNextShip(self,player:Enums.Player,orientation:Enums.Orientation,coordinate:tuple)->bool:
        ship = self.getNextShip(player)
        if ship is None:
            return False
        success=self.Boards[player].placeShip(orientation,coordinate,ship)
        if not success:
            return False

        self.RemainingShipsToPlace[player].pop(0)
        return True

    def placeShip(self,player:Enums.Player,ship:Ship,orientation:Enums.Orientation,coordinate:tuple)->bool:
        success=self.Boards[player].placeShip(orientation,coordinate,ship)
        if success:
            self.RemainingShipsToPlace[player].remove(ship)

        return success

    def getNextShip(self,player:Enums.Player)->Ship | None:
        if not self.RemainingShipsToPlace[player]:
            return None
        return self.RemainingShipsToPlace[player][0]

    def isPlacementFinished(self)->bool:
        # wir nehmen nur des Values aus dem dictionary, die keys (player) brauchen wir nicht
        for remainingShip in self.RemainingShipsToPlace.values():
            if remainingShip:
                return False
        return True

    def randomShipPlacement(self,player:Enums.Player):
        while self.RemainingShipsToPlace[player]:
            randRow = random.randint(0, 9)
            randCol = random.randint(0, 9)
            randOrientation = random.choice(list(Enums.Orientation))
            self.placeNextShip(player,randOrientation,(randRow,randCol))

    def getOpponent(self):
        if self.CurrentPlayer == Enums.Player.One:
            return Enums.Player.Two
        if self.CurrentPlayer == Enums.Player.Two:
            return Enums.Player.One
        raise Exception("Unknown opponent.")


    def shoot(self,targetCoordinate:tuple)->ShotOutcome:
        targetBoard = self.Boards[self.getOpponent()]
        response=targetBoard.receiveShot(targetCoordinate)

        if response.ShotResult is Enums.ShotResult.AlreadyShot:
            return response

        self.CurrentPlayer = self.getOpponent()
        return response

    def getWinner(self) -> Enums.Player | None:
        for player,board in self.Boards.items():
            if board.allShipsSunk():
                match player:
                    case Enums.Player.One:
                        return Enums.Player.Two
                    case Enums.Player.Two:
                        return Enums.Player.One
        return None



    @staticmethod
    def createFleet():
        ships = [
            Ship("Carrier", 5),
            Ship("Battleship", 4),
            Ship("Cruiser", 3),
            Ship("Submarine", 3),
            Ship("Destroyer", 2),
        ]
        return ships





