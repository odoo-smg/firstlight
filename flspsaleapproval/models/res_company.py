# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Flspcompany(models.Model):
    _inherit = "res.company"

    so_flsp_max_percent_approval = fields.Float(string="Max Discount Allowed", help="Minimum discount percent allowed")
    #flsp_gst_reg_no = fields.Char('GST Reg No.', help="GST Reg No.", groups="base.group_system")
    _columns = {'flsp_gst_reg_no':fields.Char('GST Reg No.', help="GST Reg No.", groups="base.group_system"),}
    
