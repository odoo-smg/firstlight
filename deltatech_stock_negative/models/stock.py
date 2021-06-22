# ©  2015-2019 Deltatech
# See README.rst file on addons root folder for license details


from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _update_available_quantity(
        self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, in_date=None
    ):
        allow_negaive = False
        #if 'flsp_backflush' in self.env['product.template']._fields:
            #allow_negaive = product_id.flsp_backflush and product_id.bom_count > 0
        
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # product_id.qty_available is not a correct qty for product because there may be moves in other locations
        # product_quantity = product_id.qty_available
        product_quantity = self.get_flsp_stock_quantity(product_id, location_id, lot_id=lot_id, package_id=package_id)

        if (
            not location_id.allow_negative_stock
            and not allow_negaive
            and location_id.usage == "internal"
            and float_compare(product_quantity + quantity, 0, precision_digits=precision_digits) < 0
        ):
            if location_id.company_id.no_negative_stock:
                raise UserError(
                    _( """You have chosen to avoid negative stock. 
%s pieces of %s are remaining in location %s, but you want to transfer %s pieces. 
Please adjust your quantities or correct your stock with an inventory adjustment."""
                    )
                    % (product_quantity, "["+product_id.default_code+"] "+product_id.name, location_id.name, 0 - quantity)
                )

        return super(StockQuant, self)._update_available_quantity(
            product_id, location_id, quantity, lot_id, package_id, owner_id, in_date
        )
        
    def get_flsp_stock_quantity(self, product_id, location_id, lot_id=None, package_id=None):
        stock_quants = False
        if lot_id and package_id:
            stock_quants = self.env['stock.quant'].search(['&', '&', '&', ('product_id', '=', product_id.id), ('location_id', '=', location_id.id), ('lot_id', '=', lot_id.id), ('package_id', '=', package_id.id)]).mapped('quantity')
        elif lot_id:
            stock_quants = self.env['stock.quant'].search(['&', '&', ('product_id', '=', product_id.id), ('location_id', '=', location_id.id), ('lot_id', '=', lot_id.id)]).mapped('quantity')
        elif package_id:
            stock_quants = self.env['stock.quant'].search(['&', '&', ('product_id', '=', product_id.id), ('location_id', '=', location_id.id), ('package_id', '=', package_id.id)]).mapped('quantity')
        else:
            stock_quants = self.env['stock.quant'].search(['&', ('product_id', '=', product_id.id), ('location_id', '=', location_id.id)]).mapped('quantity')

        product_quantity = 0
        if stock_quants:
            # if there is record found, returned '[number]', set qty with number, even when it is 0.0 sometimes
            for sq in stock_quants:
                product_quantity += sq
        else:
            # if there is no record found, returned '[]', set qty with 0
            product_quantity = 0

        return product_quantity

