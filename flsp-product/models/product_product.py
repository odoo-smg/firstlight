# -*- coding: utf-8 -*-

from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)


class smgproductprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_acc_valid   = fields.Boolean(string="Accounting Validated", readonly=True, copy=False)
    attachment_ids = fields.Many2many('ir.attachment', 'product_attachment_rel','drawing_id', 'attachment_id',
        string='Attachments',
        compute='_get_product_attachment',
        store=False,
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.')
    x_studio_specification = fields.Binary(string='Specification', store=False, compute='_get_specification_attachment')
    x_studio_drawing = fields.Binary(string="Drawing", store=False, compute='_get_drawing_attachment')
    x_studio_drawing_filename = fields.Char(string="Drawing Filename", store=False)
    x_studio_specification_filename = fields.Char(string="Specification Filename", store=False)

    def button_acc_valid(self):
        self.product_tmpl_id.flsp_acc_valid = True
        return self.write({'flsp_acc_valid': True})

    def button_acc_valid_off(self):
        self.product_tmpl_id.flsp_acc_valid = False
        return self.write({'flsp_acc_valid': False})

    def _get_product_attachment(self):
        products = self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)])
        self.attachment_ids = products.attachment_ids

    def _get_specification_attachment(self):
        products = self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)])
        self.x_studio_specification = products.x_studio_specification
        self.x_studio_specification_filename = products.x_studio_specification_filename

    def _get_drawing_attachment(self):
        products = self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)])
        self.x_studio_drawing_filename = products.x_studio_drawing_filename
        self.x_studio_drawing = products.x_studio_drawing

    @api.model
    def recalculateCost(self):
        """
         Date:    Apr/6th/2021
         Purpose: create a routine to recalculate the cost of finished products based on BOM to run every night.
         Author:  Perry He
        """   
        _logger.info("Starting 'recalculateCost()' for finished products.")

        finished_products = self.env['product.product'].search([]).filtered(lambda p: p.bom_count > 0)
        _logger.info("The products to calculate: " + str(finished_products.mapped('display_name')))

        finished_products.calculate_bom_cost()
        _logger.info("'recalculateCost()' done.")

        finished_products.notify_recalculateCost()

    
    # Simialr to method action_bom_cost() in \mrp_account\models\product.py
    # the products exclude ones with "valuation == 'real_time'" in method action_bom_cost(), but no need to filter them out in our schedule
    def calculate_bom_cost(self):
        # get all boms for the products
        boms_to_recompute = self.env['mrp.bom'].search(['|', ('product_id', 'in', self.ids), '&', ('product_id', '=', False), ('product_tmpl_id', 'in', self.mapped('product_tmpl_id').ids)])

        # In Dynamic Programming, costMap is used to map products which have been calculated this time to its cost
        # key: product.id
        # value: product.standard_price
        costMap ={}
        
        for product in self:
            prod_price = costMap.get(product.id)
            if not prod_price:
                prod_price = product.calculate_price_from_bom(costMap, boms_to_recompute)
                costMap[product.id] = prod_price

            # set standard_price with the cost 
            product.standard_price = prod_price

    def calculate_price_from_bom(self, costMap, boms_to_recompute=False):
        self.ensure_one()
        bom = self.env['mrp.bom']._bom_find(product=self)
        return self.calculate_bom_price(bom, costMap, boms_to_recompute=boms_to_recompute)

    def calculate_bom_price(self, bom, costMap, boms_to_recompute=False):
        prod_price = costMap.get(self.id)
        if prod_price:
            return prod_price

        self.ensure_one()
        if not bom:
            prod_price = 0
            costMap[self.id] = prod_price
            return prod_price
        if not boms_to_recompute:
            boms_to_recompute = []

        total = 0
        for opt in bom.routing_id.operation_ids:
            duration_expected = (
                opt.workcenter_id.time_start +
                opt.workcenter_id.time_stop +
                opt.time_cycle)
            total += (duration_expected / 60) * opt.workcenter_id.costs_hour
        for line in bom.bom_line_ids:
            if line._skip_bom_line(self):
                continue

            # Compute recursive if line has `child_line_ids`
            if line.child_bom_id and line.child_bom_id in boms_to_recompute:
                child_total = line.product_id.calculate_bom_price(line.child_bom_id, costMap, boms_to_recompute=boms_to_recompute)
                total += line.product_id.uom_id._compute_price(child_total, line.product_uom_id) * line.product_qty
            else:
                total += line.product_id.uom_id._compute_price(line.product_id.standard_price, line.product_uom_id) * line.product_qty
        bom_price = bom.product_uom_id._compute_price(total / bom.product_qty, self.uom_id)
        costMap[self.id] = bom_price
        return bom_price

    def notify_recalculateCost(self):
        _logger.info("************ Sending 'Products with Cost Recalculation - Daily Report' ************")
        self.env['flspautoemails.bpmemails'].send_email(self, 'AC0002')
        _logger.info("************ 'Products with Cost Recalculation - Daily Report' DONE ***************")
        