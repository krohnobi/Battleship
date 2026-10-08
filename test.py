import random
from time import sleep

from Battleship.Enums import Player, ShotResult
from Battleship.Game import Game

def shootRand()->tuple:
    randRow = random.randint(0, 9)
    randCol = random.randint(0, 9)

    return (randRow,randCol)

battleshipGame = Game()

battleshipGame.randomShipPlacement(Player.One)
battleshipGame.randomShipPlacement(Player.Two)

print(f"Platzierung abgeschlossen: {battleshipGame.isPlacementFinished()}.")




while(battleshipGame.getWinner() is None):
    if(battleshipGame.CurrentPlayer == Player.One):
        print("Sie sind am Zug.")

        while True:
            try:
                choice = int(input("Wählen, Zufällige Koordinaten (1) oder selber bestimmen (2)?:"))
            except ValueError:
                print("Ungültige Eingabe.")
                continue
            if(choice==1):
                coordinate=shootRand()
                break
            if(choice==2):
                while True:
                    try:
                        eingabe = input("Gib die Koordinaten ein (z.B. 5,3): ")
                        coordinate = tuple(int(x) for x in eingabe.split(","))
                        if len(coordinate) == 2 and 0 <= coordinate[0] <= 9 and 0 <= coordinate[1] <= 9:
                            break
                        print("Ungültige Koordinate.")
                    except ValueError:
                        print("Ungültige Koordinate.")

                break
            else:
                print("Ungültige Eingabe.")

        response=battleshipGame.shoot(coordinate)
        print(response.ShotResult.name)
        if response.ShotResult is ShotResult.AlreadyShot:
            continue
        if response.ShotResult is ShotResult.Sunken:
            print(f"{response.Ship.ShipType} vom Spieler {Player.Two.name} ist Gesunken!")
    else:
        print("Computer am Zug.")
        while True:
            coordinate=shootRand()
            response=battleshipGame.shoot(coordinate)
            if response.ShotResult is ShotResult.AlreadyShot:
                continue
            print(response.ShotResult.name)
            if response.ShotResult is ShotResult.Sunken:
                print(f"{response.Ship.ShipType} vom Spieler {Player.One.name} ist Gesunken!")
            break

    sleep(1)

winner = battleshipGame.getWinner()
print(f"Spieler {winner.name} hat gewonnen!")