# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from odoo.tools import float_compare
import queue

import logging
_logger = logging.getLogger(__name__)
    
class FlspMrpSimulatedProduct(models.Model):
    _name = 'flsp.mrp.simulatd.product'
    _description = 'FLSP MRP Simulated Product'

    simulation_id = fields.Many2one('flsp.mrp.simulation', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    required_qty = fields.Float(string='Qty Required')
    onhand_qty = fields.Float(related='product_id.qty_available', string='Qty on Hand')
    cost = fields.Float(related='product_id.product_tmpl_id.standard_price', string='Cost', default=0.0)
    bom_cost = fields.Float(string='BOM Cost', default=False)

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.onhand_qty = self.product_id.qty_available
        self.cost = self.product_id.product_tmpl_id.standard_price

class FlspMrpSubProduct(models.Model):
    _name = 'flsp.mrp.sub.product'
    _description = 'FLSP MRP Sub Product'

    simulation_id = fields.Many2one('flsp.mrp.simulation', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    required_qty = fields.Float(string='Qty Required')
    onhand_qty = fields.Float(related='product_id.qty_available', string='Qty on Hand')
    diff_qty = fields.Float(string='Diff Qty')
    cost = fields.Float(related='product_id.product_tmpl_id.standard_price', string='Cost', default=0.0)

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.onhand_qty = self.product_id.qty_available
        self.cost = self.product_id.product_tmpl_id.standard_price

class FlspMrpPlanningLine(models.Model):
    _name = 'flsp.mrp.simulation'
    _description = 'FLSP MRP Simulation Tool'

    simulation_name = fields.Char(string='Description', required=True)
    simulated_products = fields.One2many(comodel_name='flsp.mrp.simulatd.product', inverse_name='simulation_id', string="Simulated Products")
    missed_only = fields.Boolean('Missed Only', default=False,
        help="By checking the field, you may only see sub products with missed quantities in BoMs of the selected finished products.")
    total_onhand_value = fields.Float(string='Total On Hand Value', default=0.0)
    total_value_needed = fields.Float(string='Total Value Needed', default=0.0)
    sub_products = fields.One2many(comodel_name='flsp.mrp.sub.product', inverse_name='simulation_id', string="Sub Products")
    missed_sub_products = fields.Many2many(comodel_name='flsp.mrp.sub.product', string="Missed Sub Products")

    def button_calculate_sub_products(self):
        # delete previous items at first
        for psp in self.sub_products:
            psp.unlink()
        self.sub_products = False
        self.missed_sub_products = False

        if not self.simulated_products or len(self.simulated_products) == 0:
            return
        
        # get total onhand value
        self.calculate_total_onhand_value(self.simulated_products)
        
        # set default value
        self.total_value_needed = 0

        # get simulated_products with qty > 0
        valid_simulated_products = []
        for sp in self.simulated_products:
            if sp.required_qty > 0:
                valid_simulated_products.append(sp)
        if not valid_simulated_products or len(valid_simulated_products) == 0:
            return
        
        # calculate its BoM cost and check loop for valid product
        self.calculate_bom_cost(valid_simulated_products)
        
        # verify product qty in inventory, compare its required qty and break it down if needed
        self.calculate_full_sub_products(valid_simulated_products)

        missed_sub_product_ids = []
        for p in self.sub_products:
            if p.diff_qty < 0:
                missed_sub_product_ids.append(p.id)
                self.total_value_needed += p.cost * (0 - p.diff_qty)
        self.missed_sub_products = self.env['flsp.mrp.sub.product'].browse(missed_sub_product_ids)

    def calculate_bom_cost(self, valid_simulated_products):
        # set False for all products at first if not calculate before
        product_id_list = []
        for sp in valid_simulated_products:
            product_id_list.append(sp.product_id.id)
        products = self.env['product.product'].browse(product_id_list)

        boms_to_recompute = self.env['mrp.bom'].search(['|', ('product_id', 'in', products.ids), '&', ('product_id', '=', False), ('product_tmpl_id', 'in', products.mapped('product_tmpl_id').ids)])

        # In Dynamic Programming, costMap is used to map products which have been calculated this time to its cost
        # key: product.id
        # value: product.standard_price
        costMap ={}
        for p in products:
            prod_price = costMap.get(p.id)
            if not prod_price:
                prod_price = p.calculate_price_from_bom(costMap, boms_to_recompute)
                costMap[p.id] = prod_price
            sp.bom_cost = prod_price

    def calculate_total_onhand_value(self, simulated_products=False):
        self.total_onhand_value = 0
        for sp in simulated_products:
            self.total_onhand_value += sp.cost * sp.onhand_qty

    def get_bom(self, product):
        return self.env['mrp.bom']._bom_find(product=product)

    def calculate_full_sub_products(self, simulated_products):
        # runtime_prod_map is used to map products to its onhand_qty
        # key: product.id
        # value: onhand_qty
        runtime_prod_map ={}

        # init the queue with entry {product_id, onhand_qty, required_qty}
        prod_queue = queue.Queue()
        for sp in simulated_products:
            prod_queue.put({ "id": sp.product_id, "onhand_qty": sp.onhand_qty, "required_qty": sp.required_qty, "cost": sp.cost})
            runtime_prod_map[sp.product_id.id] = sp.onhand_qty

        while not prod_queue.empty():
            pq = prod_queue.get()
            prod = pq["id"]
            onhand_qty = pq["onhand_qty"]
            required_qty = pq["required_qty"]
            cost = pq["cost"]
            
            runtime_onhand_qty = runtime_prod_map.get(prod.id)
            if not runtime_onhand_qty:
                # prod is not added, so add it 
                runtime_prod_map[prod.id] = onhand_qty
                runtime_onhand_qty = onhand_qty
                
            # determine how to handle the product in DB and queue
            diff_qty = runtime_onhand_qty - required_qty
            if float_compare(runtime_onhand_qty, required_qty, precision_rounding=prod.product_tmpl_id.uom_id.rounding) >= 0:
                # have more in stock than needed, just add it in list
                self.update_sub_product_entry(self.id, prod.id, required_qty, onhand_qty, diff_qty, cost)
                # update runtime onhand qty
                runtime_prod_map[prod.id] = diff_qty
            else:
                # have less in stock than needed
                runtime_prod_map[prod.id] = 0

                bom = self.get_bom(prod)
                if not bom:
                    # no bom for the product, just add it in list
                    self.update_sub_product_entry(self.id, prod.id, required_qty, onhand_qty, diff_qty, cost)
                else:
                    # has bom for the product, add all in stock in list
                    self.update_sub_product_entry(self.id, prod.id, onhand_qty, onhand_qty, 0, cost)

                    # create new products in bom of the product with extra qty into the queue
                    extra_qty = 0 - diff_qty
                    for line in bom.bom_line_ids:
                        if line._skip_bom_line(prod):
                            continue
                        new_required_qty = line.product_qty * extra_qty
                        prod_queue.put({ "id": line.product_id, "onhand_qty": line.product_id.qty_available, "required_qty": new_required_qty, "cost": line.product_id.product_tmpl_id.standard_price})

    def update_sub_product_entry(self, simulation_id, product_id, required_qty, onhand_qty, diff_qty, cost):
        sub_prod = self.env['flsp.mrp.sub.product'].search([('simulation_id', '=', simulation_id), ('product_id', '=', product_id)])
        if sub_prod:
            sub_prod.required_qty += required_qty
            sub_prod.diff_qty = sub_prod.onhand_qty - sub_prod.required_qty
        else:
            self.env['flsp.mrp.sub.product'].create({
                        'simulation_id': simulation_id,
                        'product_id': product_id,
                        'required_qty': required_qty,
                        'diff_qty': diff_qty,
            })