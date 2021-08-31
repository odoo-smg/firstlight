# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class flspCustomerBsalesorder(models.Model):
    _inherit = 'sale.order'

    # fields for customer badge(cb)
    flsp_cb_id = fields.Many2one(related='partner_id.flsp_cb_id', readonly=True)
    flsp_cb_image = fields.Image(related='flsp_cb_id.image_1920', readonly=True)
    flsp_cb_sale_discount = fields.Float(related='flsp_cb_id.sale_discount', readonly=True)
    flsp_cb_freight_units_5_to_10_discount = fields.Float(related='flsp_cb_id.freight_units_5_to_10_discount', readonly=True)
    flsp_cb_freight_units_over_10_discount = fields.Float(related='flsp_cb_id.freight_units_over_10_discount', readonly=True)

    @api.depends('order_line.discount')
    def _calc_sale_approval(self):
        self.flsp_approval_required = False
        flsp_sales_discount_approval = self.env['ir.config_parameter'].sudo().get_param('flsp_sales_discount_approval')
        so_flsp_max_percent_approval = self.env.company.so_flsp_max_percent_approval
        customer_badge_discount = 0
        if self.partner_id and self.flsp_cb_id and self.flsp_cb_sale_discount:
            customer_badge_discount = self.flsp_cb_sale_discount
        total_discount = 0.0
        self.flsp_order_line_count = 0
        for line in self.order_line:
            self.flsp_order_line_count = self.flsp_order_line_count +1
            if flsp_sales_discount_approval and (line.discount > so_flsp_max_percent_approval) and (line.discount > customer_badge_discount):
                self.flsp_approval_required = True
            total_discount += line.discount
