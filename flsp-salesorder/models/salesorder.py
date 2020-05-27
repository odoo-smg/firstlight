# -*- coding: utf-8 -*-

from odoo import fields, models, api


class flspsalesorder(models.Model):
    _inherit = 'sale.order'

    flsp_so_user_id = fields.Many2one('res.users', string="Salesperson 2")

    @api.onchange('partner_id')
    def flsp_partner_onchange(self):
        return {
            'value': {
                'flsp_so_user_id': self.partner_id.flsp_user_id.id
            },
        }

class flspsalesorderline(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom_qty')
    def flsp_product_uom_qty_onchange(self):
        value_ret = self.product_uom_qty
        if self.product_uom_qty < self.product_template_id.flsp_min_qty:
            value_ret = self.product_template_id.flsp_min_qty
        return {
            'value': {
                'product_uom_qty': value_ret
            },
        }

    @api.onchange('product_template_id')
    def flsp_product_template_id_onchange(self):
        value_ret = self.product_uom_qty
        if self.product_uom_qty < self.product_template_id.flsp_min_qty:
            value_ret = self.product_template_id.flsp_min_qty
        return {
            'value': {
                'product_uom_qty': value_ret
            },
        }
