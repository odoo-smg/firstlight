
from odoo import api, fields, models, modules

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dafault_part_init = fields.Char(default_model='product.template')
    flsp_part_init = fields.Char(string="First Digit Part #")

    #default_seats = fields.Integer(default_model='openacademy.session')
    #my_setting = fields.Char(string='My Setting')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            flsp_part_init=self.env['ir.config_parameter'].sudo().get_param('product_template.flsp_part_init')
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('product_template.flsp_part_init', self.flsp_part_init)
