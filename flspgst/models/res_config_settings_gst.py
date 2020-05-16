from odoo import api, fields, models, modules


class ResConfigSettingsgst(models.TransientModel):
    _inherit = 'res.config.settings'

    flsp_gst_number = fields.Char(related='company_id.flsp_gst_number', readonly=False)


    def get_values(self):
        res = super(ResConfigSettingsgst, self).get_values()
        res.update(
            flsp_gst_number=self.env['ir.config_parameter'].sudo().get_param('flsp_gst_number')
        )
        return res

    def set_values(self):
        super(ResConfigSettingsgst, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('flsp_gst_number', self.flsp_gst_number)
