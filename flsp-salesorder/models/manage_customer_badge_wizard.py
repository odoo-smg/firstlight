# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime

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
    flsp_customer_badge_id = fields.Many2one('flsp.customer.badge', string="Customer Badge", ondelete='cascade', required='True')

    # Used to help in sending email
    update_date = fields.Date(string="Date of Managing Customer Badge")

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
            if 'flsp_customer_badge_id' in fields:
                res['flsp_customer_badge_id'] = customer.flsp_customer_badge_id

        res = self._convert_to_write(res)
        return res

    def button_set_customer_badge(self):
        """
            Purpose: 1) Button used in wizard to add/update the badge
                     2) send the email only when it is done
        """
        self.ensure_one()
        self.customer_id.write({'flsp_customer_badge_id': self.flsp_customer_badge_id})
        self.update_date = datetime.now()

        # result = {'badgeManagement': {'status': 'SET', 'name': 'Bronze', 'customer_id': {'id': 34, 'name': 'smg'}, 'update_date': '2021-04-09 16:00:00'}}
        badgeManagement = {
            'status': 'SET',
            'name': self.flsp_customer_badge_id.name,
            'customer_id': {
                'id': self.customer_id.id, 
                'name': self.customer_id.name
            },
            'update_date': self.update_date,
            }
        self.env['flspautoemails.bpmemails'].send_email(badgeManagement, 'AC0004')

        return {'type': 'ir.actions.act_window_close'}

    def button_delete_customer_badge(self):
        """
            Purpose: 1) Button used in wizard to delete the badge
                     2) send the email only when it is done
        """
        self.ensure_one()
        self.customer_id.write({'flsp_customer_badge_id': False})
        self.update_date = datetime.now()

        badgeManagement = {
            'status': 'DELETED',
            'name': self.flsp_customer_badge_id.name,
            'customer_id': {
                'id': self.customer_id.id, 
                'name': self.customer_id.name
            },
            'update_date': self.update_date,
            }
        self.env['flspautoemails.bpmemails'].send_email(badgeManagement, 'AC0004')

        return {'type': 'ir.actions.act_window_close'}