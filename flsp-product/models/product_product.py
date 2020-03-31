# -*- coding: utf-8 -*-

from odoo import fields, models, api


class smgproductprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_acc_valid   = fields.Boolean(string="Acconting Validated", readonly=True)

    def button_acc_valid(self):
        self.product_tmpl_id.flsp_acc_valid = True
        return self.write({'flsp_acc_valid': True})

    def button_acc_valid_off(self):
        self.product_tmpl_id.flsp_acc_valid = False
        return self.write({'flsp_acc_valid': False})
