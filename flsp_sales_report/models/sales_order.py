# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SalesOrder(models.Model):
    _inherit = "sale.order"
    _check_company_auto = True

    flsp_utm_other_source = fields.Char(string="Other Source Desc.")
    flsp_source_name = fields.Char(string="Other Source")

    @api.onchange('source_id')
    def _onchange_source_id(self):
        self.flsp_source_name = self.source_id.name

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id and self.user_id.sale_team_id:
            self.team_id = False #self.user_id.sale_team_id
