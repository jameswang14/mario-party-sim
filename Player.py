class Player(object):
    def __init__(self, skill, strat_bonus=0.0, ident=0):
        self.reset()
        self.skill = skill
        self.strat_bonus = 1.0+strat_bonus
        self.wins = 0
        self.id = ident
    def __str__(self):
        return "Stars: {}, Coins: {}, Skill: {}".format(self.stars, self.coins, self.skill)
    def reset(self):
        self.coins = 10 
        self.spaces_moved = 0
        self.items_used = 0
        self.green = 0
        self.red = 0
        self.coins_spent = 0
        self.spaces_from_star = 0
        self.stars = 0
        self.items = 0
        self.minigames_won = 0
        
