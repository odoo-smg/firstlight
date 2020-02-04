# -*- coding: utf-8 -*-

from odoo import fields, api, models, exceptions

class myproduceline(models.TransientModel):
    _inherit = 'mrp.product.produce.line'
    _check_company_auto = True

    #lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', domain=lambda self: self._get_lot_domain(), check_company=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', check_company=True)

    @api.onchange('lot_id')
    def _lot_id_onchange(self):
        lot_locations = self.env['stock.location'].search([('usage', '=', 'internal'), ('active', '=', True)]).ids
        stock_id = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),('quantity', '>', 0),('location_id', '=', lot_locations)]).mapped("lot_id").ids

        if self.lot_id.id in stock_id:
            return {
                'domain': {
                    'lot_id': [('id', 'in', stock_id)]
                },
            }
        else:
            return {
                'warning': {
                    'title': "Zero quantity",
                    'message': "The Lot/Serial Number select has not stock available. Please select a valid Lot/Serial Number",
                },
                'domain': {
                    'lot_id': [('id', 'in', stock_id)]
                },
            }

    @api.constrains('lot_id')
    def _check_stock_availability(self):
        valid = True
        for record in self:
            lot_locations = self.env['stock.location'].search([('usage', '=', 'internal'), ('active', '=', True)]).ids
            stock_id = self.env['stock.quant'].search([('product_id', '=', record.product_id.id), ('quantity', '>', 0),
                                                       ('location_id', '=', lot_locations)]).mapped("lot_id").ids
            if record.lot_id.id
                if not record.lot_id.id in stock_id:
                    raise exceptions.ValidationError("The following Lot does not has quantity available in stock: %s" % record.lot_id.id)

    @api.model
    def _get_lot_domain(self):
        lot_locations = self.env['stock.location'].search([('usage', '=', 'internal'), ('active', '=', True)]).ids
        stock_id = self.env['stock.quant'].search([('product_id', '=', 39),('quantity', '>', 0),('location_id', '=', lot_locations)]).mapped("lot_id").ids
        return [('id', 'in', stock_id)]
