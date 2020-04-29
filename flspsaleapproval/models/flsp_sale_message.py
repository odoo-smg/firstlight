# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Saleflspmessage(models.TransientModel):
    _name = 'flspsaleapproval.saleflspmessage'
    _description = "Wizard: Message on Sales"

    @api.model
    def default_get(self, fields):
        res = super(Saleflspmessage, self).default_get(fields)
        sale_order = self.env['sale.order']
        order_id = self.env.context.get('default_order_id') or self.env.context.get('active_id')
        if order_id:
            sale_order = self.env['sale.order'].browse(order_id)
        if sale_order.exists():
            if 'partner_id' in fields:
                res['partner_id'] = sale_order.partner_id.id

        return res

    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)

    def flsp_open_sale_message(self):
        self.order_line.order_id |= self.order_id
        return {}

