import utils
import matplotlib.pyplot as plt
from GameStat import GameStat
from Game import Game

def win_pct_by_turn():
    n = 10000
    minigame_win_pcts = []
    win_pcts = []
    for i in range(0, 4):
        players = [(100, 0), (100, 0), (100, 0), (100, 0)]    
        players[i] = (0, 0)
        minigame_win_pcts.append([])
        win_pcts.append([])
        for skill in range(0, 101):
            players[i] = (skill, 0)
            minigame_win_pcts[i].append(utils.players_win_pct_4way(players)[i])
            win_pcts[i].append(trial(players, n)[i])
        for j in range(0, 4):
            if j == i: continue
            for skill in range(0, 101):
                players[j] = (100-skill, 0)
                minigame_win_pcts[i].append(utils.players_win_pct_4way(players)[i])
                win_pcts[i].append(trial(players, n)[i])

    print("done")
    for i in range(0, len(minigame_win_pcts)):
        plt.plot(minigame_win_pcts[i], win_pcts[i])
        plt.legend(['First', 'Second', 'Third', 'Fourth'])
    plt.title("Percent of Games Won Based on Minigame Win Percent and Turn Order")
    plt.xlabel("4-player Minigame Win Percent")
    plt.ylabel("Win Percent")
    plt.show()


def trial(players, n, gs=GameStat()):
    wins = [0,0,0,0]
    for x in range(0, n):
        g = Game(players, 15, stats=gs)
        g.run()
        wins[g.get_winner()] += 1
        gs.num_games += 1
    return [x/n for x in wins]

if __name__ == '__main__':
    win_pct_by_turn()
