# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Saleflsprejectwizard(models.TransientModel):
    _name = 'flspsaleapproval.saleflsprejectwizard'
    _description = "Wizard: testing my wizard"

    @api.model
    def default_get(self, fields):
        res = super(Saleflsprejectwizard, self).default_get(fields)
        sale_order = self.env['sale.order']
        order_id = self.env.context.get('default_order_id') or self.env.context.get('active_id')
        if order_id:
            sale_order = self.env['sale.order'].browse(order_id)
        if sale_order.exists():
            if 'order_id' in fields:
                res['order_id'] = sale_order.id
            if 'validity_date' in fields:
                res['validity_date'] = sale_order.validity_date
            if 'partner_id' in fields:
                res['partner_id'] = sale_order.partner_id.id

        res = self._convert_to_write(res)
        return res

    order_id = fields.Many2one('sale.order', string='Order Reference', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    validity_date = fields.Date(string='Expiration')
    reject_reason = fields.Text(string="Notes")

    def flsp_reject(self):
        self.ensure_one()

        self.order_id.write({'flsp_state': 'draft'})
        self.order_id.write({'flsp_approval_approved': False})
        self.order_id.write({'flsp_approval_requested': False})

        self.order_id.message_post(body='Order Rejected: ' + self.reject_reason)
        #self.order_id.message_post_with_view(
        #    'flspsaleapproval.flsp_salesapprv_rejected',
        #    subtype_id=self.env.ref('mail.mt_note').id)
        self.env['flspautoemails.bpmemails'].send_email(self, 'SO0003')
        return {'type': 'ir.actions.act_window_close'}

        self.order_id.write({'flsp_approval_requested': False})

        body = '<p>Hi there, </p>'
        body += '<br/>'
        body += '<p>The discount approval requested for the quotation: '+self.order_id.name+' has been rejected.</p>'
        body += '<br/><br/><br/>'

        body += '<p>Here is the note from your manager: </p>'
        body += self.reject_reason
        body += '<br/><br/><br/>'
        body += '<div style = "text-align: center;" >'
        body += '  <a href = "https://odoo-smg-firstlight1.odoo.com/web#action=408&amp;model=sale.order&amp;view_type=list&amp;cids=1&amp;menu_id=230" style = "background: #1abc9c; padding: 20px; text-decoration: none; color: #fff; border-radius: 5px; font-size: 16px;" class ="o_default_snippet_text">Access Sales Order</a>'
        body += '  <br/><br/><br/>'
        body += '</div>'
        body += '<p>Thank you!</p>'

        self.env['mail.mail'].create({
            'body_html': body,
            'subject': 'Odoo - Sales Discount Rejected',
            'email_to': 'alexandresousa@smartrendmfg.com; '+self.order_id.user_id.login,
            'auto_delete': True,
        }).send()


        return {'type': 'ir.actions.act_window_close'}

        #self.order_id.write({'validity_date': self.validity_date,})

    def flsp_open_reject_wizard(self):
        self.order_line.order_id |= self.order_id
        return {}
