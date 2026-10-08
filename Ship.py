class Ship:
    ShipType:str
    Size:int
    IsSunken:bool
    Positions:set
    HitPositions:set

    def __init__(self,shipType:str,size:int):
        self.ShipType = shipType
        self.Size=size
        self.Positions=set()
        self.HitPositions=set()
        self.IsSunken=False


    def hit(self,position:tuple):
        self.HitPositions.add(position)


    def hasPosition(self,position)->bool:
        if position in self.Positions:
            return True
        return False

    def hasSunken(self):
        if self.IsSunken:
            return True
        if set(self.HitPositions)==set(self.Positions):
            self.IsSunken=True
            return True
        return False


