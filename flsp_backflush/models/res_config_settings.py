from odoo import api, fields, models, modules


class BackflushSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    flsp_backflush = fields.Boolean(string="Backflush Consumption", config_parameter='flsp_backflush')

