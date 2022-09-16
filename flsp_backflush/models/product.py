# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Backflushproducts(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    flsp_backflush = fields.Boolean(string="Backflush", default=False)
    flsp_bf_check = fields.Boolean(string="BF Check", default=False)
    flsp_show_backflush = fields.Boolean(string="Show Backflush", compute="_flsp_compute_backflush")


    def _flsp_compute_backflush(self):
        for record in self:
            record.flsp_show_backflush = self.env['ir.config_parameter'].get_param('flsp_backflush', False)
