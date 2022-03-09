# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api
from datetime import datetime


class SummarizedBomReport(models.Model):
    #_name = 'report.flsp.summarized.bom'
    _name = 'report.mrp.prd.simulation'
    _auto = False
    _description = 'Summarized BOM Report'

    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Part #', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    bom_id = fields.Many2one(comodel_name="mrp.bom", string="BOM")
    quanty_available = fields.Float(string='On Hand', readonly=True)
    weeks_available = fields.Float(string="Weeks Available")
    product_qty = fields.Float(string='Qty Req/Week', readonly=True)
    product_uom = fields.Many2one(comodel_name="uom.uom", string='UofM', readonly=True)
    level_bom = fields.Integer(String="BOM Level", readonly=True, help="Position of the product inside of a BOM.")

    def name_get(self):
        res = []
        for line in self:
            if line.default_code:
                name = line.default_code
            else:
                name = line.id
            res.append((line.id, name))
        return res


    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_mrp_prd_simulation')

        query = """
        CREATE or REPLACE VIEW report_mrp_prd_simulation AS (
        SELECT
            max(id) as id,
            description,
            default_code,
            product_tmpl_id,
            product_id,
            max(bom_id) as bom_id,
            max(quanty_available) as quanty_available,
            (max(quanty_available)/sum(product_qty)) as weeks_available,
            sum(product_qty) as product_qty,
            max(product_uom) as product_uom,
            max(level_bom) as level_bom
        FROM flsp_mrp_prd_simulation_line
		group by product_id, product_tmpl_id, description, default_code );"""

        self.env.cr.execute(query)


    def action_view_details(self):
        action = self.env.ref('flsp_mrp_summarized_bom.flsp_summarized_bom_details_action').read()[0]
        # Set ignore_session: read to prevent reading previous options
        print('Showing list for item:')
        print(self.product_id)
        action.update({'domain': [('product_id', '=', self.product_id.id)],})
        return action
