# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class FlspCustomerBadgeRequest(models.Model):
    _name = 'flsp.customer.badge.request'
    _inherit = ['image.mixin']
    _description = 'FLSP - request of customer badge'

    status = fields.Selection([
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', required=True)

    customer_id = fields.Many2one('res.partner', string="Customer", required='True')
    flsp_current_cb_id = fields.Many2one('flsp.customer.badge', string="Current Customer Badge", ondelete='cascade')
    flsp_new_cb_id = fields.Many2one('flsp.customer.badge', string="New Customer Badge", ondelete='cascade')
    requester = fields.Many2one('res.users', string='Requester', required=True, default=lambda self: self.env.user)
    responder = fields.Many2one('res.users', string='Responder')
    note = fields.Char(string="Note")
    message = fields.Char(string="System Message")

    _sql_constraints = [
        ('different_new_customer_badge',
         'CHECK (flsp_new_cb_id != flsp_current_cb_id)',
         "The new 'Customer Badge' to be set must be different from the current one"),
    ]

    def update_badge(self):
        # set customer badge for customer
        self.customer_id.write({'flsp_cb_id': self.flsp_new_cb_id})

        # set customer badge for delivery addresses
        customer_delivery_addrs = self.env['res.partner'].search([('parent_id', '=', self.customer_id.id)])
        for addr in customer_delivery_addrs:
            addr.write({'flsp_cb_id': self.flsp_new_cb_id})

    def button_approve(self):
        """
            Purpose: 1) Button used to approve the badge change
                     2) send the email only when it is done
        """
        self.ensure_one()

        self.message = False

        if not self.status:
            raise UserError(_("The status of approval request can't be False"))

        if self.status == 'rejected':
            self.message = "The approval request has been rejected. Unable to approve it."
            return

        if self.status == 'approved':
            self.message = "The approval request has been approved. Skip to approve it again."
            return

        self.status = 'approved'
        self.responder = self.env.user

        self.update_badge()

        # keep it in the history record
        if self.flsp_current_cb_id:
            current_record = self.env['flsp.customer.badge.record'].search(
                [('customer_id', '=', self.customer_id.id), ('flsp_cb_id', '=', self.flsp_current_cb_id.id),
                 ('end_date', '=', False)], order='start_date desc', limit=1)
            if current_record:
                current_record.end_date = self.write_date

        self.env['flsp.customer.badge.record'].create({
            'customer_id': self.customer_id.id,
            'flsp_cb_id': self.flsp_new_cb_id.id,
            'start_date': self.write_date,
        })

        # result = {'badgeManagement': {'request_id': '123', 'status': 'approved', 'action': 'SET', 'current_name': 'Bronze', 'new_name': 'Silver', 'requester': 'Adam', 'note': 'customer promotion', 'responder': 'Cam', 'customer_id': {'id': 34, 'name': 'smg'}, 'update_date': '2021-04-09 16:00:00'}}
        try:
            badgeManagement = {
                'request_id': self.id,
                'status': self.status,
                'action': 'SET' if self.flsp_new_cb_id else 'DELETE',
                'current_name': self.flsp_current_cb_id.name if self.flsp_current_cb_id else "",
                'new_name': self.flsp_new_cb_id.name if self.flsp_new_cb_id else "",
                'requester': self.requester.name if self.requester else "",
                'note': self.note if self.note else "",
                'responder': self.responder.name if self.responder else "",
                'customer_id': {
                    'id': self.customer_id.id,
                    'name': self.customer_id.name
                },
                'update_date': self.write_date.strftime("%c"),
            }
            self.env['flspautoemails.bpmemails'].send_email(badgeManagement, 'SO0020')
        except Exception as e:
            _logger.warning("Exception happens when to send email: " + str(e))

        self.message = 'The request is approved'
        return {'type': 'ir.actions.act_window_close'}

    def button_reject(self):
        """
            Purpose: 1) Button used to reject the badge change
                     2) send the email only when it is done
        """
        self.ensure_one()

        self.message = False

        if not self.status:
            raise UserError(_("The status of approval request can't be False"))

        if self.status == 'rejected':
            self.message = "The approval request has been rejected. Skip to reject it again."
            return

        if self.status == 'approved':
            self.message = "The approval request has been approved. Unable to reject it."
            return

        self.status = 'rejected'
        self.responder = self.env.user

        # result = {'badgeManagement': {'request_id': '123', 'status': 'rejected', 'action': 'SET', 'current_name': 'Bronze', 'new_name': 'Silver', 'requester': 'Adam', 'responder': 'Cam', 'note': 'customer promotion', 'customer_id': {'id': 34, 'name': 'smg'}, 'update_date': '2021-04-09 16:00:00'}}
        try:
            badgeManagement = {
                'request_id': self.id,
                'status': self.status,
                'action': 'SET' if self.flsp_new_cb_id else 'DELETE',
                'current_name': self.flsp_current_cb_id.name if self.flsp_current_cb_id else "",
                'new_name': self.flsp_new_cb_id.name if self.flsp_new_cb_id else "",
                'requester': self.requester.name if self.requester else "",
                'note': self.note if self.note else "",
                'responder': self.responder.name if self.responder else "",
                'customer_id': {
                    'id': self.customer_id.id,
                    'name': self.customer_id.name
                },
                'update_date': self.write_date.strftime("%c"),
            }
            self.env['flspautoemails.bpmemails'].send_email(badgeManagement, 'SO0021')
        except Exception as e:
            _logger.warning("Exception happens when to send email: " + str(e))

        self.message = 'The request is rejected'
        return {'type': 'ir.actions.act_window_close'}

