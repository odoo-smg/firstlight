from odoo import models, fields, api


class Flspstockquantpack(models.Model):
    _inherit = 'stock.quant.package'
    _check_company_auto = True

    stock_picking_id = fields.Many2one('stock.picking', string='Delivery', compute='_stock_picking_compute')
    flsp_sid = fields.Char('SID')
    flsp_stc = fields.Char('Ship to Code')

    def _stock_picking_compute(self):
        sml_id = self.env['stock.move.line'].search([('result_package_id', '=', self.id)], limit=1)
        self.stock_picking_id = sml_id.picking_id.id
