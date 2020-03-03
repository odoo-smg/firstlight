
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    flsp_part_init = fields.Char(related="company_id.flsp_part_init", default="1", readonly=False)
    flsp_sec_param = fields.Integer(string="Second Par", default=1)
