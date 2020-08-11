from odoo import fields, models, api


class flspstockpackaging(models.Model):
    _inherit = 'product.packaging'
    _check_company_auto = True

    flsp_package_set_qty = fields.Integer(string="Quantity of Boxes")
