class Process:
    def __init__(self, name, needs, results, delay):
        self.name = name
        self.needs = needs
        self.results = results
        self.delay = delay
        self.start_time = 0
        self.end_time = 0
        self.priority = 0
