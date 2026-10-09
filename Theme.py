import math
import tkinter as tk

# ---------------------------------------------------------------
# Farben (Radar-Konsole)
# ---------------------------------------------------------------
BACKGROUND_COLOR = "#06110d"      # Fensterhintergrund
PANEL_COLOR = "#0c1f17"           # Hintergrund der Bereiche (Frames, Statusleiste)
BORDER_COLOR = "#1f6b45"          # Rahmen um die Bereiche

TEXT_COLOR = "#b8f5cf"            # normaler Text
DIM_TEXT_COLOR = "#5f9c7a"        # Untertitel, Nebeninfos
ACCENT_COLOR = "#3ddc84"          # Überschriften, Hervorhebungen

BUTTON_COLOR = "#123a2a"          # normale Buttons (rechte Leiste)
BUTTON_ACTIVE_COLOR = "#1d5a40"   # Button beim Draufklicken

WATER_COLOR = "#0f3a4c"           # leeres Feld
SHIP_COLOR = "#6c7a80"            # eigenes Schiff
HIT_COLOR = "#d7263d"             # Treffer
HIT_TEXT_COLOR = "#ffffff"        # das X auf einem Treffer
MISS_TEXT_COLOR = "#9fd8ef"       # das O bei einem Fehlschuss
SUNK_BORDER_COLOR = "#ff5c6c"     # Rahmen um ein versenktes Schiff
SUNK_COLOR = "#6b1020"            # Felder eines versenkten Schiffs
SUNK_TEXT_COLOR = "#ff9aa5"       # Kürzel auf einem versenkten Schiff

SUCCESS_COLOR = "#3ddc84"         # Statusmeldung: hat geklappt
WARNING_COLOR = "#ffd166"         # Statusmeldung: Hinweis
ERROR_COLOR = "#ff5c6c"           # Statusmeldung: Fehler, eigenes Schiff getroffen

RADAR_GRID_COLOR = "#0b2219"      # Gitterlinien im Hintergrund
RADAR_RING_COLOR = "#14412d"      # Radarkreise
RADAR_SWEEP_COLOR = "#0e2e20"     # der drehende Radarstrahl
RADAR_LINE_COLOR = "#2a8f5c"      # Vorderkante des Radarstrahls

PREVIEW_VALID_COLOR = "#2f9e5f"   # Vorschau: Schiff passt hier
PREVIEW_INVALID_COLOR = "#a83a45" # Vorschau: Schiff passt hier nicht


# ---------------------------------------------------------------
# Schriften
# ---------------------------------------------------------------
FONT_FAMILY = "Consolas"
FONT = (FONT_FAMILY, 11)
TITLE_FONT = (FONT_FAMILY, 12, "bold")
HEADER_FONT = (FONT_FAMILY, 24, "bold")
SUBTITLE_FONT = (FONT_FAMILY, 10)
MARK_FONT = (FONT_FAMILY, 18, "bold")

SUNK_FONT = (FONT_FAMILY, 14, "bold")

# ---------------------------------------------------------------
# Radar-Hintergrund
# ---------------------------------------------------------------
RADAR_GRID_SPACING = 40           # Abstand der Gitterlinien in Pixeln
RADAR_RING_COUNT = 6              # Anzahl der Radarkreise
RADAR_SWEEP_WIDTH = 30            # Breite des Radarstrahls in Grad
RADAR_SWEEP_STEP = 2              # Drehung pro Animationsschritt in Grad
RADAR_SWEEP_DELAY = 40            # Millisekunden zwischen zwei Schritten


def applyTheme(root: tk.Tk):
    # Wird einmal direkt nach tk.Tk() aufgerufen.
    root.title("Battleship")
    root.configure(bg=BACKGROUND_COLOR)

    setDefaultStyles(root)
    RadarBackground(root)
    createHeader(root)


def setDefaultStyles(root: tk.Tk):
    # Standardwerte für alle Widgets, die danach erstellt werden.
    # Was im Code direkt gesetzt wird (z. B. bg=...), hat Vorrang.
    root.option_add("*Font", FONT)
    root.option_add("*Foreground", TEXT_COLOR)

    root.option_add("*Frame.Background", PANEL_COLOR)

    root.option_add("*Label.Background", PANEL_COLOR)
    root.option_add("*Label.Foreground", TEXT_COLOR)
    root.option_add("*Label.padX", 8)
    root.option_add("*Label.padY", 6)

    root.option_add("*Button.Background", BUTTON_COLOR)
    root.option_add("*Button.Foreground", TEXT_COLOR)
    root.option_add("*Button.activeBackground", BUTTON_ACTIVE_COLOR)
    root.option_add("*Button.activeForeground", TEXT_COLOR)
    root.option_add("*Button.relief", "flat")
    root.option_add("*Button.borderWidth", 0)
    root.option_add("*Button.highlightThickness", 0)
    root.option_add("*Button.padX", 12)
    root.option_add("*Button.padY", 5)
    root.option_add("*Button.cursor", "hand2")


def createHeader(root: tk.Tk):
    title = tk.Label(
        root,
        text="⚓  B A T T L E S H I P",
        font=HEADER_FONT,
        fg=ACCENT_COLOR,
        bg=BACKGROUND_COLOR
    )
    title.pack(side="top", pady=(18, 0))

    subtitle = tk.Label(
        root,
        text="Radar-Konsole  ·  Flotte bereitmachen, Feuer frei",
        font=SUBTITLE_FONT,
        fg=DIM_TEXT_COLOR,
        bg=BACKGROUND_COLOR
    )
    subtitle.pack(side="top", pady=(0, 10))


def styleArea(frame: tk.Frame):
    # Gibt einem Bereich (linkes/rechtes Feld) einen Rahmen und Innenabstand.
    frame.config(
        highlightthickness=1,
        highlightbackground=BORDER_COLOR,
        highlightcolor=BORDER_COLOR,
        padx=10,
        pady=10
    )


class RadarBackground:
    # Zeichnet einen Radarschirm mit drehendem Strahl hinter das ganze Fenster.

    def __init__(self, root: tk.Tk):
        self.canvas = tk.Canvas(root, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Canvas.lower() verschiebt nur Zeichen-Elemente. Damit das ganze
        # Canvas hinter alle anderen Widgets rutscht, wird die Methode von
        # tk.Misc verwendet.
        tk.Misc.lower(self.canvas)

        self.sweepAngle = 90
        self.canvas.bind("<Configure>", self.onResize)
        self.animateSweep()

    def onResize(self, event):
        self.drawStaticElements()

    def getCenter(self) -> tuple:
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        centerX = width // 2
        centerY = height // 2
        return (centerX, centerY)

    def getRadius(self) -> int:
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        diagonal = math.hypot(width, height)
        return int(diagonal / 2)

    def drawStaticElements(self):
        self.canvas.delete("static")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        centerX, centerY = self.getCenter()
        maxRadius = self.getRadius()

        for x in range(0, width, RADAR_GRID_SPACING):
            self.canvas.create_line(x, 0, x, height, fill=RADAR_GRID_COLOR, tags="static")
        for y in range(0, height, RADAR_GRID_SPACING):
            self.canvas.create_line(0, y, width, y, fill=RADAR_GRID_COLOR, tags="static")

        for ringNumber in range(1, RADAR_RING_COUNT + 1):
            radius = maxRadius * ringNumber / RADAR_RING_COUNT
            self.canvas.create_oval(
                centerX - radius, centerY - radius,
                centerX + radius, centerY + radius,
                outline=RADAR_RING_COLOR,
                tags="static"
            )

        self.canvas.create_line(centerX, 0, centerX, height, fill=RADAR_RING_COLOR, tags="static")
        self.canvas.create_line(0, centerY, width, centerY, fill=RADAR_RING_COLOR, tags="static")

        self.canvas.tag_raise("static")

    def animateSweep(self):
        self.canvas.delete("sweep")

        centerX, centerY = self.getCenter()
        radius = self.getRadius()

        self.canvas.create_arc(
            centerX - radius, centerY - radius,
            centerX + radius, centerY + radius,
            start=self.sweepAngle,
            extent=RADAR_SWEEP_WIDTH,
            style=tk.PIESLICE,
            fill=RADAR_SWEEP_COLOR,
            outline="",
            tags="sweep"
        )

        angleInRadians = math.radians(self.sweepAngle)
        lineEndX = centerX + radius * math.cos(angleInRadians)
        lineEndY = centerY - radius * math.sin(angleInRadians)
        self.canvas.create_line(
            centerX, centerY, lineEndX, lineEndY,
            fill=RADAR_LINE_COLOR,
            width=2,
            tags="sweep"
        )

        # Gitter und Kreise bleiben über dem Strahl sichtbar.
        self.canvas.tag_raise("static")

        self.sweepAngle = (self.sweepAngle - RADAR_SWEEP_STEP) % 360
        self.canvas.after(RADAR_SWEEP_DELAY, self.animateSweep)
