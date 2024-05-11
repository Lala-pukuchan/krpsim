class Stock:
    def __init__(self):
        self.resources = {}
        self.raw_materials = []

    def add_resource(self, name, quantity):
        self.resources[name] = quantity

    def add_raw_material(self, name):
        self.raw_materials.append(name)
