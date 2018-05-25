import math
import numpy as np

def random_exponential(x, l):
    return -math.log(1-x) / (l)

def players_win_pct_4way(players):
    return [float("{0:.3f}".format(x[0] / sum([x[0] for x in players]))) for x in players]