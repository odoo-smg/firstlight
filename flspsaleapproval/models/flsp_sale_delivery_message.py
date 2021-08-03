# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FlspSaleDeliveryMessage(models.TransientModel):
    _name = 'flsp.sale.delivery.message'
    _description = "Wizard: Message on Sales Delivery"

    @api.model
    def default_get(self, fields):
        res = super(FlspSaleDeliveryMessage, self).default_get(fields)
        order_id = self.env.context.get('default_order_id') or self.env.context.get('active_id')
        if order_id:
            sale_order = self.env['sale.order'].browse(order_id)
        if sale_order.exists():
            if 'order_id' in fields:
                res['order_id'] = sale_order.id
            if 'partner_shipping_id' in fields:
                res['partner_shipping_id'] = sale_order.partner_shipping_id.id
            if 'delivery_contact' in fields:
                res['delivery_contact'] = sale_order.flsp_delivery_contact.id
            if 'delivery_tax' in fields:
                res['delivery_tax'] = sale_order.flsp_delivery_tax

        return res

    order_id = fields.Many2one('sale.order', string='Order Reference', readonly=True)
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address', readonly=True)
    delivery_contact = fields.Many2one("flsp.contact", string='Delivery Contact', help='The contact for the "Delivery Adress"')
    delivery_tax = fields.Char(string='Tax ID', help='The Tax ID for the "Delivery Adress"')
