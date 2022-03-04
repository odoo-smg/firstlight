# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_round


class flsppurchaseproductprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_open_po_qty = fields.Float(compute='_compute_flsp_open_po_qty', string='Qty Open PO')
    flsp_bom_level = fields.Integer(string='Bom Level')
    flsp_suggested_qty = fields.Float(string="Suggested Qty", readonly=True, help="Quantity suggested to buy or produce.")
    flsp_adjusted_qty = fields.Float(String="Adjusted Qty", help="Adjust the quantity to be executed.")
    flsp_suggested_state = fields.Selection([
        ('buy', 'To Buy'),
        ('ok' , 'No Action'),
        ('po' , 'Confirm PO'),
        ('mo' , 'Confirm MO'),
        ('mfg', 'To Manufacture'),
    ], string='State', readonly=True)
    flsp_route_buy = fields.Selection([('buy', 'To Buy'),('na' , 'Non Applicable'),], string='To Buy', readonly=True)
    flsp_route_mfg = fields.Selection([('mfg', 'To Manufacture'),('na' , 'Non Applicable'),], string='To Produce', readonly=True)

    flsp_curr_ins = fields.Float(string="In Coming Qty", readonly=True)
    flsp_curr_outs = fields.Float(string="Out Going Qty", readonly=True)
    flsp_month1_use = fields.Float(string="Las month usage", readonly=True)
    flsp_month2_use = fields.Float(string="Two months ago usage", readonly=True)
    flsp_month3_use = fields.Float(string="Three months ago usage", readonly=True)
    flsp_qty_rfq = fields.Float(string="Total RFQs", readonly=True)
    flsp_qty_mo = fields.Float(string="Qty MO Draft", readonly=True)
    flsp_min_qty = fields.Float(string="Min Qty", readonly=True)
    flsp_max_qty = fields.Float(string="Max Qty", readonly=True)
    flsp_mult_qty = fields.Float('Qty Multiple', readonly=True)
    flsp_qty     = fields.Float(string="On Hand", readonly=True)
    flsp_desc = fields.Char(string='Description', readonly=True)
    flsp_default_code = fields.Char(string='Part #', readonly=True)
    flsp_type = fields.Char(string='Type', readonly=True)


    def _flsp_call_report_wizard(self):
        action = self.env.ref('flsppurchase.launch_flsp_suggestion_wizard').read()[0]
        return action

    def _flsp_calc_suggested_qty(self):

        ## First update the bom levels:
        self._flsp_calc_bom_level()

        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id
        route_mto = self.env.ref('stock.route_warehouse0_mto').id
        route_mfg = self.env.ref('mrp.route_warehouse0_manufacture').id

        replenish_suggestion = self.env['report.flsppurchase.auxview'].search([], order="level_bom")

        #print(' starting the calculation of suggestions| Route mfg = '+str(route_mfg)+' Route buy='+str(route_buy))

        for suggestion in replenish_suggestion:
            suggestion.product_id.flsp_curr_ins = suggestion.curr_ins
            suggestion.product_id.flsp_curr_outs = suggestion.curr_outs
            suggestion.product_id.flsp_month1_use = suggestion.month1_use
            suggestion.product_id.flsp_month2_use = suggestion.month2_use
            suggestion.product_id.flsp_month3_use = suggestion.month3_use
            suggestion.product_id.flsp_qty_rfq = suggestion.qty_rfq
            suggestion.product_id.flsp_qty_mo = suggestion.qty_mo
            suggestion.product_id.flsp_min_qty = suggestion.product_min_qty
            suggestion.product_id.flsp_mult_qty = suggestion.qty_multiple
            #suggestion.product_id.flsp_max_qty = suggestion.max_qty
            suggestion.product_id.flsp_desc = suggestion.description
            suggestion.product_id.flsp_default_code = suggestion.default_code
            suggestion.product_id.flsp_qty = suggestion.product_qty
            suggestion.product_id.flsp_type = suggestion.type
            suggestion.product_id.flsp_suggested_state = 'ok'
            suggestion.product_id.flsp_suggested_qty = 0
            suggestion.product_id.flsp_adjusted_qty = 0

            ## ignore non storable products
            if suggestion.level_bom <= 0:
                continue

            ## minimal quantity
            total_forcasted = suggestion.product_qty+suggestion.curr_ins-suggestion.curr_outs
            if total_forcasted < suggestion.product_min_qty or total_forcasted < 0:
                if suggestion.qty_rfq > 0 and suggestion.qty_rfq >= suggestion.product_min_qty - total_forcasted:
                    suggestion.product_id.flsp_suggested_state = 'po'
                elif suggestion.qty_mo > 0 and suggestion.qty_mo >= suggestion.product_min_qty - total_forcasted:
                    suggestion.product_id.flsp_suggested_state = 'mo'
                else:
                    suggestion.product_id.flsp_suggested_qty = suggestion.product_min_qty - total_forcasted
                    suggestion.product_id.flsp_adjusted_qty = suggestion.product_id.flsp_suggested_qty
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
                        if suggestion.qty_rfq > 0 and suggestion.qty_rfq >= suggestion.product_min_qty - total_forcasted:
                            suggestion.product_id.flsp_suggested_state = 'po'
                        elif suggestion.qty_mo > 0 and suggestion.qty_mo >= suggestion.product_min_qty - total_forcasted:
                            suggestion.product_id.flsp_suggested_state = 'mo'
                        else:
                            suggestion.product_id.flsp_suggested_qty = suggestion.product_min_qty - total_forcasted
                            suggestion.product_id.flsp_adjusted_qty = suggestion.product_id.flsp_suggested_qty
                            if route_mfg in suggestion.product_id.route_ids.ids:
                                suggestion.product_id.flsp_suggested_state = 'mfg'
                            elif route_buy in suggestion.product_id.route_ids.ids:
                                suggestion.product_id.flsp_suggested_state = 'buy'
            qty_multiple = fields.Float('Qty Multiple', readonly=True)
            # multiple quantities:
            if suggestion.qty_multiple > 0:
                remaining = suggestion.product_id.flsp_suggested_qty % suggestion.qty_multiple
                if remaining > 0:
                    suggestion.product_id.flsp_suggested_qty += suggestion.qty_multiple-remaining
                    suggestion.product_id.flsp_adjusted_qty = suggestion.product_id.flsp_suggested_qty
        self.env['flspautoemails.bpmemails'].send_email(self, 'P00001')


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
        receipt_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Receipts')]).ids
        for product in self:
            if not product.purchase_ok:
                product.flsp_open_po_qty = 0.0
            else:
                domain = [
                    '&', ('state', 'not in', ['done', 'cancel', 'draft']),
                    '&', ('picking_type_id', 'in', receipt_stock_type),
                    ('product_id', '=', product.id)
                ]
                open_receipts = self.env['stock.picking'].search(domain)
                if not product.id:
                    product.flsp_open_po_qty = 0.0
                    continue
                for receipt in open_receipts:
                    stock_move_product = self.env['stock.move'].search(['&', ('picking_id', '=', receipt.id), ('product_id', '=', product.id)])
                    for move in stock_move_product:
                        product.flsp_open_po_qty += move.product_uom_qty
            if not product.flsp_open_po_qty:
                product.flsp_open_po_qty = 0

    def action_view_open_po(self):
        receipt_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Receipts')]).ids
        domain = [
            '&', ('state', 'not in', ['done', 'cancel', 'draft']),
            '&', ('picking_type_id', 'in', receipt_stock_type),
            ('product_id', 'in', self.ids)
        ]
        open_receipts = self.env['stock.picking'].search(domain)
        orders_to_approve = self.env['purchase.order'].search([('flsp_po_status', '=', 'to_approve')]).ids
        po_ids = []
        product_ids = []
        for product in self:
            product_ids.append(product.id)
            if not product.id:
                product.flsp_open_po_qty = 0.0
                continue
            for receipt in open_receipts:
                stock_move_product = self.env['stock.move'].search(
                    ['&', ('picking_id', '=', receipt.id), ('product_id', '=', product.id)])
                for move in stock_move_product:
                    if move.purchase_line_id.product_uom_qty - move.purchase_line_id.qty_received > 0:
                        po_ids.append(move.purchase_line_id.id)
            lines_to_approve = self.env['purchase.order.line'].search(['&', ('order_id', 'in', orders_to_approve), ('product_id', '=', product.id)])
            for line in lines_to_approve:
                po_ids.append(line.id)

        #action = self.env.ref('flsppurchase.action_purchase_order_line_all').read()[0]
        #action['domain'] = ['&', ('id', 'in', po_ids), ('product_id', 'in', product_ids)]
        action = self.env.ref('flsppurchase.flsp_stock_move_open_po_action').read()[0]
        action['domain'] = ['&', '&', ('state', 'not in', ['cancel', 'done']), ('purchase_line_id', 'in', po_ids), ('product_id', 'in', product_ids)]
        return action


class flsppurchaseproducttmp(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    flsp_open_po_qty = fields.Float(compute='_compute_flsp_open_po_qty', string='Qty Open PO')

    def _compute_flsp_open_po_qty(self):
        for template in self:
            if not template.purchase_ok:
                template.flsp_open_po_qty = 0
            else:
                amount = float_round(sum([p.flsp_open_po_qty for p in template.product_variant_ids]), precision_rounding=template.uom_id.rounding)
                amount = template.uom_po_id._compute_quantity(amount,template.uom_id)
                template.flsp_open_po_qty = amount

    def action_view_open_po(self):
        receipt_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Receipts')]).ids
        product_ids = self.env['product.product'].search([('product_tmpl_id', 'in', self.ids)]).ids
        domain = [
            '&', ('state', 'not in', ['done', 'cancel', 'draft']),
            '&', ('picking_type_id', 'in', receipt_stock_type),
            ('product_id', 'in', product_ids)
        ]
        open_receipts = self.env['stock.picking'].search(domain)
        po_ids = []
        product_ids = []
        for product in self:
            product_ids = self.env['product.product'].search([('product_tmpl_id', '=', product.id)]).ids
            for receipt in open_receipts:
                stock_move_product = self.env['stock.move'].search(
                    ['&', ('picking_id', '=', receipt.id), ('product_id', 'in', product_ids)])
                for move in stock_move_product:
                    if move.purchase_line_id.product_uom_qty - move.purchase_line_id.qty_received > 0:
                        po_ids.append(move.purchase_line_id.id)
        #action = self.env.ref('flsppurchase.action_purchase_order_line_all').read()[0]
        #action['domain'] = ['&', ('id', 'in', po_ids), ('product_id', 'in', product_ids)]
        action = self.env.ref('flsppurchase.flsp_stock_move_open_po_action').read()[0]
        action['domain'] = ['&', '&', ('state', 'not in', ['cancel', 'done']), ('purchase_line_id', 'in', po_ids), ('product_id', 'in', product_ids)]
        return action
