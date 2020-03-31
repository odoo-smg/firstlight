# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flsppartner(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True

    # Account review enforcement
    #    if (self.env.uid != 8):
    flsp_acc_valid   = fields.Boolean(string="Acconting Validated", readonly=True)
