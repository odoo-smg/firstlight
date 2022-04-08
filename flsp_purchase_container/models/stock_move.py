from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'
    _check_company_auto = True

    flsp_container_id = fields.Many2one('flsp.purchase.container', 'Container', compute='_flsp_calc_container')
    flsp_purchase_id = fields.Many2one('purchase.order', 'PO', compute='_flsp_calc_purchase_order')

    def _flsp_calc_purchase_order(self):
        for move in self:
            move.flsp_purchase_id = move.purchase_line_id.order_id.id

    def _flsp_calc_container(self):
        for move in self:
            if move.picking_id:
                picking = move.picking_id
                if picking.flsp_purchase_id:
                    receipts = self.env['flsp.purchase.container.line'].search([('picking_id', '=', picking.id)])
                    if receipts:
                        for each in receipts:
                            move.flsp_container_id = each.container_id
                    else:
                        move.flsp_container_id = False
                else:
                    move.flsp_container_id = False
            else:
                move.flsp_container_id
