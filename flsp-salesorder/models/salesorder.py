# -*- coding: utf-8 -*-

from odoo import fields, models, api


class flspsalesorder(models.Model):
    _inherit = 'sale.order'

    flsp_so_user_id = fields.Many2one('res.users', string="Salesperson 2")
    flsp_amount_deposit = fields.Monetary(string='Deposit Payment', store=True, copy=False, readonly=True)

    @api.onchange('partner_id')
    def flsp_partner_onchange(self):
        self.flsp_so_user_id = self.partner_id.flsp_user_id.id
        return {
            'value': {
                'flsp_so_user_id': self.partner_id.flsp_user_id.id
            },
        }

class flspsalesorderline(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom_qty')
    def flsp_product_uom_qty_onchange(self):
        ret_val = {}
        value_ret = self.product_uom_qty
        if self.product_uom_qty < self.product_template_id.flsp_min_qty:
            value_ret = self.product_template_id.flsp_min_qty
            self.product_uom_qty = value_ret
            ret_val = {'value': {'product_uom_qty': value_ret}}
        return ret_val

    @api.onchange('product_template_id')
    def flsp_product_template_id_onchange(self):
        ret_val = {}
        value_ret = self.product_uom_qty
        if self.product_uom_qty < self.product_template_id.flsp_min_qty:
            value_ret = self.product_template_id.flsp_min_qty
            self.product_uom_qty = value_ret
            ret_val = {'value': {'product_uom_qty': value_ret}}
        return ret_val
