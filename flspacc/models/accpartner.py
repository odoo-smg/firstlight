# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flsppartner(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True

    # Account review enforcement
    #    if (self.env.uid != 8):
    flsp_acc_valid   = fields.Boolean(string="Accounting Validated", readonly=True)

    def button_partner_acc_valid(self):
        self.env['flspautoemails.bpmemails'].send_email(self, 'SO0005')
        return self.write({'flsp_acc_valid': True})

    def button_partner_acc_valid_off(self):
        return self.write({'flsp_acc_valid': False})
