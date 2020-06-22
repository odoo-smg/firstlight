# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import api, fields, models, exceptions


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
