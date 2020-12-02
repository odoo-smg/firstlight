# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Saleflspcancelwizard(models.TransientModel):
    _name = 'flspsaleapproval.saleflspcancelwizard'
    _description = "Wizard: Cancel"

    @api.model
    def default_get(self, fields):
        res = super(Saleflspcancelwizard, self).default_get(fields)
        sale_order = self.env['sale.order']
        order_id = self.env.context.get('default_order_id') or self.env.context.get('active_id')
        if order_id:
            sale_order = self.env['sale.order'].browse(order_id)
        if sale_order.exists():
            if 'order_id' in fields:
                res['order_id'] = sale_order.id
            if 'partner_id' in fields:
                res['partner_id'] = sale_order.partner_id.id

        res = self._convert_to_write(res)
        return res

    order_id = fields.Many2one('sale.order', string='Order Reference', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    cancel_reason = fields.Text(string="Notes")

    def flsp_cancel(self):
        self.ensure_one()

        self.order_id.write({'flsp_state': 'draft'})
        self.order_id.write({'flsp_approval_approved': False})
        self.order_id.write({'flsp_approval_requested': False})

        self.env['flspautoemails.bpmemails'].send_email(self, 'SO0015')

        self.order_id.wiz_cancel_confirm()

        self.order_id.message_post(
            body='Order Cancelled: ' + self.cancel_reason,
            subtype="mail.mt_note")
        return {'type': 'ir.actions.act_window_close'}
