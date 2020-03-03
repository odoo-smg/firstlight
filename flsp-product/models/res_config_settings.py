
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    flsp_part_init = fields.Char(string="First Par", realted='company_id.flsp_part_num_init')
