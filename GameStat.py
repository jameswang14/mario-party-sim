class GameStat(object):
    def __init__(self):
        self.num_games = 0
        self.stats = {}

    def inc(self, key, amt=1):
        if key not in self.stats:
            self.stats[key] = 0
        self.stats[key] += amt
    def dec (self, key, amt):
        if key not in self.stats:
            self.stats[key] = 0
        self.stats[key] -= amt

    def print_stats(self):
        for k,v in self.stats.items():
            print("{}: {}".format(k, v))
    def print_stats_avg(self):
        for k,v in self.stats.items():
            print("{}: {}".format(k, v/self.num_games))


