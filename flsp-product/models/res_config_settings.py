
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    flsp_part_init = fields.Char(string="Part Number Digit", default="1")
    flsp_sec_param = fields.int(string="Second Par", default="1")
