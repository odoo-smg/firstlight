# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api
from datetime import datetime


class Purcahsesuggestion(models.Model):
    _name = 'report.purchase.suggestion'
    _auto = False
    _description = 'Purchase Suggestion Report'

    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_min_qty = fields.Float('Min. Qty', readonly=True)
    qty_multiple = fields.Float('Qty Multiple', readonly=True)
    product_qty = fields.Float(string='Qty on Hand', readonly=True)
    curr_outs = fields.Float(String="Demand", readonly=True, help="Includes all confirmed sales orders and manufacturing orders")
    curr_ins = fields.Float(String="Replenishment", readonly=True, help="Includes all confirmed purchase orders and manufacturing orders")
    average_use = fields.Float(String="Avg Use", readonly=True, help="Average usage of the past 3 months.")
    month1_use = fields.Float(String="2020-06 Usage", readonly=True, help="Total usage of last month.")
    month2_use = fields.Float(String="2020-05 Usage", readonly=True, help="Total usage of 2 months ago.")
    month3_use = fields.Float(String="2020-04 Usage", readonly=True, help="Total usage of 3 months ago.")
    suggested_qty = fields.Float(String="Suggested Qty", readonly=True, help="Quantity suggested to buy or produce.")
    adjusted_qty = fields.Float(String="Adjusted Qty", help="Adjust the quantity to be executed.")
    qty_rfq = fields.Float(String="RFQ Qty", readonly=True, help="Total Quantity of Requests for Quotation.")
    qty_mo = fields.Float(string="Qty MO Draft", readonly=True)
    level_bom = fields.Integer(String="BOM Level", readonly=True, help="Position of the product inside of a BOM.")
    route_buy = fields.Selection([('buy', 'To Buy'),('na' , 'Non Applicable'),], string='To Buy', readonly=True)
    route_mfg = fields.Selection([('mfg', 'To Manufacture'),('na' , 'Non Applicable'),], string='To Produce', readonly=True)
    state = fields.Selection([
        ('buy', 'To Buy'),
        ('ok' , 'No Action'),
        ('po' , 'Confirm PO'),
        ('mo' , 'Confirm MO'),
        ('mfg', 'To Manufacture'),
    ], string='State', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_purchase_suggestion')

        query = """
        CREATE or REPLACE VIEW report_purchase_suggestion AS (
        SELECT
            pp.id,
            pp.flsp_bom_level as level_bom,
            pp.flsp_default_code as default_code,
            pp.id as product_id,
            pp.product_tmpl_id as product_tmpl_id,
            pp.flsp_suggested_state as state,
            pp.flsp_curr_ins as curr_ins,
            pp.flsp_curr_outs as curr_outs,
            pp.flsp_month1_use as month1_use,
            pp.flsp_month2_use as month2_use,
            pp.flsp_month3_use as month3_use,
            0 as average_use,
            pp.flsp_qty_rfq as qty_rfq,
            pp.flsp_qty_mo as qty_mo,
            pp.flsp_route_buy as route_buy,
            pp.flsp_route_mfg as route_mfg,
            pp.flsp_suggested_qty as suggested_qty,
            pp.flsp_adjusted_qty as adjusted_qty,
            pp.flsp_desc AS description,
            pp.flsp_qty AS product_qty,
            pp.flsp_min_qty as product_min_qty,
            pp.flsp_mult_qty as qty_multiple
        FROM product_product pp
        where flsp_type = 'product'
        );
        """
        self.env.cr.execute(query)

    def execute_suggestion(self):
        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id
        route_mfg = self.env.ref('mrp.route_warehouse0_manufacture').id

        email_log = {}
        for item in self:
            email_log[item.id] = {'default_code': item.default_code,
                                  'description': item.description,
                                  'status': '',
                                  'adjusted_qty': item.adjusted_qty,
                                  'suggested_qty': item.suggested_qty,
                                  'log': ''}
            if item.adjusted_qty <= 0:
                email_log[item.id]['status'] = 'N/A'
                email_log[item.id]['log'] = 'No action taken'
                continue
            if route_buy in item.product_id.route_ids.ids:
                partner_id = False
                price_unit = 0
                product_uom = False
                for seller in item.product_tmpl_id.seller_ids:
                    partner_id = seller.name
                    price_unit = seller.price
                    product_uom = seller.product_uom.id
                if partner_id:
                    email_log[item.id]['status'] = 'To Buy'
                    email_log[item.id]['log'] = 'Creating PO...'
                    item_to_buy = [
                        (0, 0, {'product_id': item.product_id.id,
                                'name': item.product_tmpl_id.name,
                                'product_qty': item.adjusted_qty,
                                'product_uom': product_uom,
                                'price_unit': price_unit,
                                'date_planned': datetime.now()}),]
                    new_po = self.env['purchase.order'].create({'partner_id': partner_id.id,
                                                       'currency_id': self.env.company.currency_id.id,
                                                       'date_order': datetime.now(),
                                                       'order_line': item_to_buy})
                    email_log[item.id]['status'] = 'success'
                    email_log[item.id]['log'] = 'PO created: ' + new_po.name
                else:
                    email_log[item.id]['status'] = 'warning'
                    email_log[item.id]['log'] = 'No vendor or price was found.'
            elif route_mfg in item.product_id.route_ids.ids:
                email_log[item.id]['status'] = 'To Manufacture'
                email_log[item.id]['log'] = 'Creating MO...'
                bom_id = self.env['mrp.bom'].search([('product_tmpl_id', '=', item.product_tmpl_id.id)], limit=1)
                if not bom_id:
                    email_log[item.id]['status'] = 'warning'
                    email_log[item.id]['log'] = 'No BOM was found.'
                    continue

                mo = self.env['mrp.production'].create({
                    'product_id': item.product_id.id,
                    'bom_id': bom_id.id,
                    'product_uom_id': item.product_id.uom_id.id,
                    'product_qty': item.adjusted_qty,
                })
                email_log[item.id]['status'] = 'success'
                email_log[item.id]['log'] = 'MO created: ' + mo.name + 'Processing components'

                list_move_raw = [(4, move.id) for move in mo.move_raw_ids.filtered(lambda m: not m.bom_line_id)]
                moves_raw_values = mo._get_moves_raw_values()
                move_raw_dict = {move.bom_line_id.id: move for move in mo.move_raw_ids.filtered(lambda m: m.bom_line_id)}
                for move_raw_values in moves_raw_values:
                    if move_raw_values['bom_line_id'] in move_raw_dict:
                        # update existing entries
                        list_move_raw += [(1, move_raw_dict[move_raw_values['bom_line_id']].id, move_raw_values)]
                    else:
                        # add new entries
                        list_move_raw += [(0, 0, move_raw_values)]
                mo.move_raw_ids = list_move_raw
                email_log[item.id]['status'] = 'success'
                email_log[item.id]['log'] = 'MO created: ' + mo.name
            else:
                email_log[item.id]['status'] = 'warning'
                email_log[item.id]['log'] = 'MO route defined'

        self.env['flspautoemails.bpmemails'].send_email(email_log, 'P00002')
