from odoo import models, fields, api


class SaleTargetCategory(models.Model):
    _name = 'flsp.sale.target.category'
    _description = "Category Sales Target"
    _check_company_auto = True

    category_id = fields.Many2one('product.category', string='Category', readonly=True)
    year = fields.Char(string="Year", required=True)
    month01 = fields.Float(string="January")
    month02 = fields.Float(string="February")
    month03 = fields.Float(string="March")
    month04 = fields.Float(string="April")
    month05 = fields.Float(string="May")
    month06 = fields.Float(string="June")
    month07 = fields.Float(string="July")
    month08 = fields.Float(string="August")
    month09 = fields.Float(string="September")
    month10 = fields.Float(string="October")
    month11 = fields.Float(string="November")
    month12 = fields.Float(string="December")
