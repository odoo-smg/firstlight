# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import Form
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from datetime import date, datetime
from psycopg2.errors import UniqueViolation
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP

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
        self.mrp_simulatd_product_model = self.env['flsp.mrp.simulatd.product']
        self.mrp_sub_product_model = self.env['flsp.mrp.sub.product']
        self.mrp_product_model = self.env['product.product']
        self.mrp_product_tmpl_model = self.env['product.template']
        self.mrp_bom_model = self.env['mrp.bom']
        self.mrp_bom_line_model = self.env['mrp.bom.line']
        self.category_model = self.env['product.category']
        self.uom_model = self.env['uom.uom']
        self.tax_model = self.env['account.tax']

    def create_product_tmpl(self, name, type, categ_id, uom_id, uom_po_id, sale_line_warn, purchase_line_warn, tracking, standard_price):
        # form = Form(self.mrp_product_tmpl_model.with_context(tracking_disable=True))
        # form.name = name
        # form.type = type
        # form.categ_id = self.category_model.browse(categ_id)
        # form.uom_id = self.uom_model.browse(uom_id)
        # form.uom_po_id = self.uom_model.browse(uom_po_id)
        # form.sale_line_warn = sale_line_warn
        # form.purchase_line_warn = purchase_line_warn
        # form.tracking = tracking
        # form.list_price = list_price
        # return form.save()

        tax_include_id = self.tax_model.create(dict(name="Include tax",
                                                    amount='21.00',
                                                    price_include=True,
                                                    type_tax_use='sale'))
        product_tmpl_id = self.mrp_product_tmpl_model.create(dict(name="Voiture",
                                                              list_price=121,
                                                              taxes_id=[(6, 0, [tax_include_id.id])]))
        # return self.mrp_product_tmpl_model.create({
        #                 'name': name,
        #                 'type': type,
        #                 'categ_id': categ_id,
        #                 'uom_id': uom_id,
        #                 'uom_po_id': uom_po_id,
        #                 'tracking': tracking,
        #                 'standard_price': standard_price,
        #                 'sale_line_warn': sale_line_warn,
        #                 # 'purchase_line_warn': purchase_line_warn,
        #         })
        
    def create_product(self, default_code, name, cost, onhand_qty):
        form = Form(self.mrp_product_model.with_context(tracking_disable=True))
        form.product_tmpl_id = self.create_product_tmpl(name, 'product', 8, 1, 1, "no-message", 'no-message', 'none', cost).id
        form.default_code = default_code
        form.active = True
        form.qty_available = onhand_qty
        return form.save()
        
    def create_simulate_product(self, cost, onhand_qty):
        postfix = str(datetime.now())
        aName = 'prod-simulation-' + postfix
        default_code = 'code-simulation-' + postfix
        return self.create_product(default_code, aName, cost, onhand_qty)
        
    def create_bom(self, product):
        form = Form(self.mrp_bom_model.with_context(tracking_disable=True))
        form.code = product.name + "_bom"
        form.active = True
        form.type = 'normal'
        form.product_tmpl_id = product.product_tmpl_id.id
        form.product_id = product.id
        form.product_qty = 1.0
        form.product_uom_id = 1
        form.ready_to_produce = 'asap'
        return form.save()
        
    def create_bom_lines(self, bom, bom_lines):
        for line in bom_lines:
            form = Form(self.mrp_bom_line_model.with_context(tracking_disable=True))
            form.product_id = line["product_id"]
            form.product_qty = line["qty"]
            form.product_uom_id = 1
            form.bom_id = bom.id
            form.save()
        
    def create_mrp_simulation_product(self, cost, onhand_qty, bom_lines):
        prod = self.create_simulate_product(cost, onhand_qty)
        bom = False
        if bom_lines:
            bom = self.create_bom(prod)
            self.create_bom_lines(bom, bom_lines)
        return prod, bom
        
    def delete_mrp_simulation_product(self, prod, bom):
        if bom:
            self.mrp_bom_line_model.search(['bom_id', '=', bom.id]).unlink()
            self.mrp_bom_model.search(['id', '=', bom.id]).unlink()
        self.mrp_product_model.search(['id', '=', prod.id]).unlink()
        self.mrp_product_tmpl_model.search(['id', '=', prod.product_tmpl_id.id]).unlink()
        
    def create_mrp_simulation(self, missed_only):
        form = Form(self.mrp_simulation_model.with_context(tracking_disable=True))
        postfix = str(datetime.now())
        aName = 'simulation-' + postfix
        form.simulation_name = aName
        form.missed_only = missed_only
        return form.save()
        
    def create_mrp_simulated_product(self, simulation_id, prod_id, required_qty):
        form = Form(self.mrp_simulation_model.with_context(tracking_disable=True))
        form.simulation_id = simulation_id
        form.product_id = prod_id
        form.required_qty = required_qty
        return form.save()
        
    def test_simulation_product_without_bom(self):
        # prepare test data
        # bom_lines_1 = [{"product_id": 1, "qty": 2}]

        tax_include_id = self.tax_model.create(dict(name="Include tax",
                                                    amount='21.00',
                                                    price_include=True,
                                                    type_tax_use='sale'))
        product_tmpl_id = self.mrp_product_tmpl_model.create(dict(name="Voiture",
                                                              list_price=121,
                                                              taxes_id=[(6, 0, [tax_include_id.id])]))
        _logger.info("product_tmpl_id.....")

        cost = 1.2
        onhand_qty = 2
        required_qty = 1
        prod_1, bom_1 = self.create_mrp_simulation_product(cost, onhand_qty, False)
        s_1 = self.create_mrp_simulation(False)
        self.create_mrp_simulated_product(s_1, prod_1, required_qty)

        # call the method
        self.mrp_simulation_model.button_calculate_sub_products(s_1)
        
        # validate the result
        self.assertEquals(s_1.total_onhand_value, cost * onhand_qty, "total_onhand_value")
        self.assertEquals(s_1.total_value_needed, 0, "total_value_needed")
        self.assertEquals(len(s_1.sub_products), 1, "sub_products.len")
        p_1 = False
        for p in s_1.sub_products:
            if p.id == prod_1.id:
                p_1 = prod_1
                break
        self.assertTrue(p_1)
        self.assertEquals(p_1.id, prod_1.id, "sub_product.id")
        self.assertEquals(p_1.required_qty, required_qty, "sub_product.required_qty")
        self.assertEquals(p_1.onhand_qty, onhand_qty, "sub_product.onhand_qty")
        self.assertEquals(p_1.diff_qty, onhand_qty - required_qty, "sub_product.diff_qty")
        self.assertEquals(p_1.cost, cost, "sub_product.cost")
        self.assertEquals(len(s_1.missed_sub_products), 1, "missed_sub_products.len")
        p_1 = False
        for p in s_1.missed_sub_products:
            if p.id == prod_1.id:
                p_1 = prod_1
                break
        self.assertTrue(p_1)
        
        # add info to make sure the test case is done
        _logger.info("test_simulation_product_without_bom() is done.")
