# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from datetime import datetime
from firstlight.flspautomation.product import FlspProductAutomation
from firstlight.flspautomation.purchase import FlspPurchaseAutomation
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
        self.purchase_auto = FlspPurchaseAutomation(self) 
        self.stock_auto = FlspStockAutomation(self) 
        
    def test_flsp_status_cancel_before_shipped(self):
        # test flsp_status when user cancels the PO just before shipping and confirm the PO after shipping
        tc_name = 'test_flsp_status_cancel_before_shipped'

        # prepare test data
        prod_1 = self.product_auto.create_typical_product(tc_name, 1.3, 5)
        po_1 = self.purchase_auto.create_simple_purchase_order(tc_name)
        pol_1 = self.purchase_auto.create_simple_purchase_order_line(tc_name, po_1.id, prod_1, 15)
        location_1 = self.stock_auto.create_location(tc_name, tc_name, 'internal', False)
        location_2 = self.stock_auto.create_location(tc_name, tc_name, 'internal', False)
        sp_1 =  self.stock_auto.create_stock_picking(location_1.id, location_2.id, po_1, 1)
        stock_move =  self.stock_auto.create_stock_move(tc_name, prod_1.id, sp_1.location_id.id, sp_1.location_dest_id.id, sp_1.id, pol_1.product_qty, pol_1.id)
        move_line =  self.stock_auto.create_stock_move_line(stock_move.location_id.id, stock_move.location_dest_id.id, sp_1.id, prod_1, pol_1.product_qty)

        # run the case and verify
        # confirm PO in normal steps
        po_1.state = 'purchase'
        po_1.flsp_po_status = 'confirmed'
        po_1.flsp_vendor_confirmation_date = datetime.now()
        self.assertEquals(po_1.state, 'purchase', 'state=purchase')
        self.assertEquals(po_1.is_shipped, False, 'is_shipped=False')
        self.assertEquals(po_1.flsp_po_status, 'confirmed', 'flsp_po_status=confirmed')

        # cancel PO by clicking button "Cancel" which calls button_cancel()
        po_1.button_cancel()
        self.assertEquals(po_1.state, 'cancel', 'state=cancel')
        self.assertEquals(po_1.is_shipped, False, 'is_shipped=False')
        self.assertEquals(po_1.flsp_po_status, 'cancelled', 'flsp_po_status=cancelled')

        # close stock.picking
        sp_1.button_validate()
        sp_1.state = 'done'
        self.assertEquals(po_1.state, 'cancel', 'state=cancel')
        self.assertEquals(po_1.is_shipped, True, 'is_shipped=True')
        self.assertEquals(po_1.flsp_po_status, 'cancelled', 'flsp_po_status=cancelled')

        # reopen PO by clicking button "Set to Draft" which calls button_draft()
        po_1.button_draft()
        self.assertEquals(po_1.state, 'draft', 'state=draft')
        self.assertEquals(po_1.is_shipped, True, 'is_shipped=True')
        self.assertEquals(po_1.flsp_po_status, 'request', 'flsp_po_status=request')

        # reset PO by clicking button "Confirm Order" which calls button_confirm()
        po_1.button_confirm()
        self.assertEquals(po_1.state, 'purchase', 'state=purchase')
        self.assertEquals(po_1.is_shipped, True, 'is_shipped=True')
        self.assertEquals(po_1.flsp_po_status, 'received', 'flsp_po_status=received')
        
        # add info to make sure the test case is done
        _logger.info(tc_name + "() is done.") 
        
    def test_flsp_status_cancel_before_shipped_1(self):
        # test flsp_status when user cancels the PO just before shipping and confirm the PO after shipping, with set flsp_vendor_confirmation_date later than confirmation
        tc_name = 'test_flsp_status_cancel_before_shipped_1'

        # prepare test data
        prod_1 = self.product_auto.create_typical_product(tc_name, 1.3, 5)
        po_1 = self.purchase_auto.create_simple_purchase_order(tc_name)
        pol_1 = self.purchase_auto.create_simple_purchase_order_line(tc_name, po_1.id, prod_1, 3)
        location_1 = self.stock_auto.create_location(tc_name, tc_name, 'internal', False)
        location_2 = self.stock_auto.create_location(tc_name, tc_name, 'internal', False)
        sp_1 =  self.stock_auto.create_stock_picking(location_1.id, location_2.id, po_1, 1)
        stock_move =  self.stock_auto.create_stock_move(tc_name, prod_1.id, sp_1.location_id.id, sp_1.location_dest_id.id, sp_1.id, pol_1.product_qty, pol_1.id)
        move_line =  self.stock_auto.create_stock_move_line(stock_move.location_id.id, stock_move.location_dest_id.id, sp_1.id, prod_1, pol_1.product_qty)

        # run the case and verify
        # confirm PO in normal steps
        po_1.state = 'purchase'
        po_1.flsp_po_status = 'confirmed'
        self.assertEquals(po_1.state, 'purchase', 'state=purchase')
        self.assertEquals(po_1.is_shipped, False, 'is_shipped=False')
        self.assertEquals(po_1.flsp_po_status, 'confirmed', 'flsp_po_status=confirmed')

        # cancel PO by clicking button "Cancel" which calls button_cancel()
        po_1.button_cancel()
        self.assertEquals(po_1.state, 'cancel', 'state=cancel')
        self.assertEquals(po_1.is_shipped, False, 'is_shipped=False')
        self.assertEquals(po_1.flsp_po_status, 'cancelled', 'flsp_po_status=cancelled')

        # close stock.picking
        sp_1.button_validate()
        sp_1.state = 'done'
        self.assertEquals(po_1.state, 'cancel', 'state=cancel')
        self.assertEquals(po_1.is_shipped, True, 'is_shipped=True')
        self.assertEquals(po_1.flsp_po_status, 'cancelled', 'flsp_po_status=cancelled')

        # reopen PO by clicking button "Set to Draft" which calls button_draft()
        po_1.button_draft()
        self.assertEquals(po_1.state, 'draft', 'state=draft')
        self.assertEquals(po_1.is_shipped, True, 'is_shipped=True')
        self.assertEquals(po_1.flsp_po_status, 'request', 'flsp_po_status=request')

        # reset PO by clicking button "Confirm Order" which calls button_confirm()
        po_1.button_confirm()
        self.assertEquals(po_1.state, 'purchase', 'state=purchase')
        self.assertEquals(po_1.is_shipped, True, 'is_shipped=True')
        self.assertEquals(po_1.flsp_po_status, 'non_confirmed', 'flsp_po_status=received')
        
        # set flsp_vendor_confirmation_date in PO
        po_1.flsp_vendor_confirmation_date = datetime.now()
        po_1._change_status_to_confirmed() # the method has to been called here because it is invoked on UI change.
        self.assertEquals(po_1.state, 'purchase', 'state=purchase')
        self.assertEquals(po_1.is_shipped, True, 'is_shipped=True')
        self.assertEquals(po_1.flsp_po_status, 'received', 'flsp_po_status=received')
        
        # add info to make sure the test case is done
        _logger.info(tc_name + "() is done.")