# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
from datetime import date, datetime
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class ManageCusomerBadge(models.TransientModel):
    """
        Class_Name: ManageCusomerBadge
        Model_Name: flsp.manage.customer.badge
        Purpose:    To create a model used in the wizard to manage customer badge
        Date:       April/09th/2021
        Author:     Perry He
    """

    _name = 'flsp.manage.customer.badge'
    _description = "ManageCusomerBadge"

    customer = fields.Many2one('res.partner', string="Customer")
    flsp_cb_id = fields.Many2one('flsp.customer.badge', string="Customer Badge", ondelete='cascade')
    note = fields.Char(string="Note of Change")

    @api.model
    def default_get(self, fields):
        """
            Purpose: to get the default values from the customer model and load in the wizard
        """
        res = super(ManageCusomerBadge, self).default_get(fields)
        customer_id = self.env.context.get('default_customer_id')
        if customer_id:
            customer = self.env['res.partner'].browse(customer_id)
        if customer.exists():
            if 'customer' in fields:
                res['customer'] = customer
            if 'flsp_cb_id' in fields:
                res['flsp_cb_id'] = customer.flsp_cb_id

        res = self._convert_to_write(res)
        return res

    def button_submit_for_approval(self):
        self.ensure_one()

        flsp_current_cb_id = self.customer.flsp_cb_id
        if flsp_current_cb_id == self.flsp_cb_id:
            raise UserError(_("The new Customer Badge is as same as the current one, skip to submit request"))

        # create request
        request_id = self.env['flsp.customer.badge.request'].create({
            'status': 'submitted',
            'customer_id': self.customer.id,
            'flsp_current_cb_id': flsp_current_cb_id.id,
            'flsp_new_cb_id': self.flsp_cb_id.id,
            'requester': self.env.user.id,
            'note': self.note,
        })

        # send email
        # result = {'badgeManagement': {'request_id': '123', 'status': 'submitted', 'action': 'SET', 'current_name': 'Bronze', 'new_name': 'Silver', 'customer_id': {'id': 34, 'name': 'smg'}, 'requester': 'Adam', 'note': 'customer promotion', 'update_date': '2021-04-09 16:00:00'}}
        try:
            badgeManagement = {
                'request_id': request_id.id,
                'status': 'submitted',
                'action': 'SET' if self.flsp_cb_id else 'DELETE',
                'current_name': flsp_current_cb_id.name if flsp_current_cb_id else "",
                'new_name': self.flsp_cb_id.name if self.flsp_cb_id else "",
                'requester': self.env.user.name if self.env.user else "",
                'note': self.note if self.note else "",
                'customer_id': {
                    'id': self.customer.id,
                    'name': self.customer.name
                },
                'update_date': self.write_date.strftime("%c"),
            }
            self.env['flspautoemails.bpmemails'].send_email(badgeManagement, 'SO0019')
        except Exception as e:
            _logger.warning("Exception happens when to send email: " + str(e))

        return {'type': 'ir.actions.act_window_close'}

    def button_customer_badge_records(self):
        self.ensure_one()

        action = self.env.ref('flsp_customer_badge.launch_customer_badge_record').read()[0]
        action['domain'] = [('customer_id', '=', self.customer.id)]
        return action