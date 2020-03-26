# -*- coding: utf-8 -*-

from odoo import fields, models, api


class smgproductprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_acc_valid   = fields.Boolean(string="Acconting Validated", readonly=True)

    def button_acc_valid(self, cr, uid, ids, context=None):
        assignment_ids = product_template.search(cr, uid, [('id', '=', record.id)], context=context)
            if assignment_ids:
                product_template.write(cr, uid, assignment_ids, {'flsp_acc_valid': True}, context=context)
        return self.write({'flsp_acc_valid': True})

    def button_acc_valid_off(self):
        return self.write({'flsp_acc_valid': False})
