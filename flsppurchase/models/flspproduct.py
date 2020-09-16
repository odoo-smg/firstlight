# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_round


class flsppurchaseproductprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_open_po_qty = fields.Float(compute='_compute_flsp_open_po_qty', string='Qty Open PO')
    flsp_bom_level = fields.Integer(string='Bom Level')
    flsp_suggested_qty = fields.Float(string="Suggested Qty", readonly=True, help="Quantity suggested to buy or produce.")
    flsp_suggested_state = fields.Selection([
        ('buy', 'To Buy'),
        ('ok' , 'No Action'),
        ('po' , 'Confirm PO'),
        ('mfg', 'To Manufacture'),
    ], string='State', readonly=True)
    flsp_route_buy = fields.Selection([('buy', 'To Buy'),('na' , 'Non Applicable'),], string='To Buy', readonly=True)
    flsp_route_mfg = fields.Selection([('mfg', 'To Manufacture'),('na' , 'Non Applicable'),], string='To Produce', readonly=True)

    def _flsp_call_report_wizard(self):
        action = self.env.ref('flsppurchase.launch_flsp_suggestion_wizard').read()[0]
        return action

    def _flsp_calc_suggested_qty(self):

        ## First update the bom levels:
        self._flsp_calc_bom_level()

        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id
        route_mto = self.env.ref('stock.route_warehouse0_mto').id
        route_mfg = self.env.ref('mrp.route_warehouse0_manufacture').id

        replenish_suggestion = self.env['report.purchase.suggestion'].search([], order="level_bom")

        #print(' starting the calculation of suggestions| Route mfg = '+str(route_mfg)+' Route buy='+str(route_buy))

        for suggestion in replenish_suggestion:
            suggestion.product_id.flsp_suggested_state = 'ok'
            suggestion.product_id.flsp_suggested_qty = 0
            ## ignore non storable products
            if suggestion.level_bom <= 0:
                continue

            ## minimal quantity
            total_forcasted = suggestion.product_qty+suggestion.curr_ins-suggestion.curr_outs
            if total_forcasted < suggestion.product_min_qty or total_forcasted < 0:
                if suggestion.qty_rfq > 0 and suggestion.qty_rfq > suggestion.product_min_qty - total_forcasted:
                    suggestion.product_id.flsp_suggested_state = 'po'
                else:
                    suggestion.product_id.flsp_suggested_qty = suggestion.product_min_qty - total_forcasted
                    if route_mfg in suggestion.product_id.route_ids.ids:
                        suggestion.product_id.flsp_suggested_state = 'mfg'
                    elif route_buy in suggestion.product_id.route_ids.ids:
                        suggestion.product_id.flsp_suggested_state = 'buy'

            ''' calculate from top bottom the indirect demand from BOM'''
            parent_boms = self.env['mrp.bom.line'].search([('product_id', '=', suggestion.product_id.id)])
            for bom in parent_boms:
                parent_product = self.env['product.product'].search([('product_tmpl_id', '=', bom.bom_id.product_tmpl_id.id)])
                if parent_product.flsp_suggested_qty > 0:
                    needed_qty = bom.product_qty*parent_product.flsp_suggested_qty
                    total_forcasted = suggestion.product_qty+suggestion.curr_ins-suggestion.curr_outs-needed_qty
                    if total_forcasted < suggestion.product_min_qty or total_forcasted < 0:
                        if suggestion.qty_rfq > 0  and suggestion.qty_rfq > suggestion.product_min_qty - total_forcasted:
                            suggestion.product_id.flsp_suggested_state = 'po'
                        else:
                            suggestion.product_id.flsp_suggested_qty = suggestion.product_min_qty - total_forcasted
                            if route_mfg in suggestion.product_id.route_ids.ids:
                                suggestion.product_id.flsp_suggested_state = 'mfg'
                            elif route_buy in suggestion.product_id.route_ids.ids:
                                suggestion.product_id.flsp_suggested_state = 'buy'
            #print('level bom: '+str(suggestion.level_bom))

        action = self.env.ref('flsppurchase.purchase_suggestion_action').read()[0]
        return action

    def _flsp_calc_bom_level(self):
        current_level = 1
        next_level = {current_level: {}}

        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id
        route_mfg = self.env.ref('mrp.route_warehouse0_manufacture').id

        all_products = self.env['product.product'].search([('route_ids', 'in', [route_buy, route_mfg])])

        for lines in all_products:
            if route_buy in lines.route_ids.ids:
                lines.flsp_route_buy = 'buy'
            else:
                lines.flsp_route_buy = 'na'

            if route_mfg in lines.route_ids.ids:
                lines.flsp_route_mfg = 'mfg'
            else:
                lines.flsp_route_mfg = 'na'

            if lines.used_in_bom_count:
                lines.flsp_bom_level = -1
            else:
                lines.flsp_bom_level = current_level
                next_level[current_level][lines.product_tmpl_id.id] = lines

        complete = False
        while not complete and current_level < 30:
            current_level += 1
            complete = True
            next_level[current_level] = {}
            for lines in all_products:
                if lines.flsp_bom_level < 0:
                    comp_boms = self.env['mrp.bom.line'].search([('product_id', '=', lines.id)])
                    found_level = False
                    for parent_bom in comp_boms:
                        if parent_bom.bom_id.product_tmpl_id.id in next_level[current_level - 1]:
                            lines.flsp_bom_level = current_level
                            next_level[current_level][lines.product_tmpl_id.id] = lines
                            found_level = True
                    if not found_level:
                        complete = found_level

    def _compute_flsp_open_po_qty(self):
        if not self.purchase_ok:
            for product in self:
                product.flsp_open_po_qty = 0.0
        else:
            domain = [
                ('flsp_open_qty', '>', 0),
                ('product_id', 'in', self.ids)
            ]
            order_lines = self.env['purchase.order.line'].search(domain)
            for product in self:
                if not product.id:
                    product.flsp_open_po_qty = 0.0
                    continue
                for line in order_lines:
                    product.flsp_open_po_qty += line.flsp_open_qty
        if not self.flsp_open_po_qty:
            self.flsp_open_po_qty = 0

    def action_view_open_po(self):
        action = self.env.ref('flsppurchase.action_purchase_order_line_all').read()[0]
        action['domain'] = ['&', ('product_id', 'in', self.ids), ('flsp_open_qty', '>', 0)]
        return action


class flsppurchaseproducttmp(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    flsp_open_po_qty = fields.Float(compute='_compute_flsp_open_po_qty', string='Qty Open PO')

    def _compute_flsp_open_po_qty(self):
        if not self.purchase_ok:
            for template in self:
                template.flsp_open_po_qty = 0
        else:
            for template in self:
                template.flsp_open_po_qty = float_round(sum([p.flsp_open_po_qty for p in template.product_variant_ids]), precision_rounding=template.uom_id.rounding)

    def action_view_open_po(self):
        product_prd = self.env['product.product'].search([('product_tmpl_id', 'in', self.ids)])
        action = self.env.ref('flsppurchase.action_purchase_order_line_all').read()[0]
        action['domain'] = ['&', ('product_id', '=', product_prd.ids), ('flsp_open_qty', '>', 0)]
        return action
