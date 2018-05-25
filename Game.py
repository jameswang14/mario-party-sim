from Player import Player
from GameStat import GameStat
import random
import math

# Based on averages from 5 multiplayer boards in Mario Party 7 #
RED_PCT = 0.12524186787
GREEN_PCT = 0.0860890342
DK_PCT = 0.03283618376
BOWSER_PCT = 0.03283618376
DUEL_PCT = 0.05211141851
ITEM_PCT = 0.05778546277
SHOP_PCT = 0.03283618376
# ----------------------------------------------------------- #

# Estimates
MIN_STAR_DIST = 30
MAX_STAR_DIST = 40
GREEN_STAR_PCT = 0.05
BOWSER_MINIGAME_PCT = 0.5
BOWSER_TAKE_STAR_PCT = 0.1 
BOWSER_MIN_COIN_TAKE = 5
BOWSER_MAX_COIN_TAKE = 50
BATTLE_MINIGAME_PCT = 0.1

class Game(object):
    def __init__(self, players, max_turns, stats=GameStat()):
        self.players = [Player(x[0], x[1], ident=i) for i,x in enumerate(players)]
        self.total_skill = sum([x[0] for x in players])
        self.standings = []
        self.turn_num = 0
        self.max_turns = max_turns
        self.stats = stats

    def run(self):
        while self.turn_num < self.max_turns:
            self.turn()
            self.minigame()
            self.turn_num += 1
        self.bonus_stars()

    def minigame(self):
        win_amt = 0
        # Battle Mini-game
        if random.random() < BATTLE_MINIGAME_PCT: 
            bounty = 5 * random.choice([1, 2, 4, 6, 8, 10])
            for p in self.players:
                win_amt += min(bounty, p.coins)
                p.coins -= min(bounty, p.coins)
        else: win_amt = 10

        win_pcts = [p.skill/self.total_skill for p in self.players]

        r = random.random()
        p = 0.0
        for i, pct in enumerate(win_pcts):
            p += pct
            if r < p:
                self.players[i].coins += win_amt
                self.players[i].minigames_won += 1
                break

    def turn(self):

        # 1. Use Items and Roll
        #   1a. Double Dice
        #   1a. Triple Dice
        # 2. Check if star is passed
        # 3. Pick up Items and Shop (if money allows)
        # 4. Land on Space
        #   4a. Blue:   +3 Coins
        #   4b. Red:    -3 Coins
        #   4c. Green:  +Coins/Star, -Coins, Teleport
        #   4d. Bowser: -Coins/Star sometimes based on skill
        #   4e: DK:     +Coins/Star sometimes based on skill
        #   4f. Duel:   +- Coins/Star based on skill
        # 5. Minigame (once all players are done)

        for p in self.players:
            # 1. Use Items and Roll
            roll = self.roll()
            p.spaces_moved += roll
            p.spaces_from_star -= roll

            # 2. Check if star is passed
            if p.spaces_from_star <= 0:
                if p.coins >= 20:
                    self.give_star(p)
                else:
                    p.spaces_from_star = MAX_STAR_DIST + p.spaces_from_star

            # 3. Pick up Items and Shop (if money allows)
            if random.random() < ITEM_PCT * roll:
                p.items += 1

            # item_cost = random.randint(0, 4) * 5
            # if p.coins - item_cost >= 25: # TODO: Replace with some player-based tolerance value
            #     p.items += 1
            #     p.coins -= item_cost

            # 4. Land on Space
            r_space = random.random()

            # 4b. Red: -3 Coins
            if r_space < RED_PCT:
                p.red += 1
                p.coins -= 3

            # 4c. Green: +Coins/Star, -Coins, Teleport
            elif r_space < RED_PCT + GREEN_PCT:
                self.green_square(p)

            # 4d. Bowser: -Coins/Star sometimes based on Minigame pct
            elif r_space < RED_PCT + GREEN_PCT + BOWSER_PCT:
                self.bowser_square(p)

            # 4e: DK: +Coins/Srar sometimes based on skill
            elif r_space < RED_PCT + GREEN_PCT + BOWSER_PCT + DK_PCT:
                self.dk_square(p)

            # 4f. Duel: +- Coins/Star based on skill            
            elif r_space < RED_PCT + GREEN_PCT + BOWSER_PCT + DK_PCT + DUEL_PCT:
                self.duel_square(p)

            # 4a. Blue: +3 coins
            else:
                p.coins += 3

            # Make sure nothing is negative
            for x in self.players:
                x.coins = max(x.coins, 0)
                x.stars = max(x.stars, 0)

            self.update_standings()    

    def green_square(self, p):
        r = random.choice([1,2,3])

        # +Coins/Star - Coins are pretty much guaranteed, usually the question is how many. 
        # Stars are much more rare
        if r == 1:
            p.coins += random.randint(1, 20)
            if random.random() <= GREEN_STAR_PCT:
                p.stars += 1

        # -Coins - I don't think there are any green spaces that make you lose coins in MP7, but 
        # they're usually present in other games so I've included it here
        if r == 2:
            p.coins -= random.randint(1, 10)

        # Teleport - Note: These don't contribute to the movement bonus star
        if r == 3:
            p.spaces_from_star = random.randint(0, MAX_STAR_DIST)
            if p.spaces_from_star == 0:
                self.give_star(p) # Yes it's possible to get two stars in one turn!

        p.green += 1

    # Bowser really differs from game to game, but we keep it simple and assume
    # he either straight up takes from you or forces you to play a minigame
    def bowser_square(self, p):
        self.stats.num_bowsers += 1

        # Bowser straight up takes stuff from you
        if random.random() < (1-BOWSER_MINIGAME_PCT):
            if random.random() < BOWSER_TAKE_STAR_PCT:
                p.stars -= 1 
            else:                    
                p.coins -= random.randint(BOWSER_MIN_COIN_TAKE, BOWSER_MAX_COIN_TAKE)

        # Bowser mini-game: These are interesting since they're survival games rather than battles. 
        # In my experience, these mini-games vary in widely in difficulty but are generally not that 
        # easy to win. The single-player games do seem to be easier than the multiplayer ones, 
        # but for a multiplayer game only one player has to win to avoid all penalties for everyone. 
        else:
            # Single-player: apply a slight bonus since single-player games tend to be pretty easy
            if random.random() < 0.5: 
                # Failed - apply penalty
                if random.random() < 1-(p.skill / 100 + 0.05):
                    if random.random() < BOWSER_TAKE_STAR_PCT:
                        p.stars -= 1
                    else:
                        p.coins -= random.randint(BOWSER_MIN_COIN_TAKE, BOWSER_MAX_COIN_TAKE)
            # Multi-player: only one player has to pass
            else:
                game_pass = False
                for x in self.players:
                    if random.random() < p.skill / 100:
                        game_pass = True
                        break
                if not game_pass:
                    if random.random() < BOWSER_TAKE_STAR_PCT:
                        for x in self.players: x.stars -= 1
                    else:
                        t = random.randint(BOWSER_MIN_COIN_TAKE, BOWSER_MAX_COIN_TAKE)
                        for x in self.players: x.coins -= t

    # In other Mario Parties, DK usually does more. A star may only be acquired in single-player minigames
    def dk_square(self, p):
        # Single-Player DK
        if random.random() < 0.5:
            if random.random() < p.skill/100.0: # Wins
                r_dk = random.choice([1,2,3,4])
                if r_dk == 4:
                    p.stars += 1
                else:
                    p.coins += 10 * r_dk
        # Multi-Player DK
        else:
            r_dk = random.choice([1,2,3])
            total_bananas = 35
            for x in self.players:
                x.coins += int(x.skill/self.total_skill * total_bananas) * r_dk

    # Duels are especailly key since they can drastically turn a game around. Choosing an optimal 
    # duel opponent can be tricky, since it depends both on how many turns are remaining, how many stars/coins everyone has,
    # and the relative skill level of players. For example, while it makes sense to pick the weakest player, if she
    # has no stars, or if you're second and close to first, then it doesn't make sense to select her. It becomes even more
    # tricky in older MP games as the stakes aren't random and instead can be chosen. 
    #
    # Here, we'll stick with MP7 duel mechanics and make the stakes random with the possibilities being 
    # nothing, 10 coins, half coins, all coins, 1 star, 2 stars.
    #
    # To select an opponent, we'll assume players are always rational and choose the most +EV opponent. This may not necessarily
    # true in practice, since all that matters is first place so sometimes it makes sense to take larger risks. In other cases 
    # such as near the end of a game, it makes sense to take less risks and always choose the weakest opponent if you're in first.
    # 
    # Calculating EV is a bit tricky since we're working with both stars and coins. While stars are usually bought for 20 coins, 
    # it'd be very incorrect to use this conversion rate. Assuming that the farthest a star can be is 40 blocks, it would require at least 
    # two 3x dice blocks to reach it as quick as possible, giving us an actual cost of about 60 coins. Additionally, stars become
    # way more valuable as turns pass. So we assign stars a base value of 60 coins and exponentially scale their value up to 300 as 
    # time increases. This increase potential upside for those not in first. 
    # 
    # Time should also increase potential downside for people in higher levels (TODO)
    # 
    # And because only first place matters, we calculate EV relative to first place. So if you're in first place, EV is based off 
    # your "distance" to second place. For all other positions, EV is your "distance" to first place. Distance is measured by coins (after conversion).
    def duel_square(self, p):
        self.stats.num_duels += 1
        ev = self.calc_duel_ev(p)
        duel_target = max(ev, key=ev.get)
        win_pct = p.skill / (duel_target.skill + p.skill)
        winner = duel_target
        loser = p
        if random.random() < win_pct:
            winner = p
            loser = duel_target

        opt = random.choice([1,2,3,4,5,6])
        # Win 10 coins
        if opt == 2:
            self.stats.coins_from_duels += min(loser.coins, 10)
            winner.coins += min(loser.coins, 10)
            loser.coins -= min(loser.coins, 10)

        # Win half coins
        if opt == 3:
            self.stats.coins_from_duels += loser.coins / 2
            winner.coins += loser.coins / 2
            loser.coins /= 2

        # Win all coins
        if opt == 4:
            self.stats.coins_from_duels += loser.coins 
            winner.coins += loser.coins
            loser.coins = 0

        # Win one star
        if opt == 5:
            self.stats.stars_from_duels += min(loser.stars, 1)
            winner.stars += min(loser.stars, 1)
            loser.stars -= min(loser.stars, 1)

        # Win two stars
        if opt == 6:
            self.stats.stars_from_duels += min(loser.stars, 2)
            winner.stars += min(loser.stars, 2)
            loser.stars -= min(loser.stars, 2)


    def calc_duel_ev(self, p):
        ev = {}
        for x in self.players:
            if x == p: continue
            win_pct = p.skill / (x.skill + p.skill)
            star_to_coins = 60 * math.exp(math.log(5) * (self.turn_num / self.max_turns))
            exp_val = win_pct * (1/6) * (0 + min(x.coins, 10) + x.coins/2 + x.coins + min(x.stars, 1) * star_to_coins + min(x.stars, 2) * star_to_coins)
            exp_val -= (1-win_pct) * (1/6) * (0 + min(p.coins, 10) + p.coins/2 + p.coins + min(p.stars, 1) * star_to_coins + min(x.stars, 2) * star_to_coins)
            ev[x] = exp_val
        return ev

    def roll(self):
        return random.randint(0, 10)

    def give_star(self, p):
        p.stars += 1
        p.coins -= 20
        new_star = random.randint(MIN_STAR_DIST, MAX_STAR_DIST)
        for x in self.players:
            x.spaces_from_star = min(5, new_star-x.spaces_from_star)

    def bonus_stars(self):
        minigame_star = max(self.players, key=lambda x: x.minigames_won)
        running_star = max(self.players, key=lambda x: x.spaces_moved)
        happening_star = max(self.players, key=lambda x: x.green)
        red_star = max(self.players, key=lambda x: x.red)
        # shopping_star = max(self.players, key=lambda x: x.coins_spent)
        # orb_star = max(self.players, key=lambda x: x.items_used)
        opts = [minigame_star, running_star, happening_star, red_star]
        choices = random.choices(opts, k=3)
        for c in choices: c.stars += 1

    def update_standings(self):
        # Sort by coins, then by stars to take advantage of stable sort
        self.standings = sorted(self.players, key=lambda x: x.coins, reverse=True)
        self.standings = sorted(self.standings, key=lambda x: x.stars, reverse=True)

    def print_results(self):
        for p in self.players: print(p)

    def get_winner(self):
        self.update_standings()
        return self.standings[0].id


if __name__ == '__main__':
    players = [(45, 0), (50, 0), (52, 0), (55, 0)]
    wins = [0,0,0,0]
    n = 1000
    gs = GameStat()
    for x in range(0, n):
        g = Game(players, 15, stats=gs)
        g.run()
        wins[g.get_winner()] += 1
        gs.num_games += 1
    print([x/n for x in wins])
    print(gs.num_duels)
    print(gs.coins_from_duels)
    print(gs.stars_from_duels)
    print(gs.num_bowsers)



