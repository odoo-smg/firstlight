# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class flspmrpbom(models.Model):
    _inherit = 'mrp.bom'
    _check_company_auto = True

    @api.model
    def _default_nextbomref(self):
        res = (datetime.now()).strftime('%Y%m%d%H%M%S')
        return res

    code = fields.Char('Reference', required=True, default=_default_nextbomref)

    type = fields.Selection([
        ('normal', 'Manufacture this product'),
        ('phantom', 'Phantom')], 'BoM Type',
        default='normal', required=True)

    # constraints to validate code and description to be unique
    _sql_constraints = [
        ('default_code_unique_flsp',
         'UNIQUE(code)',
         "The Reference must be unique"),
    ]

    @api.constrains('product_tmpl_id','type')
    def _constraint_phanthom_consumable(self):
        if self.type == 'phantom' and self.product_tmpl_id.type != 'consu':
            raise ValidationError('The BOM Type Phantom can be used only for consumable products.'
                  '\nPlease review the product selected.')
