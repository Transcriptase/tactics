'''
Created on Aug 11, 2014

@author: rwill127
'''
import pygame
import sys

class Node(object):
    '''
    A single location on a map grid.
    '''
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
    '''
    A cartesian grid of nodes, stored as a list of lists
    '''
    def __init__(self, x, y):
        '''
        Note that this construction method means that the
        y coordinate comes first when calling directly from
        the map matrix.
        
        To avoid confusion, use get_node(x, y) instead of
        raw indexing.
        '''
        self.nodes = []
        for j in range(y):
            self.nodes.append([])
            for i in range(x):
                new_node = Node(i, j)
                self.nodes[j].append(new_node)
                
    def get_node(self, x, y):
        '''
        Returns the Node at (x,y). Use to avoid x/y coordinate confusion
        ''' 
        return self.nodes[y][x]
 
    def neighbors(self, node, dist):
        '''
        Returns a list of Nodes that are within dist squares of the original Node.
        '''
        neighbors = []
        deltas = range(-dist,dist+1)
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
        self.move_speed = 3
        self.name = "A"

    def move(self, node):
        '''
        Sets the Unit's location to the specified Node
        '''
        self.location = node
        
    def join_battle(self, battle, x, y):
        '''
        Attaches the Unit to a Battle in an initial position (x,y)
        '''
        self.battle = battle
        self.battle.units.append(self)
        self.move(battle.grid.get_node(x,y))
         
    def legal_moves(self):
        '''
        Returns a list of Nodes it is legal to move to.
        Currently checks only for move range.
        '''
        in_range = self.battle.grid.neighbors(self.location, self.move_speed)
        return(in_range)
    
    def make_move_menu(self):
        '''
        Create and print an indexed list of possible moves
        '''
        move_menu = dict(zip(range(len(self.legal_moves())), self.legal_moves()))
        return(move_menu)
        
    def print_menu(self, menu, title):
        '''
        Prints a dictionary as a menu, preceded by title.
        '''
        print "%s :\n" % title
        for number, item in menu.iteritems():
            print "%s: %s" % (number, item)
            
    def prompt_for_input(self):
        '''
        Prompt user for selection from list
        Just a wrapper for raw_input for testing purposes
        '''
        return(raw_input("Enter a number: "))
        
    def pull_from_menu(self, command, menu):
        '''
        Returns an item selected from a numerically indexed menu prompt
        '''
        try:
            command = int(command)
        except:
            return(False)
        if command in menu.keys():
            result = menu[int(command)]
            return(result)
        else:
            return(False)
        
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

    
    def turn(self):
        print "%s's Turn:" % self.name
        self.get_move_command(self.prompt_for_input)
        self.ct = 0

class Battle(object):
    def __init__(self, grid):
        self.units = []
        self.active_unit = False
        self.grid = grid
        
    def tick(self):
        '''
        Moves time forward by one tick
        '''
        for unit in self.units:
            unit.ct += unit.speed
            if unit.ct >= 100:
                self.active_unit = unit
                
    def advance(self):
        '''
        Advances time until a unit is ready
        '''
        while not self.active_unit:
            self.tick()
        
    def run(self, kill_func):
        '''
        Main Battle loop. Proceeds until kill_func returns True
        '''
        finished = False
        while not finished:
            self.advance()
            self.active_unit.turn()
            self.active_unit = False
            finished = kill_func()
            
    def manual_kill_check(self):
        '''
        Manual stop of the main loop
        '''
        if raw_input("Quit?") == "y":
            return True
        else:
            return False
        
class Visualizer(object):
    '''
    Uses pygame to graphically represent a Battle
    '''
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
                (0,y),
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
        
        START_POSITIONS = [(0, 0),
                           (9, 9)]
        NAMES = ["A",
                 "B"]
        
        SPEEDS = [3,8]
        
        for info in zip(NAMES, SPEEDS, START_POSITIONS):
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