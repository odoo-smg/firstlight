# -*- coding: utf-8 -*-

from odoo import fields, models, api


class flspstockcustomer(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True

    flsp_show_packing = fields.Boolean(string="Show Packaging on Packing List")
    flsp_supplier_id  = fields.Char(string="Supplier ID(Assigned by Customer)")
    flsp_partner_code = fields.Char(string="Partner Code", readonly=True, compute="_compute_flsp_partner_code")

    def _compute_flsp_partner_code(self):
        if self.id:
            self.flsp_partner_code = ('00000' + str(self.id))[-6:]
