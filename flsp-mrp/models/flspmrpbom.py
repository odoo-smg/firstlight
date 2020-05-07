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

    # constraints to validate code and description to be unique
    _sql_constraints = [
        ('default_code_unique_flsp',
         'UNIQUE(code)',
         "The Reference must be unique"),
    ]

    def copy(self, default=None):
        default['code'] = self._default_nextbomref()
        return super(flspmrpbom, self).copy(default)
