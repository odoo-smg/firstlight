
from odoo import fields, models

class FLSPConfigSettings(models.TransientModel):

    flsp_part_init = fields.Char("Part Number Digit", default='1')
