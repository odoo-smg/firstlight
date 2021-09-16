# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class flspProductionSubstitution(models.Model):
    _inherit = 'mrp.production'
    _check_company_auto = True

    flsp_substituted = fields.Boolean('Was Substituted')
