# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class FlspStockProductionLotFilterSn(models.Model):
    """
        class_name: FlspStockProductionLotFilterSn
        inherit:    stock.production.lot
        Purpose:    To add a check box on stock_production_lot when the qty is greater than 1
        Date:       Mar/29th/2021/M
        Author:     Sami Byaruhanga
    """
    _inherit = 'stock.production.lot'

    qty_on_table = fields.Boolean(string='Quantity exist', compute='qty_available', store=True,
                                  help="Very useful since it will help show which quantities are available")
    qty_location = fields.Many2one('stock.location', string='Quantity_location', compute='qty_available', store=True)

    @api.depends('product_qty')
    def qty_available(self):
        """
            Purpose:    To make qty on table true if there is qty available on lot
            Update on:  Apr.8th.2021.R
            Tkt #:      344
        """
        for record in self:
            if record.product_qty > 0:
                record.qty_on_table = True

        stock = self.env['stock.quant'].search([('quantity', '>', 0), ('lot_id', '=', self.ids)])
        for line in stock:
            for record in self:
                if line.lot_id.name == record.name:
                    record.qty_location = line.location_id


class FlspSockQuantFilterSn(models.Model):
    """
        class_name: FlspSockQuantFilterSn
        inherit:    stock.quant
        Purpose:    To change the stock.production.lot field qty_on_table depending on qty on hand
        Date:       Mar/29th/2021/M
        Author:     Sami Byaruhanga
    """
    _inherit = 'stock.quant'

    @api.onchange('inventory_quantity', 'location_id')
    def change_product_qty_in_lot_table(self):
        """
            Purpose: To change the qty_on_table for stock.production.lot
        """
        if self.inventory_quantity > 0:# and ('PA' in self.location_id.complete_name):
            self.lot_id.qty_on_table = True
            self.lot_id.qty_location = self.location_id
        else:
            self.lot_id.qty_on_table = False


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
            Purpose: To write the stock.production.lot location and qty on table
        """
        if self.prod_lot_id:
            self.prod_lot_id.qty_location = self.location_id
            if self.product_qty > 0:
                self.prod_lot_id.qty_on_table = True
            else:
                self.prod_lot_id.qty_on_table = False


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
            Purpose: To write the stock.production.lot location and qty on table
        """
        for line in self.move_line_ids:
            if line.lot_id:
                line.lot_id.qty_location = self.location_dest_id
                if self.location_dest_id:
                    line.lot_id.qty_on_table = True
                else:
                    line.lot_id.qty_on_table = False


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
        Purpose:    To change the stock.production.lot field qty_on_table to false when consumed in MO
        Date:       Mar/29th/2021/M
        Author:     Sami Byaruhanga
    """
    _inherit = 'mrp.production'

    def change_product_qty_in_lot_table(self):
        """
            Purpose: To write the stock.production.lot to false so its filtered in next MO domain
        """
        stock_move_line = self.env['stock.move.line'].search([('reference', '=', self.name)])
        for line in stock_move_line:
            if line.lot_id:
                line.lot_id.qty_on_table = False

    def post_inventory(self):
        """
            Purpose:    To post inventory
            NOTE:       This is inherited from mrp.production
        """
        for order in self:
            # In case the routing allows multiple WO running at the same time, it is possible that
            # the quantity produced in one of the workorders is lower than the quantity produced in
            # the MO.
            if order.product_id.tracking != "none" and any(
                wo.state not in ["done", "cancel"]
                and float_compare(wo.qty_produced, order.qty_produced, precision_rounding=order.product_uom_id.rounding) == -1
                for wo in order.workorder_ids
            ):
                raise UserError(
                    _(
                        "At least one work order has a quantity produced lower than the quantity produced in the manufacturing order. "
                        + "You must complete the work orders before posting the inventory."
                    )
                )

            moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):
                move.product_uom_qty = move.quantity_done
            # MRP do not merge move, catch the result of _action_done in order
            # to get extra moves.
            moves_to_do = moves_to_do._action_done()
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do
            order._cal_price(moves_to_do)
            moves_to_finish = order.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            moves_to_finish = moves_to_finish._action_done()
            order.workorder_ids.mapped('raw_workorder_line_ids').unlink()
            order.workorder_ids.mapped('finished_workorder_line_ids').unlink()
            order.action_assign()
            consume_move_lines = moves_to_do.mapped('move_line_ids')
            for moveline in moves_to_finish.mapped('move_line_ids'):
                if moveline.move_id.has_tracking != 'none' and moveline.product_id == order.product_id or moveline.lot_id in consume_move_lines.mapped('lot_produced_ids'):
                    if any([not ml.lot_produced_ids for ml in consume_move_lines]):
                        raise UserError(_('You can not consume without telling for which lot you consumed it'))
                    # Link all movelines in the consumed with same lot_produced_ids false or the correct lot_produced_ids
                    filtered_lines = consume_move_lines.filtered(lambda ml: moveline.lot_id in ml.lot_produced_ids)
                    moveline.write({'consume_line_ids': [(6, 0, [x for x in filtered_lines.ids])]})
                else:
                    # Link with everything
                    moveline.write({'consume_line_ids': [(6, 0, [x for x in consume_move_lines.ids])]})

        self.change_product_qty_in_lot_table() #calling method to change qty

        return True


class FlspMrpAbstractFilterSn(models.AbstractModel):
    """
        class_name: FlspMrpFilterSn
        inherit:    mrp.abstract.workorder.line
        Purpose:    To inherit the abstract model and add domain filter on lot_id
        Date:       Mar/26th/2021/F
        Author:     Sami Byaruhanga
    """
    _inherit = "mrp.abstract.workorder.line"
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number', check_company=True,
        domain="[('product_id', '=', product_id), ('qty_on_table','=',True), ('qty_location.complete_name', 'ilike', 'WH/PA'), '|', ('company_id', '=', False), ('company_id', '=', parent.company_id)]")


class FlspStockMoveLineFilterSn(models.Model):
    """
        class_name: FlspMrpFilterSn
        inherit:    stock.move.line
        Purpose:    To show only Serial numbers that are available
        Date:       Apr/8th/2021/R
        Author:     Sami Byaruhanga
    """
    _inherit = 'stock.move.line'

    # Inherited and added the qty_on_table = True in domain
    # Ticket#341
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id), "
               "('qty_on_table','=',True),('qty_location','=',location_id)]", check_company=True)