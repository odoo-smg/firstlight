# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from firstlight.flspautomation.product import FlspProductAutomation
from firstlight.flspautomation.stock import FlspStockAutomation

import logging
_logger = logging.getLogger(__name__)

@tagged('flsp', 'flspmodel', '-standard')
class TestStockQuant(TransactionCase):
    
    def setUp(self):
        """ set up for all test cases """
        # call parent setUp()adge(self):
        super(TestStockQuant, self).setUp()
        # create referred models used in test cases
        # self.stock_quant = self.env['stock.quant']
        self.product_auto = FlspProductAutomation(self)
        self.stock_auto = FlspStockAutomation(self)
        
    def test_stock_qty(self):
        # test when user inputs different kinds of INVALID 'package_id' in the sql in the method

        # prepare test data
        prod_1 = self.product_auto.create_typical_product('test_stock_qty', 1.3, 5)
        location_1 = self.stock_auto.create_location('test_stock_qty', 'test_stock_qty', 'internal', False)
        lot_1 = self.stock_auto.create_lot('test_stock_qty', prod_1.id)
        sq_1 = self.stock_auto.create_stock_quant(prod_1.id, location_1.id, lot_1.id, False, 7)

        # call the method and verify
        qty_1 = sq_1.get_flsp_stock_quantity(prod_1, location_1, lot_1, False)
        self.assertEquals(7.0, qty_1, "qty_1")

        qty_2 = sq_1.get_flsp_stock_quantity(prod_1, location_1, lot_1, None)
        self.assertEquals(7.0, qty_2, "qty_2")

        qty_3 = sq_1.get_flsp_stock_quantity(prod_1, location_1, lot_1)
        self.assertEquals(7.0, qty_3, "qty_3")

        qty_4 = sq_1.get_flsp_stock_quantity(prod_1, location_1, lot_1, '')
        self.assertEquals(7.0, qty_4, "qty_4")

        self.assertRaises(AttributeError, sq_1.get_flsp_stock_quantity, prod_1, location_1, lot_1, 'invald_value')
        
        # add info to make sure the test case is done
        _logger.info("test_stock_qty() is done.")
        
        
    def test_stock_qty_1(self):
        # test when user inputs different kinds of valid 'package_id' and 'lot_id' in the method

        # prepare test data
        prod_1 = self.product_auto.create_typical_product('test_stock_qty_1', 1.3, 5)
        location_1 = self.stock_auto.create_location('test_stock_qty_1', 'test_stock_qty', 'internal', False)
        lot_1 = self.stock_auto.create_lot('test_stock_qty_1', prod_1.id)
        lot_2 = self.stock_auto.create_lot('test_stock_qty_1', prod_1.id)
        pack_1 = self.stock_auto.create_package('test_stock_qty_1')
        pack_2 = self.stock_auto.create_package('test_stock_qty_1')
        pack_3 = self.stock_auto.create_package('test_stock_qty_1')
        sq_1 = self.stock_auto.create_stock_quant(prod_1.id, location_1.id, lot_1.id, pack_1.id, 7)
        sq_2 = self.stock_auto.create_stock_quant(prod_1.id, location_1.id, lot_1.id, pack_2.id, 8)
        sq_3 = self.stock_auto.create_stock_quant(prod_1.id, location_1.id, lot_2.id, pack_1.id, 9)

        # call the method and verify
        qty_1 = sq_1.get_flsp_stock_quantity(prod_1, location_1, lot_1, pack_1)
        self.assertEquals(7.0, qty_1, "qty_1")

        qty_2 = sq_1.get_flsp_stock_quantity(prod_1, location_1, lot_1, pack_2)
        self.assertEquals(8.0, qty_2, "qty_2")

        qty_3 = sq_1.get_flsp_stock_quantity(prod_1, location_1, lot_2, pack_1)
        self.assertEquals(9.0, qty_3, "qty_3")

        qty_4 = sq_1.get_flsp_stock_quantity(prod_1, location_1, lot_1)
        self.assertEquals(7 + 8, qty_4, "qty_4")

        qty_4_1 = sq_1.get_flsp_stock_quantity(prod_1, location_1, lot_id=lot_1)
        self.assertEquals(7 + 8, qty_4_1, "qty_4_1")

        qty_5 = sq_1.get_flsp_stock_quantity(prod_1, location_1, package_id=pack_1)
        self.assertEquals(7 + 9, qty_5, "qty_5")

        # no record for pack_3
        qty_5_1 = sq_1.get_flsp_stock_quantity(prod_1, location_1, package_id=pack_3)
        self.assertEquals(0, qty_5_1, "qty_5_1")

        qty_6 = sq_1.get_flsp_stock_quantity(prod_1, location_1)
        self.assertEquals(24.0, qty_6, "qty_6")
        
        # add info to make sure the test case is done
        _logger.info("test_stock_qty_1() is done.")