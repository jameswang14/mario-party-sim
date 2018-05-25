import math
import numpy as np
import matplotlib.pyplot as plt

def random_exponential(x, l):
    return -math.log(1-x) / (l)

def scale(players, target):
    m = 0.0
    for p in players:
        if p.win_pct > m:
            m = p.win_pct
    return {}

def test():
    x = np.arange(2, 100)
    p = [random_exponential(random(), 1) for i in x]
    plt.plot(x, p)
    plt.show()
test()