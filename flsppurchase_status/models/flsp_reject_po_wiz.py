# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class FlsprejectPowiz(models.TransientModel):
    _name = 'flsp.reject.po.wiz'
    _description = "Wizard: Reject PO"

    @api.model
    def default_get(self, fields):
        res = super(FlsprejectPowiz, self).default_get(fields)
        purchase_order = self.env['purchase.order']
        order_id = self.env.context.get('default_order_id') or self.env.context.get('active_id')
        if order_id:
            purchase_order = self.env['purchase.order'].browse(order_id)
        if purchase_order.exists():
            if 'order_id' in fields:
                res['order_id'] = purchase_order.id
            if 'partner_id' in fields:
                res['partner_id'] = purchase_order.partner_id.id

        res = self._convert_to_write(res)
        return res

    order_id = fields.Many2one('purchase.order', string='Order Reference', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Supplier', readonly=True)
    reject_reason = fields.Text(string="Notes", required=True)

    def flsp_reject(self):
        self.ensure_one()

        self.order_id.write({'state': 'draft'})
        self.order_id.write({'flsp_po_status': 'request'})

        self.order_id.message_post(
            body='Order Rejected: ' + self.reject_reason,
            subtype="mail.mt_note")
        self.env['flspautoemails.bpmemails'].send_email(self, 'P00007')

        return {'type': 'ir.actions.act_window_close'}
