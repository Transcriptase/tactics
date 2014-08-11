'''
Created on Aug 11, 2014

@author: rwill127
'''
from nose.tools import *
import tactics as t

class TestNode(object):
    def setup(self):
        self.n = t.Node(1,1)
    
    def test_node(self):
        eq_(self.n.x, 1)
        eq_(self.n.y, 1)
        
class TestGrid(object):
    def setup(self):
        self.m = t.Grid(10, 10)
    
    def test_map_init(self):
        m1 = t.Grid(2,3)
        eq_(len(m1.nodes), 3)
        eq_(len(m1.nodes[0]), 2)
        ok_(isinstance(m1.nodes[0][0], t.Node))
        eq_(m1.nodes[1][0].x, 0)
        eq_(m1.nodes[2][1].y, 2)
    
    def test_sm_map(self):
        eq_(len(self.m.nodes), 10)
        eq_(len(self.m.nodes[0]), 10)
        ok_(isinstance(self.m.nodes[9][9], t.Node))
        
    def test_neighbors(self):
        n1 = self.m.get_node(5,5)
        eq_(len(self.m.neighbors(n1, 1)), 8)
        n2 = self.m.get_node(0,3)
        eq_(len(self.m.neighbors(n2, 1)), 5)
        n3 = self.m.get_node(9,9)
        eq_(len(self.m.neighbors(n3, 1)), 3)

class TestTurn(object):
    def setup(self):
        grid = t.Grid(10, 10)
        self.slow = t.Unit()
        self.slow.speed = 2
        self.fast = t.Unit()
        self.fast.speed = 10
        self.b = t.Battle(grid)
        self.b.units = [self.slow, self.fast]
        
    def test_tick(self):
        self.b.tick()
        eq_(self.slow.ct, self.slow.speed)
        eq_(self.fast.ct, self.fast.speed)

    def test_run(self):
        self.b.run()
        eq_(self.b.active_unit, self.fast)
        eq_(self.slow.ct, 20)

class TestMove(object):
    def setup(self):
        grid = t.Grid(10, 10)
        self.u = t.Unit()
        self.b = t.Battle(grid)
        self.u.join_battle(self.b, 1, 1)
        
    def test_legal(self):
        m = self.u.legal_moves()