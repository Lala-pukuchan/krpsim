class Stock:
    def __init__(self):
        self.resources = {}

    def add_resource(self, name, quantity):
        self.resources[name] = quantity
