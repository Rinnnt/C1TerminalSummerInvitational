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
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, UPGRADE, REMOVE, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        UPGRADE = config["unitInformation"][7]["shorthand"]
        REMOVE = config["unitInformation"][6]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []
        self.attack = False
        self.rests = 0
        self.mpmap = dict()
        for i in range(100):
            self.mpmap[i] = 5 + (i // 5)

        self.SUPPORTS = [[9, 5], [10, 5], [11, 5], [12, 5], [13, 5], [10, 4], [11, 4], [12, 4], [11, 3]][::-1]
        self.SUPPORTS_UPGRADE = [[9, 5], [10, 5], [11, 5], [12, 5], [13, 5], [10, 4], [11, 4], [12, 4], [11, 3]][::-1]
        self.TURRET_WALL = [[25, 13], [26, 13], [27, 13], [1, 12], [21, 12], [24, 12], [2, 11], [20, 11], [23, 11], [3, 10], [19, 10], [22, 10], [4, 9], [18, 9], [21, 9], [5, 8], [17, 8], [20, 8], [6, 7], [16, 7], [19, 7], [7, 6], [15, 6], [18, 6], [8, 5], [14, 5], [17, 5], [9, 4], [13, 4], [16, 4], [10, 3], [12, 3], [15, 3], [11, 2], [14, 2], [13, 1]] 
        self.TURRET_WALL_REMOVE = [[25, 13], [26, 13], [27, 13], [21, 12], [24, 12], [2, 11], [20, 11], [23, 11], [3, 10], [19, 10], [22, 10], [4, 9], [18, 9], [21, 9], [5, 8], [17, 8], [20, 8], [6, 7], [16, 7], [19, 7], [7, 6], [15, 6], [18, 6], [8, 5], [14, 5], [17, 5], [9, 4], [13, 4], [16, 4], [10, 3], [12, 3], [15, 3], [11, 2], [14, 2], [13, 1]] 
        self.WALL_WALL = [[0, 13], [1, 13], [2, 13]]
        self.WALL_WALL_UPGRADE = [[0, 13], [1, 13], [2, 13]]
        self.WALL_WALL_REMOVE = [[0, 13], [1, 12], [1, 13]]
        self.TURRET_LEFT = [[1, 13], [2, 12], [3, 11], [4, 10]]
        self.TURRET_RIGHT = [[20, 12], [19, 11], [18, 10], [17, 9], [16, 8]]
        self.TURRET_RIGHT_UPGRADE = [[20, 12], [19, 11], [18, 10], [17, 9], [16, 8]]
        self.WALLS = [[2, 13], [3, 12], [20, 12], [4, 11]]
        self.WALLS_UPGRADE = [[2, 13], [3, 12], [20, 12], [4, 11]]
        self.TURRET_UPGRADE = [[21, 12], [24, 12], [20, 11], [25, 13], [23, 11], [19, 10], [22, 10], [18, 9], [21, 9], [17, 8], [20, 8], [16, 7], [19, 7]]
        self.ATTACK_CORNER = [[26, 13], [27, 13]]
        self.ATTACK_SPAWN = [[13, 0], [14, 0]]

        for ts in [self.TURRET_WALL, self.TURRET_LEFT, self.TURRET_RIGHT]:
            for t in ts:
                t.append(TURRET)
        for s in self.SUPPORTS:
            s.append(SUPPORT)
        for ws in [self.WALLS, self.WALL_WALL]:
            for w in ws:
                w.append(WALL)
        for us in [self.SUPPORTS_UPGRADE, self.WALLS_UPGRADE, self.TURRET_UPGRADE, self.TURRET_RIGHT_UPGRADE, self.WALL_WALL_UPGRADE]:
            for u in us:
                u.append(UPGRADE)
        for rs in [self.WALL_WALL_REMOVE, self.TURRET_WALL_REMOVE]:
            for r in rs:
                r.append(REMOVE)

        for bs in [self.SUPPORTS, self.SUPPORTS_UPGRADE, self.TURRET_WALL, self.TURRET_WALL_REMOVE, self.WALL_WALL, self.WALL_WALL_UPGRADE, self.WALL_WALL_REMOVE, self.TURRET_LEFT, self.TURRET_RIGHT, self.TURRET_RIGHT_UPGRADE, self.WALLS, self.WALLS_UPGRADE, self.TURRET_UPGRADE, self.ATTACK_CORNER, self.ATTACK_SPAWN]:
            for b in bs:
                b[0] = 27 - b[0]

        self.BUILD_SEQUENCE = []
        self.BUILD_SEQUENCE.extend(self.WALL_WALL_REMOVE)
        self.BUILD_SEQUENCE.extend(self.TURRET_WALL_REMOVE)
        self.BUILD_SEQUENCE.extend(self.WALL_WALL)
        self.BUILD_SEQUENCE.extend(self.TURRET_WALL)
        self.BUILD_SEQUENCE.extend(self.WALL_WALL_UPGRADE)
        self.BUILD_SEQUENCE.extend(self.TURRET_LEFT)
        self.BUILD_SEQUENCE.extend([x[:] for x in self.TURRET_UPGRADE[:2]])
        self.BUILD_SEQUENCE.extend(self.TURRET_RIGHT)
        self.BUILD_SEQUENCE.extend([x[:] for x in self.TURRET_UPGRADE[:4]])
        self.BUILD_SEQUENCE.append(self.SUPPORTS[0][:])
        self.BUILD_SEQUENCE.append(self.SUPPORTS_UPGRADE[0][:])
        self.BUILD_SEQUENCE.extend([x[:] for x in self.TURRET_UPGRADE[:6]])
        self.BUILD_SEQUENCE.append(self.SUPPORTS[1][:])
        self.BUILD_SEQUENCE.append(self.SUPPORTS_UPGRADE[1][:])
        self.BUILD_SEQUENCE.extend([x[:] for x in self.TURRET_UPGRADE[:8]])
        self.BUILD_SEQUENCE.append(self.SUPPORTS[2][:])
        self.BUILD_SEQUENCE.append(self.SUPPORTS_UPGRADE[2])
        self.BUILD_SEQUENCE.append(self.SUPPORTS[3][:])
        self.BUILD_SEQUENCE.append(self.SUPPORTS_UPGRADE[3][:])
        self.BUILD_SEQUENCE.extend([x[:] for x in self.TURRET_UPGRADE[:12]])
        self.BUILD_SEQUENCE.extend([val for pair in zip(self.SUPPORTS, self.SUPPORTS_UPGRADE) for val in pair])
        self.BUILD_SEQUENCE.extend([x[:] for x in self.TURRET_UPGRADE[:]])

        self.attack_sequence_1 = [None, None, SCOUT, None, None, DEMOLISHER, SCOUT]
        self.attack_sequence_2 = [SCOUT, None, SCOUT, None, None, DEMOLISHER, SCOUT]
        self.sequence_1 = 0
        self.sequence_2 = 0

    def spawn_and_upgrade(self, game_state, locations, unit):
        for location in locations:
            game_state.attempt_spawn(unit, location)
            game_state.attempt_upgrade(location)

    def build_structures(self, game_state, without=[]):
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        for b in self.BUILD_SEQUENCE:
            gamelib.debug_write(b)
            if b[:2] in without:
                continue

            units = game_state.game_map[b[:2]]
            if b[-1] == UPGRADE:
                game_state.attempt_upgrade(b[:2])
                if len(units) == 0 or not units[0].upgraded:
                    return
            elif b[-1] == REMOVE:
                if len(units) > 0:
                    if units[0].unit_type == WALL and (not units[0].upgraded and units[0].health < 30 or units[0].upgraded and units[0].health < 60):
                        game_state.attempt_remove(b[:2])
                    elif units[0].unit_type == TURRET and (not units[0].upgraded and units[0].health < 30 or units[0].upgraded and units[0].health < 20):
                        game_state.attempt_remove(b[:2])
            else:
                game_state.attempt_spawn(b[-1], b[:2])
                if len(game_state.game_map[b[:2]]) == 0:
                    return
            
    def more_on_left(self, game_state):
        map = game_state.game_map
        left = 0
        for i in range(14):
            for j in range(14, 28):
                if map.in_arena_bounds([i, j]):
                    if len(map[[i, j]]) > 0 and map[[i, j]][0].unit_type == TURRET:
                        left += 1
                        if map[[i, j]][0].upgraded:
                            left += 1
        right = 0
        for i in range(14, 28):
            for j in range(14, 28):
                if map.in_arena_bounds([i, j]):
                    if len(map[[i, j]]) > 0 and map[[i, j]][0].unit_type == TURRET:
                        right += 1
                        if map[[i, j]][0].upgraded:
                            right += 1

        return left > right

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

        init_MPs = [5, 8.8, 11.6, 13.7, 15.3, 17.5, 19.1, 20.3]

        if game_state.turn_number == 0:
            self.build_structures(game_state)
        elif game_state.turn_number == 1:
            if (self.more_on_left(game_state)):
                game_state.attempt_remove(list(map(lambda l: l[:2].copy(), self.WALL_WALL)))
                game_state.attempt_remove(list(map(lambda l: l[:2].copy(), self.TURRET_WALL)))
                for b in self.BUILD_SEQUENCE:
                    b[0] = 27 - b[0]
                for b in self.ATTACK_CORNER:
                    b[0] = 27 - b[0]
                for b in self.ATTACK_SPAWN:
                    b[0] = 27 - b[0]
            else:
                self.build_structures(game_state)
        else:
            if self.attack:
                self.attack = False
                self.rests = 0
                self.build_structures(game_state, without=self.ATTACK_CORNER)
                blocked = True
                empty = True
                for c in self.ATTACK_CORNER:
                    if len(game_state.game_map[[c[0], c[1] + 1]]) == 0:
                        blocked = False
                    else:
                        empty = False
                if empty:
                    for _ in range(100):
                        game_state.attempt_spawn(SCOUT, self.ATTACK_SPAWN[0])
                elif blocked:
                    for _ in range(6):
                        game_state.attempt_spawn(SCOUT, self.ATTACK_SPAWN[1])
                    for _ in range(100):
                        game_state.attempt_spawn(SCOUT, self.ATTACK_SPAWN[0])
                else:
                    demolishers = 0
                    if (game_state.turn_number < 10):
                        demolishers = 2
                    elif (game_state.turn_number < 20):
                        demolishers = 3
                    else:
                        demolishers = 4
                    for _ in range(4):
                        game_state.attempt_spawn(SCOUT, self.ATTACK_SPAWN[1])
                    for _ in range(demolishers):
                        game_state.attempt_spawn(DEMOLISHER, self.ATTACK_SPAWN[0])
                    for _ in range(100):
                        game_state.attempt_spawn(SCOUT, self.ATTACK_SPAWN[0])
            elif (game_state.get_resource(MP, 1) < 3 + self.mpmap[game_state.turn_number]) or self.rests > 2:
                self.build_structures(game_state)
                game_state.attempt_remove(self.ATTACK_CORNER)
                self.attack = True
            else:
                self.build_structures(game_state)
                self.rests += 1

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some interceptors early on.
        We will place turrets near locations the opponent managed to score on.
        For offense we will use long range demolishers if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
        """
        # First, place basic defenses
        self.build_defences(game_state)
        # Now build reactive defenses based on where the enemy scored
        self.build_reactive_defense(game_state)

        # If the turn is less than 5, stall with interceptors and wait to see enemy's base
        if game_state.turn_number < 5:
            self.stall_with_interceptors(game_state)
        else:
            # Now let's analyze the enemy base to see where their defenses are concentrated.
            # If they have many units in the front we can build a line for our demolishers to attack them at long range.
            if self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14, 15]) > 10:
                self.demolisher_line_strategy(game_state)
            else:
                # They don't have many units in the front so lets figure out their least defended area and send Scouts there.

                # Only spawn Scouts every other turn
                # Sending more at once is better since attacks can only hit a single scout at a time
                if game_state.turn_number % 2 == 1:
                    # To simplify we will just check sending them from back left and right
                    scout_spawn_location_options = [[13, 0], [14, 0]]
                    best_location = self.least_damage_spawn_location(game_state, scout_spawn_location_options)
                    game_state.attempt_spawn(SCOUT, best_location, 1000)

                # Lastly, if we have spare SP, let's build some supports
                support_locations = [[13, 2], [14, 2], [13, 3], [14, 3]]
                game_state.attempt_spawn(SUPPORT, support_locations)

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place turrets that attack enemy units
        turret_locations = [[0, 13], [27, 13], [8, 11], [19, 11], [13, 11], [14, 11]]
        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        game_state.attempt_spawn(TURRET, turret_locations)
        
        # Place walls in front of turrets to soak up damage for them
        wall_locations = [[8, 12], [19, 12]]
        game_state.attempt_spawn(WALL, wall_locations)
        # upgrade walls so they soak more damage
        game_state.attempt_upgrade(wall_locations)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames 
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build turret one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1]+1]
            game_state.attempt_spawn(TURRET, build_location)

    def stall_with_interceptors(self, game_state):
        """
        Send out interceptors at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        
        # Remove locations that are blocked by our own structures 
        # since we can't deploy units there.
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        
        # While we have remaining MP to spend lets send out interceptors randomly.
        while game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP] and len(deploy_locations) > 0:
            # Choose a random deploy location.
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]
            
            game_state.attempt_spawn(INTERCEPTOR, deploy_location)
            """
            We don't have to remove the location since multiple mobile 
            units can occupy the same space.
            """

    def demolisher_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our demolisher can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        stationary_units = [WALL, TURRET, SUPPORT]
        cheapest_unit = WALL
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost[game_state.MP] < gamelib.GameUnit(cheapest_unit, game_state.config).cost[game_state.MP]:
                cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our demolisher from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn demolishers next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(DEMOLISHER, [24, 10], 1000)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
            damages.append(damage)
        
        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()