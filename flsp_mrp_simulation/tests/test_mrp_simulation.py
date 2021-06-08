# -*- coding: utf-8 -*-

from odoo.tests import Form
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from datetime import date, datetime
from odoo.tools import float_compare

import logging
_logger = logging.getLogger(__name__)

@tagged('flsp', 'flspmodel', '-standard')
class TestOnMrpSimulation(TransactionCase):
    
    def setUp(self):
        """ set up for all test cases """
        # call parent setUp()adge(self):
        super(TestOnMrpSimulation, self).setUp()
        # create referred models used in test cases
        self.mrp_simulation_model = self.env['flsp.mrp.simulation']
        self.mrp_simulatd_product_model = self.env['flsp.mrp.simulated.product']
        self.mrp_sub_product_model = self.env['flsp.mrp.sub.product']
        self.product_product_model = self.env['product.product']
        self.product_tmpl_model = self.env['product.template']
        self.mrp_bom_model = self.env['mrp.bom']
        self.mrp_bom_line_model = self.env['mrp.bom.line']
        self.category_model = self.env['product.category']
        self.uom_model = self.env['uom.uom']
        self.tax_model = self.env['account.tax']
        self.stock_quant = self.env['stock.quant']

    def create_product_tmpl(self, name, type, categ_id, uom_id, uom_po_id, tracking, standard_price, sale_line_warn, purchase_line_warn):
       return self.product_tmpl_model.create(dict(
                        name=name,
                        type=type,
                        categ_id=categ_id,
                        uom_id=uom_id,
                        uom_po_id=uom_po_id,
                        tracking=tracking,
                        standard_price=standard_price,
                        sale_line_warn=sale_line_warn,
                        purchase_line_warn=purchase_line_warn,
                        ))
        
    def create_product(self, default_code, name, cost, onhand_qty):
        prod_template = self.create_product_tmpl(name, 'product', 8, 1, 1, 'none', cost, 'no-message', 'no-message')
        p = prod_template.product_variant_ids[0]
        p.default_code = default_code
        p.active = True

        self.stock_quant.create(dict(
                        product_id=p.id,
                        location_id=8,
                        quantity=onhand_qty,
                        reserved_quantity=0,
                        ))
        return p
        
    def create_typical_product(self, cost, onhand_qty):
        postfix = str(datetime.now())
        aName = 'prod-simulation-' + postfix
        default_code = 'code-simulation-' + postfix
        return self.create_product(default_code, aName, cost, onhand_qty)
        
    def create_bom(self, product):
        return self.mrp_bom_model.create({
                        'code': product.name + "_bom",
                        'active': True,
                        'type': 'normal',
                        'product_tmpl_id': product.product_tmpl_id.id,
                        'product_id': product.id,
                        'product_qty': 1,
                        'product_uom_id': 1,
                        'ready_to_produce': 'asap',
                })
        
    def create_bom_lines(self, bom, bom_lines):
        for line in bom_lines:
            self.mrp_bom_line_model.create({
                        'product_id': line["product_id"],
                        'product_qty': line["qty"],
                        'product_uom_id': 1,
                        'bom_id': bom.id,
                })
        
    def create_simulation_product(self, cost, onhand_qty, bom_lines):
        prod = self.create_typical_product(cost, onhand_qty)
        bom = False
        if bom_lines:
            bom = self.create_bom(prod)
            self.create_bom_lines(bom, bom_lines)
        return prod
        
    def create_mrp_simulation(self, missed_only):
        postfix = str(datetime.now())
        aName = 'simulation-' + postfix
        return self.mrp_simulation_model.create({
                        'name': aName,
                        'missed_only': missed_only,
                })
        
    def create_mrp_simulated_product(self, simulation_id, prod_id, required_qty):
        return self.mrp_simulatd_product_model.create({
                        'simulation_id': simulation_id,
                        'product_id': prod_id,
                        'required_qty': required_qty,
                })
        
    def test_simulation_product_without_bom(self):
        # prepare test data
        cost = 1.2
        onhand_qty = 2
        required_qty = 1
        prod_1 = self.create_simulation_product(cost, onhand_qty, False)

        s_1 = self.create_mrp_simulation(False)
        self.create_mrp_simulated_product(s_1.id, prod_1.id, required_qty)

        # call the method
        s_1.button_calculate_sub_products()
        
        # validate the result
        self.assertEquals(s_1.total_onhand_value, cost * onhand_qty, "total_onhand_value")
        self.assertEquals(s_1.total_value_needed, 0, "total_value_needed")

        self.assertEquals(len(s_1.sub_products), 1, "sub_products.len")
        p_1 = s_1.sub_products[0]
        self.assertEquals(p_1.product_id.id, prod_1.id, "sub_products[0].id")
        self.assertEquals(p_1.required_qty, required_qty, "sub_product.required_qty")
        self.assertEquals(p_1.onhand_qty, onhand_qty, "sub_product.onhand_qty")
        self.assertEquals(p_1.diff_qty, onhand_qty - required_qty, "sub_product.diff_qty")
        self.assertEquals(p_1.cost, cost, "sub_product.cost")

        self.assertEquals(len(s_1.missed_sub_products), 0, "missed_sub_products.len")
        
        # add info to make sure the test case is done
        _logger.info("test_simulation_product_without_bom() is done.")
        
    def test_simulation_product_without_bom_1(self):
        # prepare test data
        cost = 1.2
        onhand_qty = 2
        required_qty = 2
        prod_1 = self.create_simulation_product(cost, onhand_qty, False)

        s_1 = self.create_mrp_simulation(False)
        self.create_mrp_simulated_product(s_1.id, prod_1.id, required_qty)

        # call the method
        s_1.button_calculate_sub_products()
        
        # validate the result
        self.assertEquals(s_1.total_onhand_value, cost * onhand_qty, "total_onhand_value")
        self.assertEquals(s_1.total_value_needed, 0, "total_value_needed")

        self.assertEquals(len(s_1.sub_products), 1, "sub_products.len")
        p_1 = s_1.sub_products[0]
        self.assertEquals(p_1.product_id.id, prod_1.id, "sub_products[0].id")
        self.assertEquals(p_1.required_qty, required_qty, "sub_product.required_qty")
        self.assertEquals(p_1.onhand_qty, onhand_qty, "sub_product.onhand_qty")
        self.assertEquals(p_1.diff_qty, onhand_qty - required_qty, "sub_product.diff_qty")
        self.assertEquals(p_1.cost, cost, "sub_product.cost")

        self.assertEquals(len(s_1.missed_sub_products), 0, "missed_sub_products.len")
        
        # add info to make sure the test case is done
        _logger.info("test_simulation_product_without_bom_1() is done.")
        
    def test_simulation_product_without_bom_2(self):
        # prepare test data
        cost = 1.2
        onhand_qty = 2
        required_qty = 3
        prod_1 = self.create_simulation_product(cost, onhand_qty, False)

        s_1 = self.create_mrp_simulation(False)
        self.create_mrp_simulated_product(s_1.id, prod_1.id, required_qty)

        # call the method
        s_1.button_calculate_sub_products()
        
        # validate the result
        self.assertEquals(s_1.total_onhand_value, cost * onhand_qty, "total_onhand_value")
        self.assertEquals(s_1.total_value_needed, 1.2, "total_value_needed")

        self.assertEquals(len(s_1.sub_products), 1, "sub_products.len")
        p_1 = s_1.sub_products[0]
        self.assertEquals(p_1.product_id.id, prod_1.id, "sub_products[0].id")
        self.assertEquals(p_1.required_qty, required_qty, "sub_product.required_qty")
        self.assertEquals(p_1.onhand_qty, onhand_qty, "sub_product.onhand_qty")
        self.assertEquals(p_1.diff_qty, onhand_qty - required_qty, "sub_product.diff_qty")
        self.assertEquals(p_1.cost, cost, "sub_product.cost")

        self.assertEquals(len(s_1.missed_sub_products), 1, "missed_sub_products.len")
        p_2 = s_1.missed_sub_products[0]
        self.assertEquals(p_2.product_id.id, prod_1.id, "missed_sub_products[0].id")
        self.assertEquals(p_2.diff_qty, -1, "missed_sub_products[0].id")
        
        # add info to make sure the test case is done
        _logger.info("test_simulation_product_without_bom_2() is done.")

    def test_simulation_product_with_bom(self):
        # onhand_qty in stock meets the required qty 
        onhand_qty = 2
        required_qty = 1

        # prepare test data
        prod_1 = self.create_simulation_product(2.7, 3, False)
        prod_2 = self.create_simulation_product(5.1, 100, False)
        # prod_3 can be broken down as 1 x prod_1 and 3 x prod_2
        bom_lines = [{"product_id": prod_1.id, "qty": 1}, {"product_id": prod_2.id, "qty": 3}]
        prod_3 = self.create_simulation_product(20.3, onhand_qty, bom_lines)

        s_1 = self.create_mrp_simulation(False)
        self.create_mrp_simulated_product(s_1.id, prod_3.id, required_qty)

        # call the method
        s_1.button_calculate_sub_products()
        
        # validate the result
        self.assertEquals(s_1.total_onhand_value, 40.6, "total_onhand_value")
        self.assertEquals(s_1.total_value_needed, 0, "total_value_needed")

        self.assertEquals(len(s_1.sub_products), 1, "sub_products.len")
        p_1 = s_1.sub_products[0]
        self.assertEquals(p_1.product_id.id, prod_3.id, "sub_products[0].id")
        self.assertEquals(p_1.required_qty, required_qty, "sub_product.required_qty")
        self.assertEquals(p_1.onhand_qty, onhand_qty, "sub_product.onhand_qty")
        self.assertEquals(p_1.diff_qty, 1, "sub_product.diff_qty")

        self.assertEquals(len(s_1.missed_sub_products), 0, "missed_sub_products.len")

        self.assertEquals(len(s_1.simulated_products), 1, "simulated_products.len")
        sp_1 = s_1.simulated_products[0]
        self.assertEquals(sp_1.product_id.id, prod_3.id, "simulated_products[0].id")
        self.assertEquals(sp_1.required_qty, required_qty, "simulated_products.required_qty")
        self.assertEquals(sp_1.onhand_qty, onhand_qty, "simulated_products.onhand_qty")
        self.assertEquals(sp_1.bom_cost, 2.7 + 5.1 * 3, "simulated_products.bom_cost")
        
        # add info to make sure the test case is done
        _logger.info("test_simulation_product_without_bom() is done.")
        
    def test_simulation_product_with_bom_1(self):
        # onhand_qty in stock meets the required qty 
        onhand_qty = 2
        required_qty = 2

        # prepare test data
        prod_1 = self.create_simulation_product(2.7, 3, False)
        prod_2 = self.create_simulation_product(5.1, 100, False)
        # prod_3 can be broken down as 1 x prod_1 and 3 x prod_2
        bom_lines = [{"product_id": prod_1.id, "qty": 1}, {"product_id": prod_2.id, "qty": 3}]
        prod_3 = self.create_simulation_product(20.3, onhand_qty, bom_lines)

        s_1 = self.create_mrp_simulation(False)
        self.create_mrp_simulated_product(s_1.id, prod_3.id, required_qty)

        # call the method
        s_1.button_calculate_sub_products()
        
        # validate the result
        self.assertEquals(s_1.total_onhand_value, 40.6, "total_onhand_value")
        self.assertEquals(s_1.total_value_needed, 0, "total_value_needed")

        self.assertEquals(len(s_1.sub_products), 1, "sub_products.len")
        p_1 = s_1.sub_products[0]
        self.assertEquals(p_1.product_id.id, prod_3.id, "sub_products[0].id")
        self.assertEquals(p_1.required_qty, required_qty, "sub_product.required_qty")
        self.assertEquals(p_1.onhand_qty, onhand_qty, "sub_product.onhand_qty")
        self.assertEquals(p_1.diff_qty, 0, "sub_product.diff_qty")

        self.assertEquals(len(s_1.missed_sub_products), 0, "missed_sub_products.len")
        
        # add info to make sure the test case is done
        _logger.info("test_simulation_product_with_bom_1() is done.")

    def test_simulation_product_with_bom_2(self):
        # onhand_qty in stock does not meet the required qty 
        onhand_qty = 2
        required_qty = 3

        # prepare test data
        prod_1 = self.create_simulation_product(2.7, 3, False)
        prod_2 = self.create_simulation_product(5.1, 100, False)
        # prod_3 can be broken down as 1 x prod_1 and 3 x prod_2
        bom_lines = [{"product_id": prod_1.id, "qty": 1}, {"product_id": prod_2.id, "qty": 3}]
        prod_3 = self.create_simulation_product(20.3, onhand_qty, bom_lines)

        s_1 = self.create_mrp_simulation(False)
        self.create_mrp_simulated_product(s_1.id, prod_3.id, required_qty)

        # call the method
        s_1.button_calculate_sub_products()
        
        # validate the result
        self.assertEquals(s_1.total_onhand_value, 40.6, "total_onhand_value")
        self.assertEquals(s_1.total_value_needed, 0, "total_value_needed")

        self.assertEquals(len(s_1.sub_products), 3, "sub_products.len")
        p_0 = s_1.sub_products[0]
        self.assertEquals(p_0.product_id.id, prod_3.id, "sub_products[0].id")
        self.assertEquals(p_0.required_qty, onhand_qty, "sub_product.required_qty")
        self.assertEquals(p_0.onhand_qty, onhand_qty, "sub_product.onhand_qty")
        self.assertEquals(p_0.diff_qty, 0, "sub_product.diff_qty")
        p_1 = s_1.sub_products[1]
        self.assertEquals(p_1.product_id.id, prod_1.id, "sub_products[1].id")
        self.assertEquals(p_1.required_qty, 1, "sub_product.required_qty")
        self.assertEquals(p_1.onhand_qty, 3, "sub_product.onhand_qty")
        self.assertEquals(p_1.diff_qty, 2, "sub_product.diff_qty")
        p_2 = s_1.sub_products[2]
        self.assertEquals(p_2.product_id.id, prod_2.id, "sub_products[2].id")
        self.assertEquals(p_2.required_qty, 3, "sub_product.required_qty")
        self.assertEquals(p_2.onhand_qty, 100, "sub_product.onhand_qty")
        self.assertEquals(p_2.diff_qty, 97, "sub_product.diff_qty")


        self.assertEquals(len(s_1.missed_sub_products), 0, "missed_sub_products.len")
        
        # add info to make sure the test case is done
        _logger.info("test_simulation_product_with_bom_2() is done.")

    def test_simulation_product_with_bom_3(self):
        # onhand_qty in stock does not meet the required qty with medium gap
        onhand_qty = 2
        required_qty = 10

        # prepare test data
        prod_1 = self.create_simulation_product(2.7, 3, False)
        prod_2 = self.create_simulation_product(5.1, 100, False)
        # prod_3 can be broken down as 1 x prod_1 and 3 x prod_2
        bom_lines = [{"product_id": prod_1.id, "qty": 1}, {"product_id": prod_2.id, "qty": 3}]
        prod_3 = self.create_simulation_product(20.3, onhand_qty, bom_lines)

        s_1 = self.create_mrp_simulation(False)
        self.create_mrp_simulated_product(s_1.id, prod_3.id, required_qty)

        # call the method
        s_1.button_calculate_sub_products()
        
        # validate the result
        self.assertEquals(s_1.total_onhand_value, 40.6, "total_onhand_value")
        self.assertEquals(s_1.total_value_needed, 13.5, "total_value_needed")

        self.assertEquals(len(s_1.sub_products), 3, "sub_products.len")
        p_0 = s_1.sub_products[0]
        self.assertEquals(p_0.product_id.id, prod_3.id, "sub_products[0].id")
        self.assertEquals(p_0.required_qty, onhand_qty, "sub_product.required_qty")
        self.assertEquals(p_0.onhand_qty, onhand_qty, "sub_product.onhand_qty")
        self.assertEquals(p_0.diff_qty, 0, "sub_product.diff_qty")
        p_1 = s_1.sub_products[1]
        self.assertEquals(p_1.product_id.id, prod_1.id, "sub_products[1].id")
        self.assertEquals(p_1.required_qty, 8, "sub_product.required_qty")
        self.assertEquals(p_1.onhand_qty, 3, "sub_product.onhand_qty")
        self.assertEquals(p_1.diff_qty, -5, "sub_product.diff_qty")
        p_2 = s_1.sub_products[2]
        self.assertEquals(p_2.product_id.id, prod_2.id, "sub_products[2].id")
        self.assertEquals(p_2.required_qty, 24, "sub_product.required_qty")
        self.assertEquals(p_2.onhand_qty, 100, "sub_product.onhand_qty")
        self.assertEquals(p_2.diff_qty, 76, "sub_product.diff_qty")


        self.assertEquals(len(s_1.missed_sub_products), 1, "missed_sub_products.len")
        sp_0 = s_1.missed_sub_products[0]
        self.assertEquals(sp_0.product_id.id, prod_1.id, "missed_sub_products[0].id")
        self.assertEquals(sp_0.diff_qty, -5, "missed_sub_products[0].id")
        
        # add info to make sure the test case is done
        _logger.info("test_simulation_product_with_bom_3() is done.")

    def test_simulation_product_with_bom_4(self):
        # onhand_qty in stock does not meet the required qty with large gap
        onhand_qty = 2
        required_qty = 40

        # prepare test data
        prod_1 = self.create_simulation_product(2.7, 3, False)
        prod_2 = self.create_simulation_product(5.1, 100, False)
        # prod_3 can be broken down as 1 x prod_1 and 3 x prod_2
        bom_lines = [{"product_id": prod_1.id, "qty": 1}, {"product_id": prod_2.id, "qty": 3}]
        prod_3 = self.create_simulation_product(20.3, onhand_qty, bom_lines)

        s_1 = self.create_mrp_simulation(False)
        self.create_mrp_simulated_product(s_1.id, prod_3.id, required_qty)

        # call the method
        s_1.button_calculate_sub_products()
        
        # validate the result
        self.assertEquals(s_1.total_onhand_value, 40.6, "total_onhand_value")
        self.assertEquals(s_1.total_value_needed, 165.9, "total_value_needed") # 2.7 * 35 + 5.1 * 14 = 94.5 + 71.4 = 165.9

        self.assertEquals(len(s_1.sub_products), 3, "sub_products.len")
        p_0 = s_1.sub_products[0]
        self.assertEquals(p_0.product_id.id, prod_3.id, "sub_products[0].id")
        self.assertEquals(p_0.required_qty, onhand_qty, "sub_product.required_qty")
        self.assertEquals(p_0.onhand_qty, onhand_qty, "sub_product.onhand_qty")
        self.assertEquals(p_0.diff_qty, 0, "sub_product.diff_qty")
        p_1 = s_1.sub_products[1]
        self.assertEquals(p_1.product_id.id, prod_1.id, "sub_products[1].id")
        self.assertEquals(p_1.required_qty, 38, "sub_product.required_qty")
        self.assertEquals(p_1.onhand_qty, 3, "sub_product.onhand_qty")
        self.assertEquals(p_1.diff_qty, -35, "sub_product.diff_qty")
        p_2 = s_1.sub_products[2]
        self.assertEquals(p_2.product_id.id, prod_2.id, "sub_products[2].id")
        self.assertEquals(p_2.required_qty, 114, "sub_product.required_qty") # (40-2) * 3
        self.assertEquals(p_2.onhand_qty, 100, "sub_product.onhand_qty")
        self.assertEquals(p_2.diff_qty, -14, "sub_product.diff_qty")

        self.assertEquals(len(s_1.missed_sub_products), 2, "missed_sub_products.len")
        sp_0 = s_1.missed_sub_products[0]
        self.assertEquals(sp_0.product_id.id, prod_1.id, "missed_sub_products[0].id")
        self.assertEquals(sp_0.diff_qty, -35, "missed_sub_products.id")
        sp_1 = s_1.missed_sub_products[1]
        self.assertEquals(sp_1.product_id.id, prod_2.id, "missed_sub_products[1].id")
        self.assertEquals(sp_1.diff_qty, -14, "missed_sub_products.id")
        
        # add info to make sure the test case is done
        _logger.info("test_simulation_product_with_bom_4() is done.")
        
    def test_mutiple_simulation_products_with_bom(self):
        # onhand_qty in stock does not meet the required qty

        # prepare test data
        prod_1 = self.create_simulation_product(2.7, 3, False)
        prod_2 = self.create_simulation_product(5.1, 100, False)
        # prod_3 can be broken down as 1 x prod_1 and 3 x prod_2
        # prod_3, onhand_qty=2, required_qty=5
        bom_lines_3 = [{"product_id": prod_1.id, "qty": 1}, {"product_id": prod_2.id, "qty": 3}]
        prod_3 = self.create_simulation_product(20.3, 2, bom_lines_3)
        s_1 = self.create_mrp_simulation(False)
        self.create_mrp_simulated_product(s_1.id, prod_3.id, 5)

        prod_4 = self.create_simulation_product(7, 1, False)
        # prod_5 can be broken down as 2 x prod_1, 1 x prod_3  and 2 x prod_4
        # prod_5, onhand_qty=10, required_qty=11
        bom_lines_5 = [{"product_id": prod_1.id, "qty": 2}, {"product_id": prod_3.id, "qty": 1}, {"product_id": prod_4.id, "qty": 2}]
        prod_5 = self.create_simulation_product(65, 10, bom_lines_5)
        self.create_mrp_simulated_product(s_1.id, prod_5.id, 11)

        # call the method
        s_1.button_calculate_sub_products()
        
        # validate the result
        self.assertEquals(s_1.total_onhand_value, 20.3 * 2 + 65 * 10, "total_onhand_value") 
        # prod_1 2.7 * 3 + prod_4 7 * 1 = 15.1
        self.assertEquals(float_compare(s_1.total_value_needed, 15.1, precision_rounding=prod_5.product_tmpl_id.uom_id.rounding), 0, "total_value_needed")

        self.assertEquals(len(s_1.simulated_products), 2, "simulated_products.len")
        sp_0 = s_1.simulated_products[0]
        self.assertEquals(sp_0.product_id.id, prod_3.id, "simulated_products[0].id")
        self.assertEquals(sp_0.required_qty, 5, "simulated_products.required_qty")
        self.assertEquals(sp_0.onhand_qty, 2, "simulated_products.onhand_qty")
        self.assertEquals(sp_0.bom_cost, 2.7 + 5.1 * 3, "simulated_products.bom_cost")
        sp_1 = s_1.simulated_products[1]
        self.assertEquals(sp_1.product_id.id, prod_5.id, "simulated_products[1].id")
        self.assertEquals(sp_1.required_qty, 11, "simulated_products.required_qty")
        self.assertEquals(sp_1.onhand_qty, 10, "simulated_products.onhand_qty")
        self.assertEquals(sp_1.bom_cost, 2.7 * 2 + (2.7 + 5.1 * 3) * 1 + 7 * 2, "simulated_products.bom_cost")

        self.assertEquals(len(s_1.sub_products), 5, "sub_products.len")
        p_0 = s_1.sub_products[0]
        self.assertEquals(p_0.product_id.id, prod_3.id, "sub_products[0].id")
        self.assertEquals(p_0.required_qty, 2, "sub_product.required_qty")
        self.assertEquals(p_0.onhand_qty, 2, "sub_product.onhand_qty")
        self.assertEquals(p_0.diff_qty, 0, "sub_product.diff_qty")
        p_1 = s_1.sub_products[1]
        self.assertEquals(p_1.product_id.id, prod_5.id, "sub_products[1].id")
        self.assertEquals(p_1.required_qty, 10, "sub_product.required_qty")
        self.assertEquals(p_1.onhand_qty, 10, "sub_product.onhand_qty")
        self.assertEquals(p_1.diff_qty, 0, "sub_product.diff_qty")
        p_2 = s_1.sub_products[2]
        self.assertEquals(p_2.product_id.id, prod_1.id, "sub_products[2].id")
        self.assertEquals(p_2.required_qty, 6, "sub_product.required_qty")
        self.assertEquals(p_2.onhand_qty, 3, "sub_product.onhand_qty")
        self.assertEquals(p_2.diff_qty, -3, "sub_product.diff_qty")
        p_3 = s_1.sub_products[3]
        self.assertEquals(p_3.product_id.id, prod_2.id, "sub_products[2].id")
        self.assertEquals(p_3.required_qty, 12, "sub_product.required_qty") 
        self.assertEquals(p_3.onhand_qty, 100, "sub_product.onhand_qty")
        self.assertEquals(p_3.diff_qty, 88, "sub_product.diff_qty")
        p_4 = s_1.sub_products[4]
        self.assertEquals(p_4.product_id.id, prod_4.id, "sub_products[2].id")
        self.assertEquals(p_4.required_qty, 2, "sub_product.required_qty") 
        self.assertEquals(p_4.onhand_qty, 1, "sub_product.onhand_qty")
        self.assertEquals(p_4.diff_qty, -1, "sub_product.diff_qty")

        self.assertEquals(len(s_1.missed_sub_products), 2, "missed_sub_products.len")
        ssp_0 = s_1.missed_sub_products[0]
        self.assertEquals(ssp_0.product_id.id, prod_1.id, "missed_sub_products[0].id")
        self.assertEquals(ssp_0.diff_qty, -3, "missed_sub_products.id")
        ssp_1 = s_1.missed_sub_products[1]
        self.assertEquals(ssp_1.product_id.id, prod_4.id, "missed_sub_products[1].id")
        self.assertEquals(ssp_1.diff_qty, -1, "missed_sub_products.id")
        
        # add info to make sure the test case is done
        _logger.info("test_mutiple_simulation_products_with_bom() is done.")

    def test_mutiple_simulation_products_with_bom_1(self):
        # onhand_qty in stock does not meet the required qty, but prod_3 is met for the first time

        # prepare test data
        prod_1 = self.create_simulation_product(2.7, 3, False)
        prod_2 = self.create_simulation_product(5.1, 100, False)
        # prod_3 can be broken down as 1 x prod_1 and 3 x prod_2
        # prod_3, onhand_qty=4, required_qty=3
        bom_lines_3 = [{"product_id": prod_1.id, "qty": 1}, {"product_id": prod_2.id, "qty": 3}]
        prod_3 = self.create_simulation_product(20.3, 4, bom_lines_3)
        s_1 = self.create_mrp_simulation(False)
        self.create_mrp_simulated_product(s_1.id, prod_3.id, 3)

        prod_4 = self.create_simulation_product(7, 1, False)
        # prod_5 can be broken down as 2 x prod_1, 3 x prod_3 and 1 x prod_4
        # prod_5, onhand_qty=6, required_qty=8
        bom_lines_5 = [{"product_id": prod_1.id, "qty": 2}, {"product_id": prod_3.id, "qty": 3}, {"product_id": prod_4.id, "qty": 1}]
        prod_5 = self.create_simulation_product(73, 6, bom_lines_5)
        self.create_mrp_simulated_product(s_1.id, prod_5.id, 8)

        # call the method
        s_1.button_calculate_sub_products()
        
        # validate the result
        self.assertEquals(s_1.total_onhand_value, 20.3 * 4 + 73 * 6, "total_onhand_value") 
        # prod_1 2.7 * 6 + prod_4 7 * 1 = 23.2
        self.assertEquals(float_compare(s_1.total_value_needed, 23.2, precision_rounding=prod_5.product_tmpl_id.uom_id.rounding), 0, "total_value_needed")

        self.assertEquals(len(s_1.simulated_products), 2, "simulated_products.len")
        sp_0 = s_1.simulated_products[0]
        self.assertEquals(sp_0.product_id.id, prod_3.id, "simulated_products[0].id")
        self.assertEquals(sp_0.required_qty, 3, "simulated_products.required_qty")
        self.assertEquals(sp_0.onhand_qty, 4, "simulated_products.onhand_qty")
        self.assertEquals(sp_0.bom_cost, 2.7 + 5.1 * 3, "simulated_products.bom_cost")
        sp_1 = s_1.simulated_products[1]
        self.assertEquals(sp_1.product_id.id, prod_5.id, "simulated_products[1].id")
        self.assertEquals(sp_1.required_qty, 8, "simulated_products.required_qty")
        self.assertEquals(sp_1.onhand_qty, 6, "simulated_products.onhand_qty")
        self.assertEquals(sp_1.bom_cost, 2.7 * 2 + (2.7 + 5.1 * 3) * 3 + 7 * 1, "simulated_products.bom_cost")

        self.assertEquals(len(s_1.sub_products), 5, "sub_products.len")
        p_0 = s_1.sub_products[0]
        self.assertEquals(p_0.product_id.id, prod_3.id, "sub_products[0].id")
        self.assertEquals(p_0.required_qty, 4, "sub_product.required_qty")
        self.assertEquals(p_0.onhand_qty, 4, "sub_product.onhand_qty")
        self.assertEquals(p_0.diff_qty, 0, "sub_product.diff_qty")
        p_1 = s_1.sub_products[1]
        self.assertEquals(p_1.product_id.id, prod_5.id, "sub_products[1].id")
        self.assertEquals(p_1.required_qty, 6, "sub_product.required_qty")
        self.assertEquals(p_1.onhand_qty, 6, "sub_product.onhand_qty")
        self.assertEquals(p_1.diff_qty, 0, "sub_product.diff_qty")
        p_2 = s_1.sub_products[2]
        self.assertEquals(p_2.product_id.id, prod_1.id, "sub_products[2].id")
        self.assertEquals(p_2.required_qty, 9, "sub_product.required_qty") 
        self.assertEquals(p_2.onhand_qty, 3, "sub_product.onhand_qty")
        self.assertEquals(p_2.diff_qty, -6, "sub_product.diff_qty")
        p_3 = s_1.sub_products[3]
        self.assertEquals(p_3.product_id.id, prod_4.id, "sub_products[2].id")
        self.assertEquals(p_3.required_qty, 2, "sub_product.required_qty")
        self.assertEquals(p_3.onhand_qty, 1, "sub_product.onhand_qty")
        self.assertEquals(p_3.diff_qty, -1, "sub_product.diff_qty")
        p_4 = s_1.sub_products[4]
        self.assertEquals(p_4.product_id.id, prod_2.id, "sub_products[2].id")
        self.assertEquals(p_4.required_qty, 15, "sub_product.required_qty") 
        self.assertEquals(p_4.onhand_qty, 100, "sub_product.onhand_qty")
        self.assertEquals(p_4.diff_qty, 85, "sub_product.diff_qty")

        self.assertEquals(len(s_1.missed_sub_products), 2, "missed_sub_products.len")
        ssp_0 = s_1.missed_sub_products[0]
        self.assertEquals(ssp_0.product_id.id, prod_1.id, "missed_sub_products[0].id")
        self.assertEquals(ssp_0.diff_qty, -6, "missed_sub_products.id")
        ssp_1 = s_1.missed_sub_products[1]
        self.assertEquals(ssp_1.product_id.id, prod_4.id, "missed_sub_products[1].id")
        self.assertEquals(ssp_1.diff_qty, -1, "missed_sub_products.id")
        
        # add info to make sure the test case is done
        _logger.info("test_mutiple_simulation_products_with_bom_1() is done.")