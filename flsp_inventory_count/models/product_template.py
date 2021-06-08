# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from odoo.exceptions import ValidationError

class Smgproduct(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    flsp_inv_count = fields.Boolean('To count', default=False)
    flsp_inv_date = fields.Date('Last Count')
    flsp_inv_user_id = fields.Many2one('res.users', 'Count Responsible')

    @api.model
    def _flsp_set_to_count(self):
        for product_tmpl in self:
            to_count = self.env['flsp.inv.count'].search([('product_tmpl_id', '=', product_tmpl.id)], limit=1)
            product_prd = self.env['product.product'].search([('product_tmpl_id', '=', product_tmpl.id)], limit=1)
            if to_count:
                product_tmpl.flsp_inv_count = True
                to_count.flsp_inv_count = True
                to_count.flsp_counted = False
            else:
                product_tmpl.flsp_inv_count = True
                flsp_inv = self.env['flsp.inv.count'].create({
                    'product_id': product_prd.id,
                    'name': product_tmpl.name,
                    'default_code': product_tmpl.default_code,
                    'product_tmpl_id': product_tmpl.id,
                    'flsp_inv_count': True,
                    'flsp_counted': False,
                })
        return
