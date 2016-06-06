#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________
#
# Unit Tests for indexed components
#

import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep

import pyutilib.th as unittest

from pyomo.environ import *
from pyomo.core.base.block import _BlockData
from pyomo.core.base.indexed_component import _IndexedComponent_slicer


class TestSimpleVar(unittest.TestCase):

    def test0(self):
        # Test fixed attribute - 1D
        m = ConcreteModel()
        m.x = Var()

        names = set()
        for var in m.x[:]:
            names.add(var.cname(True))
        self.assertEqual(names, set(['x']))

    def test1(self):
        # Test fixed attribute - 1D
        m = ConcreteModel()
        m.x = Var(range(3), dense=True)

        names = set()
        for var in m.x[:]:
            names.add(var.cname(True))
        self.assertEqual(names, set(['x[0]', 'x[1]', 'x[2]']))

    def test2a(self):
        # Test fixed attribute - 2D
        m = ConcreteModel()
        m.x = Var(range(3), range(3), dense=True)

        names = set()
        for var in m.x[:, 1]:
            names.add(var.cname(True))
        self.assertEqual(names, set(['x[0,1]', 'x[1,1]', 'x[2,1]']))

    def test2b(self):
        # Test fixed attribute - 2D
        m = ConcreteModel()
        m.x = Var(range(3), range(3), dense=True)

        names = set()
        for var in m.x[2, :]:
            names.add(var.cname(True))
        self.assertEqual(names, set(['x[2,0]', 'x[2,1]', 'x[2,2]']))

    def test2c(self):
        # Test fixed attribute - 2D
        m = ConcreteModel()
        m.x = Var(range(3), range(3), dense=True)

        names = set()
        for var in m.x[3, :]:
            names.add(var.cname(True))
        self.assertEqual(names, set())

    def test3a(self):
        # Test fixed attribute - 3D
        m = ConcreteModel()
        m.x = Var(range(3), range(3), range(3), dense=True)

        names = set()
        for var in m.x[:, 1, :]:
            names.add(var.cname(True))
        self.assertEqual(names, set(['x[0,1,0]', 'x[0,1,1]', 'x[0,1,2]', 'x[1,1,0]', 'x[1,1,1]', 'x[1,1,2]', 'x[2,1,0]', 'x[2,1,1]', 'x[2,1,2]' ]))

    def test3b(self):
        # Test fixed attribute - 3D
        m = ConcreteModel()
        m.x = Var(range(3), range(3), range(3), dense=True)

        names = set()
        for var in m.x[0, :, 2]:
            names.add(var.cname(True))
        self.assertEqual(names, set(['x[0,0,2]', 'x[0,1,2]', 'x[0,2,2]']))


class TestComponentSlices(unittest.TestCase):
    def setUp(self):
        def _c(b, i, j):
            b.x = Var(b.model().K)

        def _b(b, i, j):
            _c(b,i,j)
            b.c = Block(b.model().I, b.model().J, rule=_c)

        self.m = m = ConcreteModel()
        m.I = RangeSet(1,3)
        m.J = RangeSet(4,6)
        m.K = RangeSet(7,9)
        m.b = Block(m.I, m.J, rule=_b)

    def tearDown(self):
        self.m = None

    def test_simple_getitem(self):
        self.assertTrue(isinstance(self.m.b[1,4], _BlockData))

    def test_simple_getslice(self):
        _slicer = self.m.b[:,4]
        self.assertTrue(isinstance(_slicer, _IndexedComponent_slicer))
        ans = [ str(x) for x in _slicer ]
        self.assertEqual(
            ans, ['b[1,4]', 'b[2,4]', 'b[3,4]'] )

        _slicer = self.m.b[1,4].c[:,4]
        self.assertTrue(isinstance(_slicer, _IndexedComponent_slicer))
        ans = [ str(x) for x in _slicer ]
        self.assertEqual(
            ans, ['b[1,4].c[1,4]', 'b[1,4].c[2,4]', 'b[1,4].c[3,4]'] )

    def test_nonterminal_slice(self):
        _slicer = self.m.b[:,4].x
        self.assertTrue(isinstance(_slicer, _IndexedComponent_slicer))
        ans = [ str(x) for x in _slicer ]
        self.assertEqual(
            ans, ['b[1,4].x', 'b[2,4].x', 'b[3,4].x'] )

        _slicer = self.m.b[:,4].x[7]
        self.assertTrue(isinstance(_slicer, _IndexedComponent_slicer))
        ans = [ str(x) for x in _slicer ]
        self.assertEqual(
            ans, ['b[1,4].x[7]', 'b[2,4].x[7]', 'b[3,4].x[7]'] )

    def test_nested_slices(self):
        _slicer = self.m.b[1,:].c[:,4].x
        self.assertTrue(isinstance(_slicer, _IndexedComponent_slicer))
        ans = [ str(x) for x in _slicer ]
        self.assertEqual(
            ans, ['b[1,4].c[1,4].x', 'b[1,4].c[2,4].x', 'b[1,4].c[3,4].x',
                  'b[1,5].c[1,4].x', 'b[1,5].c[2,4].x', 'b[1,5].c[3,4].x',
                  'b[1,6].c[1,4].x', 'b[1,6].c[2,4].x', 'b[1,6].c[3,4].x',
              ] )

        _slicer = self.m.b[1,:].c[:,4].x[8]
        self.assertTrue(isinstance(_slicer, _IndexedComponent_slicer))
        ans = [ str(x) for x in _slicer ]
        self.assertEqual(
            ans,
            [ 'b[1,4].c[1,4].x[8]', 'b[1,4].c[2,4].x[8]', 'b[1,4].c[3,4].x[8]',
              'b[1,5].c[1,4].x[8]', 'b[1,5].c[2,4].x[8]', 'b[1,5].c[3,4].x[8]',
              'b[1,6].c[1,4].x[8]', 'b[1,6].c[2,4].x[8]', 'b[1,6].c[3,4].x[8]',
               ] )

    def test_empty_slices(self):
        _slicer = self.m.b[1,:].c[:,1].x
        self.assertTrue(isinstance(_slicer, _IndexedComponent_slicer))
        ans = [ str(x) for x in _slicer ]
        self.assertEqual( ans, [] )

        _slicer = self.m.b[1,:].c[:,4].x[1]
        self.assertTrue(isinstance(_slicer, _IndexedComponent_slicer))
        ans = [ str(x) for x in _slicer ]
        self.assertEqual( ans, [] )

        _slicer = self.m.b[1,:].c[:,4].y
        self.assertTrue(isinstance(_slicer, _IndexedComponent_slicer))
        ans = [ str(x) for x in _slicer ]
        self.assertEqual( ans, [] )

        _slicer = self.m.b[1,:].c[:,4].y
        self.assertTrue(isinstance(_slicer, _IndexedComponent_slicer))
        _slicer.attribute_errors_generate_exceptions = True
        self.assertRaises( AttributeError, _slicer.next )

        _slicer = self.m.b[1,:].c[:,4].x[1]
        self.assertTrue(isinstance(_slicer, _IndexedComponent_slicer))
        _slicer.key_errors_generate_exceptions = True
        self.assertRaises( KeyError, _slicer.next )


if __name__ == "__main__":
    unittest.main()
