from odoo import api, fields, models, modules


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    flsp_sales_discount_approval = fields.Boolean(string="Sales Order Approval")
    so_flsp_max_percent_approval = fields.Float(related='company_id.so_flsp_max_percent_approval', string="Max Discount Allowed", readonly=False)
    flsp_gst_reg_no = fields.Char(related="company_id.flsp_gst_reg_no", readonly=False)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            flsp_sales_discount_approval=self.env['ir.config_parameter'].sudo().get_param('flsp_sales_discount_approval')
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('flsp_sales_discount_approval', self.flsp_sales_discount_approval)
