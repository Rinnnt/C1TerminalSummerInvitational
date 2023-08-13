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

        self.TURRETS = [[4, 13], [11, 13], [22, 11], [25, 11]]
        self.WALLS = [[0, 13], [1, 13], [2, 13], [3, 13], [5, 13], [6, 13], [7, 13], [8, 13], [9, 13], [10, 13], [12, 13], [13, 13], [14, 13], [15, 13], [16, 13], [17, 13], [18, 13], [19, 13], [20, 13], [21, 13], [22, 13], [25, 13], [26, 13], [27, 13]]


    def spawn(self, game_state, locations, unit):
        for location in locations:
            game_state.attempt_spawn(unit,location)

    def upgrade(self, game_state, locations):
        for location in locations:
            game_state.attempt_upgrade(location)

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.spawn(game_state, self.TURRETS, TURRET)
        self.spawn(game_state, self.WALLS, WALL)
        self.upgrade(game_state, self.TURRETS)
        self.spawn(game_state, [[1, 12]], DEMOLISHER)

        if (game_state.turn_number % 4 == 0):
            self.spawn(game_state, [[1, 12] for _ in range(100)], SCOUT)

        game_state.submit_turn()

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
