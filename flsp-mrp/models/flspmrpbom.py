# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class flspmrpbom(models.Model):
    _inherit = 'mrp.bom'
    _check_company_auto = True


    code = fields.Char('Reference', required=True)

    # constraints to validate code and description to be unique
    _sql_constraints = [
        ('default_code_unique_flsp',
         'UNIQUE(default_code)',
         "The Reference must be unique"),
    ]
