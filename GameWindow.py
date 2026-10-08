import math
import random
from time import sleep

import Game
import tkinter as tk

from Battleship import Enums
from Battleship import Theme
from Battleship.Ship import Ship
from Battleship.Game import Game


class GameWindow:
    BUTTON_SIZE = 60

    isPlacing:bool
    isBattle:bool


    # zum platzieren
    playerGridButtons={}
    # zum schießen
    enemyGridButtons={}
    currentShipRotation:Enums.Orientation
    selectedShip:Ship | None

    def __init__(self):
        self.game=Game()
        self.root=tk.Tk()
        Theme.applyTheme(self.root)

        self.empty_pixel = tk.PhotoImage(width=1, height=1)
        self.hit_frames = self.load_gif_frames("animations/hit.gif", self.BUTTON_SIZE * 2)
        self.water_frames = self.load_gif_frames("animations/water-hit.gif", self.BUTTON_SIZE * 2)

        self.isPlacing = True
        self.isBattle = False
        self.currentShipRotation = Enums.Orientation.Horizontal
        self.selectedShip = None

        self.statusLabel = tk.Label(self.root, text="")
        self.statusLabel.pack(side="bottom", fill="x", padx=24, pady=(0, 18))
        self.frameLeft = tk.Frame(self.root)
        Theme.styleArea(self.frameLeft)
        self.frameLeft.pack(side="left", padx=(24, 12), pady=12)
        self.frameRight = tk.Frame(self.root)
        Theme.styleArea(self.frameRight)
        self.frameRight.pack(side="right", padx=(12, 24), pady=12)

        self.placementView()

        tk.mainloop()

    def startBattle(self):
        if not self.isPlacing:
            self.game.randomShipPlacement(Enums.Player.Two)
            for element in self.frameRight.winfo_children():
                element.destroy()
            self.isBattle = True
            self.battleView()


        else:
            self.updateStatusLabel("Platzieren der Flotte noch nicht abgeschlossen!", Theme.ERROR_COLOR)

    def placementView(self):


        # Linker Frame
        # knöpfe in der createGridFunktion muss noch angepasst werden
        self.playerGridButtons=self.createButtonGrid(self.frameLeft, self.onPlacementCellClicked)

        # Rechter Frame
        self.nextShipLabel = tk.Label(self.frameRight, text="nächstes Schiff", font=Theme.TITLE_FONT, fg=Theme.ACCENT_COLOR)
        self.nextShipLabel.pack(pady=(0, 8))

        self.fleetLabel = tk.Label(self.frameRight, text="Flotte", fg=Theme.DIM_TEXT_COLOR)
        self.fleetFrame = tk.Frame(self.frameRight)
        self.fleetLabel.pack()
        self.fleetFrame.pack(fill="x", pady=(0, 12))

        self.refreshFleetList()

        self.rotateButton = tk.Button(self.frameRight, text="drehen (R)", command=self.toggleRotation)
        self.rotateButton.pack(fill="x", pady=3)

        self.randomButton = tk.Button(self.frameRight, text="zufällig platzieren",command=self.placeRandom)
        self.randomButton.pack(fill="x", pady=3)

        self.startGameButton = tk.Button(self.frameRight, text="spiel starten",command=self.startBattle, bg=Theme.ACCENT_COLOR, fg=Theme.BACKGROUND_COLOR)
        self.startGameButton.pack(fill="x", pady=(12, 3))

    def placeRandom(self):
        self.game.randomShipPlacement(Enums.Player.One)
        self.isPlacing = False
        self.selectedShip = None
        self.refreshFleetList()
        self.updateNextShipLabel()
        self.refreshPlayerBoard()


    def toggleRotation(self):
        if self.currentShipRotation == Enums.Orientation.Horizontal:
            self.currentShipRotation = Enums.Orientation.Vertical
            self.updateNextShipLabel()
        else:
            self.currentShipRotation = Enums.Orientation.Horizontal
            self.updateNextShipLabel()

    def refreshFleetList(self):
        for button in self.fleetFrame.winfo_children():
            button.destroy()
        for ship in self.game.RemainingShipsToPlace[Enums.Player.One]:
            tk.Button(self.fleetFrame, text=f"{ship.ShipType} ({ship.Size})", command=lambda x = ship: self.setSelectedShip(x)).pack(fill="x", pady=2)

    def setSelectedShip(self,ship):
        self.selectedShip = ship
        self.updateNextShipLabel()

    def updateNextShipLabel(self):
        if self.selectedShip is None:
            self.nextShipLabel.config(text="Schiff auswählen")
            return
        self.nextShipLabel.config(text=f"{self.selectedShip.ShipType} ({self.selectedShip.Size}), {self.currentShipRotation.name}")

    def battleView(self):
        self.enemyGridButtons=self.createButtonGrid(self.frameRight, self.shot)

        #linkes ButtonGrid: Klicks entfernen statt disablen (sonst werden die GIFs grau)
        for button in self.playerGridButtons.values():
            button.config(command="")

        if self.game.CurrentPlayer == Enums.Player.Two:
            self.updateStatusLabel("Computer beginnt.")
            self.root.after(2000,self.computerTurn)
        else:
            self.updateStatusLabel("Du bist dran.")


    def computerTurn(self):
        while True:
            coordinate = self.shootRand()
            response = self.game.shoot(coordinate)
            if response.ShotResult is Enums.ShotResult.AlreadyShot:
                continue

            targetButton = self.playerGridButtons[coordinate]

            if response.ShotResult is Enums.ShotResult.Sunken:
                self.updateStatusLabel(f"Dein {response.Ship.ShipType} ist gesunken! Du bist dran.", Theme.ERROR_COLOR)
                self.play_gif(targetButton,True,self.hit_frames)
            elif response.ShotResult is Enums.ShotResult.Hit:
                self.updateStatusLabel("Dein Schiff wurde getroffen! Du bist dran.", Theme.ERROR_COLOR)
                self.play_gif(targetButton,True,self.hit_frames)
            elif response.ShotResult is Enums.ShotResult.Water:
                self.updateStatusLabel("Der Computer hat ins Wasser geschossen. Du bist dran.")
                self.play_gif(targetButton,False, self.water_frames)

            break

        self.checkGameOver()

    # computer Hilfsfunktion
    def shootRand(self) -> tuple:
        randRow = random.randint(0, 9)
        randCol = random.randint(0, 9)

        return (randRow, randCol)

    def checkGameOver(self) -> bool:
        winner = self.game.getWinner()
        if winner is None:
            return False

        if winner == Enums.Player.One:
            self.updateStatusLabel("Du hast gewonnen!", Theme.SUCCESS_COLOR)
        else:
            self.updateStatusLabel("Der Computer hat gewonnen!", Theme.ERROR_COLOR)
        return True

    def updateStatusLabel(self,message:str,color:str=Theme.TEXT_COLOR):
        self.statusLabel.config(text=message,fg=color)

    def createButtonGrid(self,frame,clickHandler)->dict:
        gridButtons = {}
        for row in range(0, 10):
            for col in range(0, 10):
                cell = tk.Frame(frame, width=self.BUTTON_SIZE, height=self.BUTTON_SIZE)
                cell.grid(row=row, column=col, padx=1, pady=1)
                cell.pack_propagate(False)

                button = tk.Button(
                    cell,
                    text="",
                    image=self.empty_pixel,
                    compound="center",
                    bg=Theme.WATER_COLOR
                )

                if clickHandler is None:
                    button.config(state= "disabled",disabledforeground="white")
                else:
                    button.config(command=lambda current_row=row, current_column=col: clickHandler((current_row, current_column)))

                button.pack(fill="both", expand=True)
                gridButtons[(row, col)] = button
        return gridButtons

    def onPlacementCellClicked(self,coordinates:tuple):
        if self.selectedShip is None:
            self.updateStatusLabel("Kein Schiff ausgewählt!", Theme.ERROR_COLOR)
            return
        success = self.game.placeShip(Enums.Player.One, self.selectedShip, self.currentShipRotation, coordinates)
        if success:
            self.updateStatusLabel("erfolgreich platziert",Theme.SUCCESS_COLOR)
            self.selectedShip = None
            self.updateNextShipLabel()
            self.refreshFleetList()
            self.refreshPlayerBoard()
            if not self.game.RemainingShipsToPlace[Enums.Player.One]:
                self.isPlacing=False

        else:
            self.updateStatusLabel("Platzieren fehlgeschlagen!", Theme.ERROR_COLOR)

    def refreshPlayerBoard(self):
        for ship in self.game.Boards[Enums.Player.One].Ships:
            for position in ship.Positions:
                self.playerGridButtons[position].config(bg=Theme.SHIP_COLOR)


    def shot(self,coordinate: tuple):
        if self.game.CurrentPlayer == Enums.Player.Two:
            return
        if self.game.getWinner() is not None:
            return

        row, column = coordinate
        clicked_button = self.enemyGridButtons[coordinate]

        response=self.game.shoot(coordinate)

        if response.ShotResult is Enums.ShotResult.AlreadyShot:
            self.updateStatusLabel(f"Koordinaten bereits beschossen, neue wählen!", Theme.WARNING_COLOR)
            return

        clicked_button.config(command="")

        if response.ShotResult is Enums.ShotResult.Sunken:
            self.updateStatusLabel(f"Gegnerischer {response.Ship.ShipType} ist gesunken!", Theme.SUCCESS_COLOR)
            self.play_gif(clicked_button,True, self.hit_frames)
        elif response.ShotResult is Enums.ShotResult.Hit:
            self.updateStatusLabel(f"Gegnerisches Schiff getroffen!", Theme.SUCCESS_COLOR)
            self.play_gif(clicked_button,True, self.hit_frames)
        elif response.ShotResult is Enums.ShotResult.Water:
            self.updateStatusLabel(f"Wasser! Daneben.")
            self.play_gif(clicked_button, False,self.water_frames)

        if self.checkGameOver():
            return

        self.root.after(2000, self.computerTurn)

    def load_gif_frames(self,file_name, target_size):
        frames = []
        frame_index = 0

        while True:
            try:
                frame = tk.PhotoImage(file=file_name, format=f"gif -index {frame_index}")
            except tk.TclError:
                break

            largest_side = max(frame.width(), frame.height())
            shrink_factor = math.ceil(largest_side / target_size)

            if shrink_factor > 1:
                frame = frame.subsample(shrink_factor)

            frames.append(frame)
            frame_index += 1

        return frames

    def play_gif(self,button,isHit,frames, frame_index=0):
        button.config(state="normal")
        if frame_index == len(frames):
            button.config(
                image=self.empty_pixel,
                font=Theme.MARK_FONT,
                state="disabled"
            )
            if isHit:
                button.config(text="X",bg=Theme.HIT_COLOR,disabledforeground=Theme.HIT_TEXT_COLOR)
            else:
                button.config(text="O", bg=Theme.WATER_COLOR,disabledforeground=Theme.MISS_TEXT_COLOR)
            return

        current_frame = frames[frame_index]
        button.config(image=current_frame)
        self.root.after(100,self.play_gif, button,isHit, frames, frame_index + 1)

start = GameWindow()