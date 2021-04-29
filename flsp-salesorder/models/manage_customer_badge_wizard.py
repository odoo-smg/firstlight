# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import date, datetime

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

    customer_id = fields.Many2one('res.partner', string="Customer")
    flsp_cb_id = fields.Many2one('flsp.customer.badge', string="Customer Badge", ondelete='cascade', required='True')

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
            if 'flsp_cb_id' in fields:
                res['flsp_cb_id'] = customer.flsp_cb_id

        res = self._convert_to_write(res)
        return res

    def button_set_customer_badge(self):
        """
            Purpose: 1) Button used in wizard to add/update the badge
                     2) send the email only when it is done
        """
        self.ensure_one()
        self.customer_id.write({'flsp_cb_id': self.flsp_cb_id})

        # result = {'badgeManagement': {'status': 'SET', 'name': 'Bronze', 'customer_id': {'id': 34, 'name': 'smg'}, 'update_date': '2021-04-09 16:00:00'}}
        try:
            badgeManagement = {
                'status': 'SET',
                'name': self.flsp_cb_id.name,
                'customer_id': {
                    'id': self.customer_id.id,
                    'name': self.customer_id.name
                },
                'update_date': self.write_date.strftime("%c"),
                }
            self.env['flspautoemails.bpmemails'].send_email(badgeManagement, 'AC0004')
        except Exception as e:
            _logger.warning("Exception happens when to send email: " + str(e))

        return {'type': 'ir.actions.act_window_close'}

    def button_delete_customer_badge(self):
        """
            Purpose: 1) Button used in wizard to delete the badge
                     2) send the email only when it is done
        """
        self.ensure_one()
        self.customer_id.write({'flsp_cb_id': False})

        try:
            badgeManagement = {
                'status': 'DELETED',
                'name': self.flsp_cb_id.name,
                'customer_id': {
                    'id': self.customer_id.id,
                    'name': self.customer_id.name
                },
                'update_date': self.write_date.strftime("%c"),
                }
            self.env['flspautoemails.bpmemails'].send_email(badgeManagement, 'AC0004')
        except Exception as e:
            _logger.warning("Exception happens when to send email: " + str(e))

        return {'type': 'ir.actions.act_window_close'}