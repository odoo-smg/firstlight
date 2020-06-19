from odoo import models, fields, api


class Customerscode(models.Model):
    _name = 'flspstock.customerscode'
    _description = "Customer Part Number"
    _check_company_auto = True

    sequence = fields.Integer('Sequence', default=1, help="The first in the sequence is the default one.")
    product_id = fields.Many2one('product.product', string='Product', check_company=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    part_number = fields.Char(string="Part Number", required=True)
    description = fields.Char(string="Description", required=True)
    company_id = fields.Many2one('res.company', 'Company', index=True)
