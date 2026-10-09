import math
import random
from time import sleep
from tkinter import messagebox

import Game
import tkinter as tk

import Enums
import Theme
from Ship import Ship
from Game import Game

import sys
from pathlib import Path


def getResourcePath(fileName: str) -> str:
    # Als exe: PyInstaller legt die Dateien in einen temporären Ordner (_MEIPASS)
    # Als Skript: die Dateien liegen neben GameWindow.py
    if hasattr(sys, "_MEIPASS"):
        baseFolder = Path(sys._MEIPASS)
    else:
        baseFolder = Path(__file__).parent

    fullPath = baseFolder / fileName
    return str(fullPath)

class GameWindow:
    BUTTON_SIZE = 60
    SHIP_ABBREVIATIONS = {
        "Carrier": "CV",
        "Battleship": "BB",
        "Cruiser": "CA",
        "Submarine": "SS",
        "Destroyer": "DD",
    }

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
        self.hit_frames = self.load_gif_frames(getResourcePath("animations/hit.gif"), self.BUTTON_SIZE * 2)
        self.water_frames = self.load_gif_frames(getResourcePath("animations/water-hit.gif"), self.BUTTON_SIZE * 2)

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

        self.hoveredCell = None
        self.previewPositions = set()
        # Linker Frame
        # knöpfe in der createGridFunktion muss noch angepasst werden
        self.playerGridButtons=self.createButtonGrid(self.frameLeft, self.onPlacementCellClicked)

        for coordinate, button in self.playerGridButtons.items():
            button.bind("<Enter>", lambda event, currentCoordinate=coordinate: self.onPlacementCellEnter(currentCoordinate))
            button.bind("<Leave>", lambda event: self.onPlacementCellLeave())

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

        self.root.bind("<KeyPress-r>", self.onRotateKeyPressed)
        self.root.bind("<KeyPress-R>", self.onRotateKeyPressed)

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
        self.showPlacementPreview()

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
        enemyBoardFrame = tk.Frame(self.frameRight)
        enemyBoardFrame.pack()
        self.enemyGridButtons=self.createButtonGrid(enemyBoardFrame, self.shot)

        self.enemyFleetFrame = tk.Frame(self.frameRight)
        self.enemyFleetFrame.pack(fill="x", pady=(10, 0))
        self.refreshEnemyFleet()
        self.playerFleetFrame = tk.Frame(self.frameLeft)
        self.playerFleetFrame.grid(row=10, column=0, columnspan=10, sticky="we", pady=(10, 0))
        self.refreshPlayerFleet()
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
                sunkShip = response.Ship
                self.play_gif(targetButton, True, self.hit_frames,
                              onFinished=lambda: self.markSunkShip(self.playerGridButtons, sunkShip))
                self.refreshPlayerFleet()
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

        # Dialog erst zeigen, wenn die letzte Animation sicher fertig ist
        longestAnimation = max(len(self.hit_frames), len(self.water_frames))
        delay = longestAnimation * 100 + 800
        self.root.after(delay, self.showGameOverDialog, winner)
        return True

    def showGameOverDialog(self, winner):
        if winner == Enums.Player.One:
            message = "Glückwunsch, du hast die gegnerische Flotte versenkt!\n\nNochmal spielen?"
        else:
            message = "Der Computer hat deine Flotte versenkt.\n\nNochmal spielen?"

        playAgain = messagebox.askyesno("Spiel vorbei", message)
        if playAgain:
            self.restartGame()
        else:
            self.root.destroy()

    def restartGame(self):
        self.game = Game()

        self.isPlacing = True
        self.isBattle = False
        self.selectedShip = None
        self.currentShipRotation = Enums.Orientation.Horizontal

        for element in self.frameLeft.winfo_children():
            element.destroy()
        for element in self.frameRight.winfo_children():
            element.destroy()

        self.placementView()
        self.updateNextShipLabel()
        self.updateStatusLabel("Neues Spiel: Platziere deine Flotte.")

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
        self.clearPlacementPreview()
        
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
        self.showPlacementPreview()

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
            sunkShip = response.Ship
            self.play_gif(clicked_button, True, self.hit_frames,
                          onFinished=lambda: self.markSunkShip(self.enemyGridButtons, sunkShip))
            self.refreshEnemyFleet()

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

    def play_gif(self,button,isHit,frames, frame_index=0, onFinished=None):
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

            if onFinished is not None:
                onFinished()
            return

        current_frame = frames[frame_index]
        button.config(image=current_frame)
        self.root.after(100,self.play_gif, button,isHit, frames, frame_index + 1, onFinished)

    def markSunkShip(self, gridButtons: dict, ship: Ship):
        abbreviation = self.SHIP_ABBREVIATIONS.get(ship.ShipType, "?")
        borderWidth = 3

        for position in ship.Positions:
            row, column = position
            button = gridButtons[position]

            button.config(
                image=self.empty_pixel,
                text=abbreviation,
                font=Theme.SUNK_FONT,
                bg=Theme.SUNK_COLOR,
                state="disabled",
                disabledforeground=Theme.SUNK_TEXT_COLOR
            )

            # Rand nur dort, wo das Nachbarfeld nicht mehr zum Schiff gehört
            hasNeighborAbove = (row - 1, column) in ship.Positions
            hasNeighborBelow = (row + 1, column) in ship.Positions
            hasNeighborLeft = (row, column - 1) in ship.Positions
            hasNeighborRight = (row, column + 1) in ship.Positions

            paddingTop = 0 if hasNeighborAbove else borderWidth
            paddingBottom = 0 if hasNeighborBelow else borderWidth
            paddingLeft = 0 if hasNeighborLeft else borderWidth
            paddingRight = 0 if hasNeighborRight else borderWidth

            cell = button.master
            cell.config(bg=Theme.SUNK_BORDER_COLOR)
            button.pack_configure(padx=(paddingLeft, paddingRight), pady=(paddingTop, paddingBottom))

    def refreshFleetStatus(self, fleetFrame: tk.Frame, player: Enums.Player, title: str):
        for element in fleetFrame.winfo_children():
            element.destroy()

        titleLabel = tk.Label(fleetFrame, text=title, fg=Theme.DIM_TEXT_COLOR, pady=2)
        titleLabel.pack(anchor="w")

        ships = self.game.Boards[player].Ships
        for ship in ships:
            abbreviation = self.SHIP_ABBREVIATIONS.get(ship.ShipType, "?")
            shipBlocks = "■ " * ship.Size

            if ship.hasSunken():
                text = f"{abbreviation}  {ship.ShipType:<11} {shipBlocks} versenkt"
                font = (Theme.FONT_FAMILY, 11, "overstrike")
                color = Theme.ERROR_COLOR
            else:
                text = f"{abbreviation}  {ship.ShipType:<11} {shipBlocks}"
                font = Theme.FONT
                color = Theme.TEXT_COLOR

            shipLabel = tk.Label(fleetFrame, text=text, font=font, fg=color, anchor="w", pady=1)
            shipLabel.pack(fill="x")

    def refreshEnemyFleet(self):
        self.refreshFleetStatus(self.enemyFleetFrame, Enums.Player.Two, "Gegnerische Flotte")

    def refreshPlayerFleet(self):
        self.refreshFleetStatus(self.playerFleetFrame, Enums.Player.One, "Deine Flotte")

    def onRotateKeyPressed(self, event):
        if not self.isPlacing:
            return
        self.toggleRotation()

    def onPlacementCellEnter(self, coordinate: tuple):
        self.hoveredCell = coordinate
        self.showPlacementPreview()

    def onPlacementCellLeave(self):
        self.hoveredCell = None
        self.clearPlacementPreview()

    def calculatePreviewPositions(self, coordinate: tuple, size: int) -> list:
        startRow, startColumn = coordinate
        positions = []

        for offset in range(size):
            if self.currentShipRotation == Enums.Orientation.Horizontal:
                position = (startRow, startColumn + offset)
            else:
                position = (startRow + offset, startColumn)
            positions.append(position)

        return positions

    def showPlacementPreview(self):
        self.clearPlacementPreview()

        if not self.isPlacing or self.selectedShip is None or self.hoveredCell is None:
            return

        allPositions = self.calculatePreviewPositions(self.hoveredCell, self.selectedShip.Size)

        positionsOnBoard = set()
        for position in allPositions:
            if position in self.playerGridButtons:
                positionsOnBoard.add(position)

        isInsideBoard = len(positionsOnBoard) == len(allPositions)
        playerBoard = self.game.Boards[Enums.Player.One]
        hasCollision = playerBoard.hasCollision(positionsOnBoard)

        if isInsideBoard and not hasCollision:
            previewColor = Theme.PREVIEW_VALID_COLOR
        else:
            previewColor = Theme.PREVIEW_INVALID_COLOR

        for position in positionsOnBoard:
            self.playerGridButtons[position].config(bg=previewColor)

        self.previewPositions = positionsOnBoard

    def clearPlacementPreview(self):
        playerBoard = self.game.Boards[Enums.Player.One]

        for position in self.previewPositions:
            button = self.playerGridButtons[position]
            if playerBoard.findShipAt(position) is None:
                button.config(bg=Theme.WATER_COLOR)
            else:
                button.config(bg=Theme.SHIP_COLOR)

        self.previewPositions = set()

start = GameWindow()