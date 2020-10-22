# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class flspproduction(models.Model):
    _inherit = 'mrp.production'
    _check_company_auto = True

    flsp_partner_id = fields.Many2one('res.partner', string='Customer for Labels')
