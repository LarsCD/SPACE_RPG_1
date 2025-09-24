from source.classes.ship.ship_class import Ship


class Player(Ship):
    def __init__(self, data):
        super().__init__(data)