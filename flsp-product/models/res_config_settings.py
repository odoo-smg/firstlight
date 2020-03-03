
from odoo import api, fields, models, modules

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    flsp_part_init = fields.Char(string="First Par", realted='company_id.flsp_part_num_init')

    #my_custom_field1_id = fields.Many2one('res.partner', string='For Customer')
    #my_custom_field2_id = fields.Many2one('res.partner', string='For Supplier')

#    @api.model
#    def get_values(self):
#        res = super(ResConfigSettings, self).get_values()
#        res.update(
#            flsp_part_init = self.env['ir.config_parameter'].sudo().get_param('flsp-product.flsp_part_init'),
#        )
#        return res
#
#    @api.multi
#    def set_values(self):
#        super(ResConfigSettings, self).set_values()
#        param = self.env['ir.config_parameter'].sudo()
#
#        field1 = self.flsp_part_init and self.flsp_part_init.id or False
#
#        param.set_param('flsp-product.flsp_part_init', field1)
