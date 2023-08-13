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

        self.MPMAP = [5, 8.8, 11.6, 13.7, 15.3, 16.5]
        
        self.TURRETS1_LOCATION = [[5, 12],[2, 13], [3, 12]] 
        self.TURRETS2_LOCATION = [[25, 11], [24,11]]

        self.TURRETS3_LOCATION = [[23, 12], [22, 11], [21, 10], [20, 9], [19, 8], [18, 7], [17, 6], [16, 5], [15, 4]]
        self.TURRETS4_LOCATION = [[6, 12], [7, 11], [8, 10], [9, 9], [10, 8], [11, 7], [12, 6], [13, 5], [14, 4]]
        
        self.WALLS1_LOCATION = [[26,12], [0, 13], [1, 13], [6, 11], [23, 11], [7, 10], [22, 10], [8, 9], [21, 9], [9, 8], [20, 8], [10, 7], [19, 7], [11, 6], [18, 6], [12, 5], [17, 5], [13, 4], [16, 4], [14, 3], [15, 3]]
        self.WALLS2_LOCATION = [[3, 13], [6, 12], [27, 13], [24, 12], [25, 12]]
        self.WALLS3_LOCATION = [[3, 11], [4, 10], [5, 9], [6, 8], [7, 7], [8, 6], [9, 5], [10, 4], [11, 3], [12, 2], [13, 1]]

        self.SUPPORTS_LOCATION = [[5, 8], [6, 7], [7, 6]]
        self.SUPPORT2_LOCATION = [[8,5],[9,4],[10,3],[11,2],[12,1]]

        self.TURRETS1 = [(l, TURRET) for l in self.TURRETS1_LOCATION]
        self.TURRETS2 = [(l, TURRET) for l in self.TURRETS2_LOCATION]
        self.TURRETS3 = [(l, TURRET) for l in self.TURRETS3_LOCATION]
        self.TURRETS4 = [(l, TURRET) for l in self.TURRETS4_LOCATION]
        self.WALLS1 = [(l, WALL) for l in self.WALLS1_LOCATION]
        self.WALLS2 = [(l, WALL) for l in self.WALLS2_LOCATION]
        self.WALLS3 = [(l, WALL) for l in self.WALLS3_LOCATION]
        self.SUPPORTS = [(l, SUPPORT) for l in self.SUPPORTS_LOCATION]
        self.SUPPORTS2 = [(l, SUPPORT) for l in self.SUPPORT2_LOCATION]
        
    
        # self.PATH_LOCATION = [[3, 11], [4, 10], [5, 9], [6, 8], [7, 7], [8, 6], [9, 5], [10, 4], [11, 3], [12, 2], [13, 1]]
        # self.PATH = [(self.PATH_LOCATION[i], TURRET if i % 2 else SUPPORT) for i in range(len(self.PATH_LOCATION))]

    # RETURN TOTAL NUMBER OF UNITS SPAWNED
    def spawn(self, build):
        total = 0
        for location, unit in build:
            total += self.game_state.attempt_spawn(unit, location)
        return total

    def upgrade(self, build):
        total = 0 
        for location, unit in build:
            total += self.game_state.attempt_upgrade(location)
        return total
    
    def check_spawn(self, build):
        for location, unit in build:
            if not self.game_state.game_map[location[0], location[1]]:
                return False
        return True
    
    def check_upgrade(self, build):
        for location, unit in build:
            if self.game_state.game_map[location[0], location[1]] and not self.game_state.game_map[location[0], location[1]][0].upgraded:
                return False
        return True
    
    def build_in_order(self, build_order):
        for build, type in build_order:
            if type == "SPAWN":
                self.spawn(build)
                if not self.check_spawn(build):
                    return False
            if type == "UPGRADE":
                self.upgrade(build)
                if not self.check_upgrade(build):
                    return False
        return True

    def attack_with_two_demolishers(self):
        self.spawn([([4, 9], DEMOLISHER) for _ in range(2)])
    
    def attack_with_one_demolisher_and_max_scouts(self):
        self.spawn([([4, 9], DEMOLISHER)])
        self.spawn([([8, 5], SCOUT) for _ in range(100)])
    
    def attack_with_max_demolishers(self):
        self.spawn([([13, 0], DEMOLISHER) for _ in range(100)])

    def attack_with_max_scouts(self, location):
        self.spawn([(location, SCOUT) for _ in range(100)])

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
        build_order = [
                        (self.WALLS1, "SPAWN"),
                        (self.WALLS2, "SPAWN"),
                        (self.TURRETS1, "SPAWN"),
                        (self.TURRETS1, "UPGRADE"),
                        (self.TURRETS2, "SPAWN"),
                        (self.TURRETS2, "UPGRADE"),
                        (self.WALLS2, "UPGRADE"),
                        (self.WALLS3, "SPAWN"),
                        (self.SUPPORTS, "SPAWN"),
                        (self.SUPPORTS, "UPGRADE"),
                        (self.TURRETS3 , "SPAWN"),
                        (self.SUPPORT2, "SPAWN"),
                        (self.WALLS3, "UPGRADE"),
                        (self.SUPPORTS2, "UPGRADE"),
                        (self.TURRETS4, "SPAWN"),
                        (self.TURRETS3, "UPGRADE"),
                        # (self.PATH, "SPAWN"),
                        ]
        self.build_in_order(build_order)
        
        # attack
        # if (self.game_state.turn_number % 4 == 0):
        #     # self.spawn(game_state, [[4, 9]], DEMOLISHER)
        #     # self.spawn(game_state, [[8, 5] for _ in range(100)], SCOUT)
        #     # self.attack_with_one_demolisher_and_max_scouts()
            # self.attack_with_max_demolishers()
        # elif (self.game_state.turn_number % 2 == 0):
            # self.attack_with_two_demolishers()
        
        loss1 = 0
        for location in self.game_state.find_path_to_edge([13, 0]):
            for attacker in self.game_state.get_attackers(location, 0):
                loss1 += 20 if attacker.upgraded else 8
        loss2 = 0
        for location in self.game_state.find_path_to_edge([14, 0]):
            for attacker in self.game_state.get_attackers(location, 0):
                loss2 += 20 if attacker.upgraded else 8
        
        spawn_location = [13, 0] if loss1 < loss2 else [14, 0]

        if self.game_state.turn_number < 20:
            if self.game_state.get_resource(MP, 0) > 15:
                self.attack_with_max_scouts(spawn_location)
        else:
            if self.game_state.get_resource(MP, 0) > 21:
                self.attack_with_max_scouts(spawn_location)

        self.game_state.submit_turn()

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
