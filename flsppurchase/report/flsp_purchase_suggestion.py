# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class Purcahsesuggestion(models.Model):
    _name = 'report.purchase.suggestion'
    _auto = False
    _description = 'Purchase Suggestion Report'

    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_min_qty = fields.Float('Min. Qty', readonly=True)
    product_qty = fields.Float(string='Qty on Hand', readonly=True)
    curr_outs = fields.Float(String="Demand", readonly=True, help="Includes all confirmed sales orders and manufacturing orders")
    curr_ins = fields.Float(String="Replenishment", readonly=True, help="Includes all confirmed purchase orders and manufacturing orders")
    average_use = fields.Float(String="Avg Use", readonly=True, help="Average usage of the past 3 months.")
    month1_use = fields.Float(String="2020-06 Usage", readonly=True, help="Total usage of last month.")
    month2_use = fields.Float(String="2020-05 Usage", readonly=True, help="Total usage of 2 months ago.")
    month3_use = fields.Float(String="2020-04 Usage", readonly=True, help="Total usage of 3 months ago.")
    suggested_qty = fields.Float(String="Suggested Qty", readonly=True, help="Quantity suggested to buy or produce.")
    qty_rfq = fields.Float(String="RFQ Qty", readonly=True, help="Total Quantity of Requests for Quotation.")
    level_bom = fields.Integer(String="BOM Level", readonly=True, help="Position of the product inside of a BOM.")
    route_buy = fields.Selection([('buy', 'To Buy'),('na' , 'Non Applicable'),], string='To Buy', readonly=True)
    route_mfg = fields.Selection([('mfg', 'To Manufacture'),('na' , 'Non Applicable'),], string='To Produce', readonly=True)
    state = fields.Selection([
        ('buy', 'To Buy'),
        ('ok' , 'No Action'),
        ('po' , 'Confirm PO'),
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
            pp.flsp_route_buy as route_buy,
            pp.flsp_route_mfg as route_mfg,
            pp.flsp_suggested_qty as suggested_qty,
            pp.flsp_desc AS description,
            pp.flsp_qty AS product_qty,
            pp.flsp_min_qty as product_min_qty
        FROM product_product pp
        where flsp_type = 'product'
        group by  pp.id, flsp_desc, default_code, flsp_route_buy, flsp_route_mfg
        );
        """
        self.env.cr.execute(query)
