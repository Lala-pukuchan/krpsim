class Optimize:
    def __init__(self, goals, final_product=None):
        self.goals = goals
        for goal in goals:
            if goal != "time":
                self.final_product = goal
