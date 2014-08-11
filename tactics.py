'''
Created on Aug 11, 2014

@author: rwill127
'''

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
        return self.nodes[y][x]
 
    def neighbors(self, node, dist):
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
        self.move = 3
        
    def join_battle(self, battle, x, y):
        '''
        Attaches the Unit to a Battle in an initial position (x,y)
        '''
        self.battle = battle
        self.battle.units.append(self)
        self.location = self.battle.grid.get_node(x, y)
         
    def turn(self):
        self.ct = 0

    def legal_moves(self):
        in_range = self.battle.grid.neighbors(self.location, self.speed)
        return(in_range)

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
                
    def run(self):
        '''
        Advances time until a unit is ready
        '''
        while not self.active_unit:
            self.tick()
        self.active_unit.turn()

if __name__ == '__main__':
    pass