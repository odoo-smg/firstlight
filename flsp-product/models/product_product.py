# -*- coding: utf-8 -*-

from odoo import fields, models, api


class smgproductprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_acc_valid   = fields.Boolean(string="Acconting Validated", readonly=True)

    def button_acc_valid(self):
        #product_id = self.env['product.product'].browse(self.env.context['default_product_id'])
        current_product = self.env['product.template'].search([('id', '=', self.product_tmpl_id)])
        if current_product:
            current_product.write({'flsp_acc_valid': True}, context=None)
        return self.write({'flsp_acc_valid': True})

    def button_acc_valid_off(self):
        return self.write({'flsp_acc_valid': False})
