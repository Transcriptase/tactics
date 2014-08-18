"""
Created on Aug 11, 2014

@author: rwill127
"""
from nose.tools import *
import tactics as t


class TestNode(object):
    def setup(self):
        self.n = t.Node(1, 1)

    def test_node(self):
        eq_(self.n.x, 1)
        eq_(self.n.y, 1)


class TestGrid(object):
    def setup(self):
        self.m = t.Grid(10, 10)

    def test_map_init(self):
        m1 = t.Grid(2, 3)
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
        n1 = self.m.get_node(5, 5)
        eq_(len(self.m.neighbors(n1, 1)), 8)
        n2 = self.m.get_node(0, 3)
        eq_(len(self.m.neighbors(n2, 1)), 5)
        n3 = self.m.get_node(9, 9)
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

    def dummy_input_end_turn(self):
        return "End Turn"

    def test_tick(self):
        self.b.tick()
        eq_(self.slow.ct, self.slow.speed)
        eq_(self.fast.ct, self.fast.speed)

    def test_advance(self):
        self.b.advance()
        eq_(self.b.active_unit, self.fast)
        eq_(self.slow.ct, 20)

    def test_turn(self):
        self.b.advance()
        eq_(self.b.active_unit, self.fast)
        eq_(self.b.active_unit.ct, 100)
        self.b.active_unit.turn(self.dummy_input_end_turn)
        eq_(self.fast.ct, 0)

    def test_next_turn(self):
        self.b.next_turn(self.dummy_input_end_turn)
        ok_(not self.b.active_unit)
        eq_(self.fast.ct, 0)
        eq_(self.slow.ct, 20)
        self.b.next_turn(self.dummy_input_end_turn)
        ok_(not self.b.active_unit)
        eq_(self.fast.ct, 0)
        eq_(self.slow.ct, 40)


class TestMove(object):
    def setup(self):
        grid = t.Grid(10, 10)
        self.u = t.Unit()
        self.b = t.Battle(grid)
        self.u.join_battle(self.b, 1, 1)
        self.u.move_speed = 1  # To keep options list small

    def test_legal(self):
        m = self.u.legal_moves()
        eq_(len(m), 8)

    def test_possible_actions(self):
        self.u.moved = False
        self.u.acted = False
        m = self.u.possible_actions()
        eq_(len(m), 3)
        ok_("Move" in m)
        ok_("End Turn" in m)


class TestHealth(object):
    def setup(self):
        self.u = t.Unit()

    def test_die(self):
        ok_(self.u.alive)
        self.u.die()
        eq_(self.u.current_hp, 0)
        ok_(not self.u.alive)

    def test_hp_update(self):
        self.u.current_hp = 100
        self.u.update_hp(-20)
        eq_(self.u.current_hp, 80)
        self.u.update_hp(30)
        eq_(self.u.current_hp, 100)
        self.u.update_hp(-110)
        eq_(self.u.current_hp, 0)


class TestMelee(object):
    def setup(self):
        self.u1 = t.Unit()
        self.u2 = t.Unit()

    def dummy_hit_chk_true(self, target):
        return True

    def dummy_hit_chk_false(self, target):
        return False

    def dummy_dmg(self, target):
        return 10

    def test_melee_atk(self):
        self.u1.melee_atk(self.u2, self.dummy_hit_chk_false, self.dummy_dmg)
        eq_(self.u2.current_hp, 100)
        self.u1.melee_atk(self.u2, self.dummy_hit_chk_true, self.dummy_dmg)
        eq_(self.u2.current_hp, 90)


class TestTeam(object):
    def setup(self):
        self.t = t.Team()
        for i in xrange(5):
            new_unit = t.Unit()
            self.t.all_units.append(new_unit)

    def test_live_update(self):
        self.t.live_update()
        eq_(len(self.t.live_units), 5)
        self.t.all_units[1].die()
        self.t.live_update()
        eq_(len(self.t.live_units), 4)
        eq_(len(self.t.dead_units), 1)

    def test_defeat(self):
        ok_(not self.t.is_defeated())
        for unit in self.t.all_units:
            unit.die()
        ok_(self.t.is_defeated())


class TestMenu(object):
    def setup(self):
        options = ["Larry", "Moe", "Curly"]
        title = "Stooges"
        self.m = t.Menu(options, title)
        self.responses = ["67",
                          "walrus",
                          "1"]
        self.fail_count = 0

    def f(self, responses):
        """
        A generator that steps through a list of responses
        """
        for response in responses:
            yield response

    def g(self, generator):
        """
        Returns a function that returns the next element of the generator.

        Swapped out for the normal input function, simulates entering the
        responses in sequence.
        """
        return lambda: next(generator)

    def fail_capture(self):
        """
        Sub in for usual fail function to count number of failures
        """
        self.fail_count += 1

    def test_string(self):
        predicted_str = "Stooges:\n0: Larry\n1: Moe\n2: Curly\n"
        eq_(str(self.m), predicted_str)

    def test_menu(self):
        r = self.m.get_result(self.m.text_display, self.g(self.f(self.responses)), self.fail_capture)
        # Should fail twice, then choose option indexed 1.
        eq_(r, "Moe")
        eq_(self.fail_count, 2)


class TestVis(object):
    def setup(self):
        g = t.Grid(10, 10)
        b = t.Battle(g)

        starts = [(0, 0),
                  (9, 9)]
        for start in starts:
            new_unit = t.Unit()
            new_unit.join_battle(b, start[0], start[1])

        self.v = t.Visualizer(b)

    def test_draw_grid(self):
        self.v.draw()
