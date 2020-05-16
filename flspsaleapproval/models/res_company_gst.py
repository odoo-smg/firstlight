# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Flspgstcompany(models.Model):
    _inherit = "res.company"

    flsp_gst_number = fields.Char('GST Reg No.', help="GST Reg No.", groups="base.group_system")
