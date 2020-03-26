# -*- coding: utf-8 -*-

from odoo import fields, models


class smgproductprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_acc_valid   = fields.Boolean(string="Acconting Validated", readonly=True)

    def button_acc_valid(self):
        return self.write({'flsp_acc_valid': True})

    def button_acc_valid_off(self):
        return self.write({'flsp_acc_valid': False})
