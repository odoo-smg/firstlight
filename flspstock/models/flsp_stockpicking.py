from odoo import fields, models, api


class flspstockpicking2(models.Model):
    _inherit = 'stock.picking'
    _check_company_auto = True

    flsp_packingdesc = fields.Text(string="Packing Description")
