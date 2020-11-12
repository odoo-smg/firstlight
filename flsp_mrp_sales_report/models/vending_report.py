# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models


class FlspMrpSalesReport(models.Model):
    """
        Class_Name: FlspMrpSalesReports
        Model_Name: flsp.mrp.sales.report
        Purpose:    To create a sold product list for use in Manufacturing
        Date:       Nov/9th/Monday/2020
        Updated:
        Author:     Sami Byaruhanga
    """
    _name = 'flsp.mrp.sales.report'
    _auto = False
    _description = 'Mrp Sales Report'

    order_id = fields.Char('Order Reference', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    country_id = fields.Many2one('res.country', 'Customer Country', readonly=True)
    street = fields.Char('Customer Street', readonly=True)
    city = fields.Char('Customer City', readonly=True)
    zip = fields.Char('Customer Zip', readonly=True)
    commitment_date = fields.Datetime('Scheduled Date', readonly=True)
    date = fields.Datetime('Order Date', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    qty_delivered = fields.Float('Qty Delivered', readonly=True)
    serial_number = fields.Many2one('stock.production.lot', readonly=True)
    return_id = fields.Float('Returned id', readonly=True)
    qty_returned = fields.Float('Qty Returned', readonly=True)
    effective_date = fields.Datetime('Effective date', readonly=True)

    def init(self):
        """
            Purpose: To extract database information and create tree view using the query
        """
        tools.drop_view_if_exists(self._cr, 'flsp_mrp_sales_report')

        query = """
        CREATE or REPLACE VIEW flsp_mrp_sales_report AS (
        SELECT
            sml.id as id,
            rp.id as partner_id,
            so.name as order_id,
            sm.product_id as product_id,
            pt.default_code as default_code,
            case when sm.origin_returned_move_id is null then sml.qty_done else sml.qty_done*(-1) end as qty_delivered,
            case when sm.origin_returned_move_id is not null then sml.qty_done end as qty_returned,
            case when sm.origin_returned_move_id is null then so.commitment_date else sm.date_expected end as commitment_date,
            sm.date as effective_date,
            --so.commitment_date as commitment_date,
            so.date_order as date,
            spl.id as serial_number,
            rp.street as street,
            rp.zip as zip,
            rp.city as city,
            rc.id as country_id,
            sm.origin_returned_move_id as return_id
        from sale_order so
            inner join sale_order_line sol
            on         sol.order_id = so.id
            inner join     product_product as pp
            on            sol.product_id = pp.id
            inner join     product_template as pt
            on            pt.id = pp.product_tmpl_id
            inner join     res_partner as rp
            on             so.partner_id = rp.id
            inner join     stock_move as sm
            on             sm.sale_line_id = sol.id
            inner join     stock_move_line as sml
            on             sml.move_id = sm.id
            left join      stock_production_lot as spl
            on             sml.lot_id = spl.id
            where          so.state in ('sale', 'done')
        );
        """
        self.env.cr.execute(query)
