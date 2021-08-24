# -*- coding: utf-8 -*-

from odoo import models, fields,tools

class FlspProductDeliveryReport(models.Model):
    """
        Class_Name: FlspProductDeliveryReport
        Model_Name: flsp.product.delivery.report
        Purpose:    To hold the results from the wizards delivery search query
        Date:       August.20.2021
        Author:     Kory McCarthy
    """

    _name = 'flsp.product.delivery.report'
    _auto = False
    _description = "Displays the deliveries"

    order_id = fields.Many2one('sale.order', 'Order Reference', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    effective_date = fields.Datetime('Date', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    qty_delivered = fields.Float('Qty Delivered', readonly=True)


    def deliveryReportSearch(self, start, end):
        """
        Called by the wizard file when search is clicked
        Creates an sql view for the report returning all deliveries that occurred
        between the startSearch and endSearch dates
        """

        tools.drop_view_if_exists(self._cr, 'flsp_product_delivery_report')

        query = """
        CREATE or REPLACE VIEW flsp_product_delivery_report AS (
        SELECT
            MAX(sml.id) as id,
            so.id as order_id,
            rp.id as partner_id,
            sm.product_id as product_id,
            pt.default_code as default_code,
            sm.product_qty as qty_delivered,
            sm.date as effective_date
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
            where          sm.state in ('done') 
			AND sm.date >= '%s'
			AND sm.date <= '%s'
		GROUP BY so.id, rp.id, sm.product_id, pt.default_code, sm.product_qty, sm.date
		);
		""" % (start,end)

        self.env.cr.execute(query)



