from odoo import api, fields, models, modules


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    flsp_sales_discount_approval = fields.Boolean(string="Sales Order Approval")
    so_flsp_max_percent_approval = fields.Float(related='company_id.so_flsp_max_percent_approval', string="Max Discount Allowed", readonly=False)

    # School PPE Purchase Program
    flsp_sppepp = fields.Boolean(string="School PPE Purchase Program")
    flspsppepp_category_id = fields.Many2one('product.category', related='company_id.flspsppepp_category_id', readonly=False)
    flsp_percent_sppepp = fields.Float(related='company_id.flsp_percent_sppepp', string="Percent of Deposit", readonly=False)
    flspsppepp_product_id = fields.Many2one('product.product', related='company_id.flspsppepp_product_id', readonly=False)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            flsp_sales_discount_approval=self.env['ir.config_parameter'].sudo().get_param('flsp_sales_discount_approval'),
            flsp_sppepp=self.env['ir.config_parameter'].sudo().get_param('flsp_sppepp'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('flsp_sales_discount_approval', self.flsp_sales_discount_approval)
        self.env['ir.config_parameter'].sudo().set_param('flsp_sppepp', self.flsp_sppepp)
