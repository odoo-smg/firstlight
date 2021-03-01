# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models

class FlspNegativeInvReport(models.Model):
    """
        Class_Name: FlspNegativeInvReport
        Model_Name: flsp.negative.inv.report
        Purpose:    To create a list for products with negative inventory in Manufacturing
        Date:       March/1st/Monday/2021
        Updated:
        Author:     Sami Byaruhanga
    """
    _name = 'flsp.mrp.negative.inv.report'
    _auto = False
    _description = 'Mrp Negative Inventory Report'

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    location_id = fields.Many2one('stock.location', string='Location', readonly=True)
    lot = fields.Many2one('stock.production.lot', string='Lot/SN', readonly=True)
    product_qty = fields.Float(string='Qty', readonly=True)
    product_uom = fields.Many2one('uom.uom', 'UOM', readonly=True)

    product_tmpl_id = fields.Many2one('product.template', string='Product Template', readonly=True)  ###
    # pdct_name = fields.Char()###
    # lot_name = fields.Char()###
    # stck_name = fields.Char()###
    # usage_name = fields.Char()###

    def init(self):
        """
            Purpose: To extract database information and create tree view using the query
        """
        tools.drop_view_if_exists(self._cr, 'flsp_mrp_negative_inv_report')

        query = """
        CREATE or REPLACE VIEW flsp_mrp_negative_inv_report AS(
        SELECT
            sq.id as id,
            pp.id as product_id, 
            pt.id as product_tmpl_id, 
            --pt.name as pdct_name, 
            pp.default_code as default_code,
            sq.quantity as product_qty, 
            uom.id as product_uom, 
            sq.lot_id as lot, 
            --spl.name as lot_name, 
            sq.location_id as location_id, 
            --sl.name as stck_name, 
            sl.complete_name as location
            --sl.usage as usage_name
            
        FROM stock_quant as sq
            inner 	join product_product as pp
            on 		sq.product_id = pp.id
            inner 	join product_template as pt
            on 		pp.product_tmpl_id = pt.id
            inner 	join uom_uom as uom
            on 		pt.uom_id = uom.id
            full 	join stock_production_lot as spl
            on		sq.lot_id = spl.id 
            inner 	join stock_location as sl
            on 		sq.location_id = sl.id
            where 	sl.usage = 'internal' and sq.quantity < 0
        );
        """
        self.env.cr.execute(query)

