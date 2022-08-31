# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api
from datetime import datetime


class FlspMrppurchaseReport(models.Model):
    _name = 'report.flsp_mrp_purchase'
    _auto = False
    _description = 'FLSP MRP purchase Report'

    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_qty = fields.Float(string='Qty on Hand', readonly=True)
    stock_qty = fields.Float(string='Stock Qty', readonly=True)
    wip_qty = fields.Float(string='WIP Qty', readonly=True)
    vendor_id = fields.Many2one('res.partner', string='Supplier')
    required_by = fields.Date(string="Required by", readonly=True)
    suggested_qty = fields.Float(string="Suggested Qty", readonly=True, help="Quantity suggested to buy or produce.")
    adjusted_qty = fields.Float(string="Adjusted Qty", help="Adjust the quantity to be executed.")
    start_date = fields.Date(string="Start Date", readonly=True)
    deadline_date = fields.Date(string="Deadline", readonly=True)
    rationale = fields.Html(string='Rationale')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_flsp_mrp_purchase')

        query = """
        CREATE or REPLACE VIEW report_flsp_mrp_purchase AS (
select      sm.id as id,
            'pp.flsp_default_code' as default_code,
            pp.id as product_id,
            pp.product_tmpl_id as product_tmpl_id,
            1 as suggested_qty,
            1 as adjusted_qty,
            'pp.flsp_desc' AS description,
            1 AS product_qty,
            NULL as start_date,
            NULL as deadline_date,
            '<p>testing</p></br>second Line"' as rationale,
            1 as stock_qty,
            1 as wip_qty,
            1 as vendor_id,
            NULL as required_by

from       stock_picking as sp
inner join sale_order as so
on         so.id = sp.sale_id
and        so.state = 'done'
inner join res_partner as rp
on         so.partner_id  = rp.id
inner join stock_move as sm
on         sp.id = sm.picking_id
inner join product_product as pp
on         sm.product_id = pp.id
inner join product_template as pt
on         pp.product_tmpl_id = pt.id
where      sp.state = 'done'
);
        """
        self.env.cr.execute(query)
