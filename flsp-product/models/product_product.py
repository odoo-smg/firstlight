# -*- coding: utf-8 -*-

from odoo import fields, models, api


class smgproductprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_acc_valid   = fields.Boolean(string="Acconting Validated", readonly=True)

    def button_acc_valid(self):
        assignment_ids = product.template.search(cr, uid, [('id', '=', record.id)], context=None)
        if assignment_ids:
            product.template.write({'flsp_acc_valid': True}, context=None)
        return self.write({'flsp_acc_valid': True})

    def button_acc_valid_off(self):
        return self.write({'flsp_acc_valid': False})
