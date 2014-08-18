"""
Created on Aug 11, 2014

@author: rwill127
"""
import pygame
import sys


class Node(object):
    """
    A single location on a map grid.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "Node(%s, %s)" % (
            self.x,
            self.y
        )

    def __repr__(self):
        return "Node(%r, %r)" % (self.x, self.y)


class Grid(object):
    """
    A cartesian grid of nodes, stored as a list of lists
    """

    def __init__(self, x, y):
        """
        Note that this construction method means that the
        y coordinate comes first when calling directly from
        the map matrix.

        To avoid confusion, use get_node(x, y) instead of
        raw indexing.
        """
        self.nodes = []
        for j in range(y):
            self.nodes.append([])
            for i in range(x):
                new_node = Node(i, j)
                self.nodes[j].append(new_node)

    def get_node(self, x, y):
        """
        Returns the Node at (x,y). Use to avoid x/y coordinate confusion
        """
        return self.nodes[y][x]

    def neighbors(self, node, dist):
        """
        Returns a list of Nodes that are within dist squares of the original Node.
        """
        neighbors = []
        deltas = range(-dist, dist + 1)
        for delta in deltas:
            new_x = node.x + delta
            for delta in deltas:
                new_y = node.y + delta
                if (new_x in range(len(self.nodes)) and
                            new_y in range(len(self.nodes[0]))
                ):
                    new_node = self.get_node(new_x, new_y)
                    if new_node != node:
                        neighbors.append(new_node)
        return neighbors


class Unit(object):
    def __init__(self):
        self.speed = 5
        self.ct = 0
        self.move_speed = 2
        self.name = "A"
        self.max_hp = 100
        self.current_hp = 100
        self.alive = True

        self.moved = False
        self.acted = False
        self.turn_finished = False

        self.location = False
        self.battle = False


    def move(self, node):
        """
        Sets the Unit's location to the specified Node
        """
        self.location = node
        self.moved = True

    def join_battle(self, battle, x, y):
        """
        Attaches the Unit to a Battle in an initial position (x,y)
        """
        self.battle = battle
        self.battle.units.append(self)
        self.move(battle.grid.get_node(x, y))

    def legal_moves(self):
        """
        Returns a list of Nodes it is legal to move to.
        Currently checks only for move range.
        """
        in_range = self.battle.grid.neighbors(self.location, self.move_speed)
        return in_range

    def possible_actions(self):
        options = []
        if not self.moved:
            options.append("Move")
        if not self.acted:
            options.append("Action")
        always = ["End Turn"]
        for item in always:
            options.append(item)
        return options

    def make_move_menu(self):
        """
        Create and print an indexed list of possible moves
        """
        move_menu = dict(zip(range(len(self.legal_moves())), self.legal_moves()))
        return move_menu

    def print_menu(self, menu, title):
        """
        Prints a dictionary as a menu, preceded by title.
        """
        print "%s :\n" % title
        for number, item in menu.iteritems():
            print "%s: %s" % (number, item)

    def prompt_for_input(self):
        """
        Prompt user for selection from list
        Just a wrapper for raw_input for testing purposes
        """
        return raw_input("Enter a number: ")

    def pull_from_menu(self, command, menu):
        """
        Returns an item selected from a numerically indexed menu prompt
        """
        try:
            command = int(command)
        except:
            return False
        if command in menu.keys():
            result = menu[int(command)]
            return result
        else:
            return False

    def get_move_command(self, input_func):
        menu = self.make_move_menu()
        self.print_menu(menu, "Possible moves")
        finished = False
        while not finished:
            command = input_func()
            dest = self.pull_from_menu(command, menu)
            if dest:
                self.move(dest)
                finished = True
            else:
                print("Please select a number from the menu.")

    def turn(self, input_func):
        """
        Run when a unit becomes active. Steps through turn sequence, then resets CT

        input_func = The function that returns the next action command
        """
        # Reset moved and acted counters
        self.moved = False
        self.acted = False
        self.turn_finished = False

        # Set up loop
        while not self.turn_finished:
            action = input_func()
            self.action_parse(action)
        self.ct = 0

    def action_parse(self, action):
        if action == "Move":
            self.execute_move_command()
        elif action == "End Turn":
            self.execute_end_turn_command()

    def execute_move_command(self):
        move_menu = Menu(self.legal_moves(), "Move to")
        dest = move_menu.text_get_result()
        self.move(dest)
        self.moved = True

    def execute_end_turn_command(self):
        self.turn_finished = True

    def update_hp(self, amount):
        """
        Changes the Unit's HP by amount. Handles cases over max and under 0.
        """
        new_hp = self.current_hp + amount
        if new_hp <= 0:
            self.die()
        elif new_hp >= self.max_hp:
            self.current_hp = self.max_hp
        else:
            self.current_hp = new_hp

    def die(self):
        """
        Kills a Unit
        """
        self.current_hp = 0
        self.alive = False

    def melee_atk(self, target, hit_func, dmg_func):
        """
        Perform a melee attack against target.

        hit_func is the function used to calculate hit.
        Should return bool
        dmg_func is the function used to calculate dmg
        Should return int

        (Loosely coupled for testing, can pass in dummy hit/dmg calcs)
        """
        if hit_func(target):
            target.update_hp(-dmg_func(target))

    def melee_hit_check(self, target):
        """
        Determine if a melee attack hits target
        Currently a placeholder
        """
        return True

    def melee_dmg(self, target):
        """
        Determine melee damage
        Currently a placeholder
        """
        damage = 10
        return damage


class Team(object):
    """
    A group of Units controlled by a player or AI.
    """

    def __init__(self):
        self.all_units = []
        self.live_units = []
        self.dead_units = []

    def live_update(self):
        for unit in self.all_units:
            if unit.alive:
                if unit not in self.live_units:
                    self.live_units.append(unit)
                if unit in self.dead_units:
                    self.dead_units.remove(unit)
            elif not unit.alive:
                if unit in self.live_units:
                    self.live_units.remove(unit)
                if unit not in self.dead_units:
                    self.dead_units.append(unit)

    def is_defeated(self):
        """
        Flags true when all a team's units are dead.
        """
        self.live_update()
        if len(self.live_units) == 0:
            return True
        else:
            return False


class Battle(object):
    def __init__(self, grid):
        self.teams = []
        self.units = []
        self.active_unit = False
        self.grid = grid

        self.finished = False

    def tick(self):
        """
        Moves time forward by one tick
        """
        for unit in self.units:
            unit.ct += unit.speed
            if unit.ct >= 100:
                self.active_unit = unit

    def advance(self):
        """
        Advances time until a unit is ready
        """
        while not self.active_unit:
            self.tick()

    def run(self, kill_func):
        """
        Main Battle loop.

        Parameters:
        input_func: The function that returns the command
        kill_func : A function that ends the loop when it returns True
        """
        self.finished = False
        while not self.finished:
            self.next_turn(self.active_unit.text_get_command)
            self.finished = kill_func()

    def next_turn(self, input_func):
        '''
        Finds the next active unit, runs its turn, and resets

        input_func: The function that returns the command.
        '''
        self.advance()
        self.active_unit.turn(input_func)
        self.active_unit = False

    def manual_kill_check(self):
        """
        Manual stop of the main loop
        """
        if raw_input("Quit?") == "y":
            return True
        else:
            return False

    def defeat_check(self):
        for team in self.teams:
            if team.is_defeated():
                return True
        return False


class Menu(object):
    """
    Presents a menu and returns the choice

    Parameters:

    options: A list. When complete, the menu will return the
    selected element of the list.

    title: The title of the menu
    """

    def __init__(self, options, title):
        self.options = options
        self.title = title

    def __str__(self):
        """
        Creates a string presentation of the menu
        """
        text_menu = ["%s:\n" % self.title]
        for number, item in zip(xrange(len(self.options)), self.options):
            text_menu.append("%s: %s\n" % (number, item))
        text_menu = "".join(text_menu)
        return text_menu

    def text_display(self):
        '''
        Simplest display function. Prints string representation of menu.
        '''
        print self

    def text_prompt(self):
        '''
        Prompt user for selection from list
        Just a wrapper for raw_input for testing purposes
        '''
        return raw_input("Enter a number: ")

    def pull(self, command):
        """
        Attempts to resolve a command into a menu selection.
        Returns the selection if successful, and False if not.
        """
        try:
            command = int(command)
        except:
            return False
        if command in xrange(len(self.options)):
            result = self.options[command]
            return result
        else:
            return False

    def text_fail(self):
        print "Invalid input. Please select again."

    def get_result(self,
                   display_func,
                   input_func,
                   fail_func):
        """
        Core menu loop. Displays the menu, gets input until a
        usable result occurs, then returns the result.

        Parameters:
        display_func: A function that displays the menu.
        (Currently only self.text_display)
        input_func: The function that prompts for user input.
        (Currently only self.text_prompt)
        fail_func: Function run if input is invalid
        (Currently only self.text_fail)
        """
        display_func()
        finished = False
        while not finished:
            command = input_func()
            if self.pull(command):
                finished = True
                return self.pull(command)
            else:
                fail_func()

    def text_get_result(self):
        """
        Wrapper for get_result() with STDOUT text-based options
        """
        return (self.get_result(self.text_display,
                                self.text_prompt,
                                self.text_fail))


class Visualizer(object):
    """
    Uses pygame to graphically represent a Battle
    """
    WINDOWWIDTH, WINDOWHEIGHT = 800, 800

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    DK_GREY = (40, 40, 40)

    def __init__(self, battle):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.WINDOWWIDTH, self.WINDOWHEIGHT))

        self.battle = battle
        self.grid = battle.grid
        self.grid_width = self.WINDOWWIDTH / len(self.grid.nodes[0])
        self.grid_height = self.WINDOWHEIGHT / len(self.grid.nodes)

        self.font = pygame.font.Font(None, 36)

    def draw_grid(self):
        for x in range(0, self.WINDOWWIDTH, self.grid_width):
            pygame.draw.line(
                self.screen,
                self.DK_GREY,
                (x, 0),
                (x, self.WINDOWHEIGHT)
            )
        for y in range(0, self.WINDOWHEIGHT, self.grid_height):
            pygame.draw.line(
                self.screen,
                self.DK_GREY,
                (0, y),
                (self.WINDOWWIDTH, y))

    def fill_grid(self):
        for row in self.grid.nodes:
            for node in row:
                draw_x = node.x * self.grid_width
                draw_y = node.y * self.grid_height
                color = self.WHITE
                draw_node = pygame.Rect(
                    (draw_x, draw_y, self.grid_width, self.grid_height))
                pygame.draw.rect(self.screen, color, draw_node)

    def place_units(self):
        for unit in self.battle.units:
            draw_x = int((unit.location.x * self.grid_width) + 0.5 * self.grid_width)
            draw_y = int((unit.location.y * self.grid_height) + 0.5 * self.grid_height)
            color = self.BLACK
            pygame.draw.circle(self.screen, color, (draw_x, draw_y), int(.45 * self.grid_width))

    def draw(self):
        self.fill_grid()
        self.draw_grid()
        self.place_units()

    def run(self):
        while True:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()


if __name__ == '__main__':

    def main():
        g = Grid(10, 10)
        b = Battle(g)

        start_positions = [(0, 0),
                           (9, 9)]
        names = ["A",
                 "B"]

        speeds = [3, 8]

        for info in zip(names, speeds, start_positions):
            name, speed, start = info
            x = start[0]
            y = start[1]
            new_unit = Unit()
            new_unit.name = name
            new_unit.speed = speed
            new_unit.join_battle(b, x, y)

        v = Visualizer(b)
        v.run()

    main()