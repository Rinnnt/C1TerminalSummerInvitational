import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup

        self.scored_on_locations = []
        self.game_state = None
        

        # self.TURRETS = [[22, 11], [25, 11], [4, 13], [11, 13],  [7, 11], [17, 11]]
        # self.WALLS = [[0, 13], [1, 13], [2, 13], [3, 13], [5, 13], [6, 13], [7, 13], [8, 13], [9, 13], [10, 13], [12, 13], [13, 13], [14, 13], [15, 13], [16, 13], [17, 13], [18, 13], [19, 13], [20, 13], [21, 13], [22, 13], [25, 13], [26, 13], [27, 13]]
        # self.WALLS   = [[0, 13], [1, 13], [2, 13], [3, 13], [4, 13], [5, 13], [6, 13], [7, 13], [8, 13], [9, 13], [11, 13], [12, 13], [13, 13], [14, 13], [15, 13], [16, 13], [17, 13], [18, 13], [19, 13], [20, 13], [21, 13], [22, 13], [23, 13], [24, 13], [25, 13], [26, 13], [27, 13]]
        self.WALLS = [[0, 13], [1, 13], [2, 13], [25, 13], [26, 13], [27, 13], [3, 12], [4, 12], [23, 12], [24, 12]]
        self.TURRETS = [[2, 12], [25, 12], [7, 10], [20, 10], [13, 9]]
        self.TURRETS_EXTRA = [[1, 12], [26, 12]]

        self.SUPPORTS = [[6, 9], [7, 9], [8, 9], [5, 8], [6, 8], [7, 8], [8, 8], [6, 7], [7, 7], [8, 7], [7, 6]]

    # RETURN TOTAL NUMBER OF UNITS SPAWNED
    def spawn(self, locations, unit):
        total = 0
        for location in locations:
            total += self.game_state.attempt_spawn(unit,location)
        return total

    def upgrade(self, locations):
        total = 0 
        for location in locations:
            total += self.game_state.attempt_upgrade(location)
        return total
    
    def check_spawn(self, locations):
        for location in locations:
            if not self.game_state.game_map[location[0], location[1]]:
                return False
        return True
    
    def check_upgrade(self, locations):
        for location in locations:
            if self.game_state.game_map[location[0], location[1]] and not self.game_state.game_map[location[0], location[1]][0].upgraded:
                return False
        return True
    
    def build_in_order(self, build_order):
        for locations, type, unit in build_order:
            if type == "SPAWN":
                self.spawn(locations, unit)
                if not self.check_spawn(locations):
                    return False
            if type == "UPGRADE":
                self.upgrade(locations)
                if not self.check_upgrade(locations):
                    return False
        return True

    def attack_with_two_demolishers(self):
        self.spawn([[4, 9], [4, 9]], DEMOLISHER)
    
    def attack_with_one_demolisher_and_max_scouts(self):
        self.spawn([[4, 9]], DEMOLISHER)
        self.spawn([[8, 5] for _ in range(100)], SCOUT)

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        self.game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(self.game_state.turn_number))
        self.game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        # defense
        self.spawn(self.TURRETS, TURRET)
        self.spawn(self.WALLS, WALL)
        self.upgrade(self.TURRETS) 
        self.spawn(self.SUPPORTS, SUPPORT)

        if self.check_upgrade(self.TURRETS):
            self.spawn(self.TURRETS_EXTRA, TURRET)
            
  
        
        # attack
        if (self.game_state.turn_number % 4 == 0):
            # self.spawn(game_state, [[4, 9]], DEMOLISHER)
            # self.spawn(game_state, [[8, 5] for _ in range(100)], SCOUT)
            self.attack_with_one_demolisher_and_max_scouts()
        elif (self.game_state.turn_number % 2 == 0):
            self.attack_with_two_demolishers()


        self.game_state.submit_turn()

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
