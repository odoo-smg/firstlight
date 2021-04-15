# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class FlspStockProductionLotFilterSn(models.Model):
    """
        class_name: FlspStockProductionLotFilterSn
        inherit:    stock.production.lot
        Purpose:    To add a check box on stock_production_lot when the qty is greater than 1
        Date:       Mar/29th/2021/M
        Author:     Sami Byaruhanga
    """
    _inherit = 'stock.production.lot'

    qty_location = fields.Many2many('stock.location', string='Quantity_location', compute='check_all_available_sn', store=True)

    def clear_all_previous_sn_locations(self):
        """
            Purpose:    To clear all the previous sn/lot locations info
        """
        sn = self.env['stock.production.lot'].search([])
        for record in sn:
            if record.qty_location:
                record.qty_location = [(5, 0, 0)]


    @api.depends('product_qty')
    def check_all_available_sn(self):
        """
            Purpose:    To check stock_quant for all lots/sn with qty >0
                        Writes the stock_qty location on the serial numbers
            NOTE:       CAN RUN THIS EVERY FRIDAY NIGHT so that the locations are recomputed
        """
        self.clear_all_previous_sn_locations()
        stock = self.env['stock.quant'].search([('quantity', '>', 0)])
        sn = self.env['stock.production.lot'].search([])
        for line in stock:
            for record in sn:
                if line.lot_id == record:
                    record.qty_location = [(4, line.location_id.id)] # adds location on serial number



class FlspSockQuantFilterSn(models.Model):
    """
        class_name: FlspSockQuantFilterSn
        inherit:    stock.quant
        Purpose:    To change the stock.production.lot field qty_location depending on qty on hand
        Date:       Mar/29th/2021/M
        Author:     Sami Byaruhanga
    """
    _inherit = 'stock.quant'

    @api.onchange('inventory_quantity', 'location_id')
    def change_product_qty_in_lot_table(self):
        """
            Purpose: To change the qty_location for stock.production.lot
        """

        if self.product_id.product_tmpl_id.tracking == 'lot':
            if self.inventory_quantity > 0:
                self.lot_id.qty_location = [(4, self.location_id.id)] #add to existing location
            else:
                self.lot_id.qty_location = [(3, self.location_id.id)]  # Removes that ID for lots


        elif self.product_id.product_tmpl_id.tracking == 'serial':
            if self.inventory_quantity > 0:
                self.lot_id.qty_location = self.location_id
            else:
                self.lot_id.qty_location = [(5, 0, 0)]  # Removes that ID for lots


class FlspInvAdjLineFilterSn(models.Model):
    """
        class_name: FlspInvAdjLineFilterSn
        inherit:    stock.inventory.line
        Purpose:    To change the stock.production.lot field qty_location depending on inventory adjustment
        Date:       Mar/30th/2021/T
        Author:     Sami Byaruhanga
    """
    _inherit = 'stock.inventory.line'

    @api.onchange('location_id', 'prod_lot_id', 'product_qty')
    def change_product_qty_in_lot_table(self):
        """
            Purpose: To write the qty_location on stock.production.lot
        """
        if self.prod_lot_id:
            if self.product_qty > 0:
                self.prod_lot_id.qty_location = [(4, self.location_id.id)]  # add to existing location
            else:
                self.prod_lot_id.qty_location = [(3, self.location_id.id)]  # Removes that ID for lots



class FlspStockPickingFilterSn(models.Model):
    """
        class_name: FlspStockPickingFilterSn
        inherit:    stock.picking
        Purpose:    To change the stock.production.lot field qty_location depending on transfer
        Date:       Mar/30th/2021/T
        Author:     Sami Byaruhanga
    """
    _inherit = 'stock.picking'

    def change_product_qty_in_lot_table(self):
        """
            Purpose: To write the qty_location on stock,production.lot table
        """
        for line in self.move_line_ids:
            if line.lot_id:
                stock = self.env['stock.quant'].search([('quantity', '>', 0), ('lot_id', '=', line.lot_id.id)])
                line.lot_id.qty_location = [(5, 0, 0)]  # clear that lot locations
                if len(stock.ids) > 0:
                    line.lot_id.qty_location = [(6, 0, stock.location_id.ids)]


    def button_validate(self):
        """
            Purpose:    To call method to change the stock.production table
            Note:       Used method because its short and called in button validate
        """
        res = super(FlspStockPickingFilterSn, self).button_validate()
        self.change_product_qty_in_lot_table()
        return res


class FlspMrpProductionFilterSn(models.Model):
    """
        class_name: FlspMrpProductionFilterSn
        inherit:    mrp.production
        Purpose:    To change the stock.production.lot field qty_location when consumed in MO
        Date:       Mar/29th/2021/M
        Author:     Sami Byaruhanga
    """
    _inherit = 'mrp.production'

    def change_product_qty_in_lot_table(self):
        """
            Purpose: To change the location name on the lot
            Note:   Did not call the method in lot coz, we had to filter the lots to those
                    Used only in the manufacturing order.
                    Did this to make the run time quicker
        """
        stock_move_line = self.env['stock.move.line'].search([('reference', '=', self.name)])
        for line in stock_move_line:
            if line.lot_id:
                stock = self.env['stock.quant'].search([('quantity', '>', 0), ('lot_id', '=', line.lot_id.id)])
                line.lot_id.qty_location = [(5, 0, 0)] # clear that lot locations
                if len(stock.ids) > 0:
                    line.lot_id.qty_location = [(6, 0, stock.location_id.ids)]


    def post_inventory(self):
        """
            Purpose:    To post inventory
            NOTE:       This is inherited from mrp.production and add own method to filter lots
        """
        res = super(FlspMrpProductionFilterSn, self).post_inventory()
        self.change_product_qty_in_lot_table() #calling method to change qty
        return res


class FlspMrpAbstractFilterSn(models.AbstractModel):
    """
        class_name: FlspMrpFilterSn
        inherit:    mrp.abstract.workorder.line
        Purpose:    To inherit the abstract model and add domain filter on lot_id
        Date:       Mar/26th/2021/F
        Author:     Sami Byaruhanga
    """
    _inherit = "mrp.abstract.workorder.line"
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', check_company=True,
        domain="[('product_id', '=', product_id), ('qty_location.complete_name', 'ilike', 'WH/PA'), '|', ('company_id', '=', False), ('company_id', '=', parent.company_id)]")


class FlspStockMoveLineFilterSn(models.Model):
    """
        class_name: FlspMrpFilterSn
        inherit:    stock.move.line
        Purpose:    To show only Serial numbers that are available on transfers,
        Date:       Apr/8th/2021/R
        Author:     Sami Byaruhanga
    """
    _inherit = 'stock.move.line'
    # Inherited and added the qty_location on the domain
    # Ticket#341
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id), "
               "('qty_location','=',location_id)]", check_company=True)
