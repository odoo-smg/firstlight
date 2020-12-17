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
    # New fields to control ECO enforcement
    flsp_eco_enforce = fields.Many2one('mrp.eco', string="ECO", store=False)
    flsp_bom_plm_valid = fields.Boolean(string="PLM Validated")

    type = fields.Selection([
        ('normal', 'Manufacture this product'),
        ('phantom', 'Phantom')], 'BoM Type',
        default='normal', required=True)

    @api.onchange('flsp_eco_enforce')
    def flsp_eco_enforce_onchange(self):
        self.flsp_plm_valid = False
        return {
            'value': {
                'flsp_bom_plm_valid': False
            },
        }

    # constraints to validate code and description to be unique
    _sql_constraints = [
        ('default_code_unique_flsp',
         'UNIQUE(code)',
         "The Reference must be unique"),
    ]

    def copy(self, default=None):
        default = dict(default or {})
        default['code'] = self._default_nextbomref()
        default['flsp_bom_plm_valid'] = False
        return super(flspmrpbom, self).copy(default)

    @api.constrains('parent_product_tmpl_id','type')
    def _constraint_phanthom_consumable(self):
        if self.type == 'phantom' and self.product_tmpl_id.type != 'consu':
            raise ValidationError('The BOM Type Phantom can be used only for consumable products.'
                  '\nPlease review the product selected.')
