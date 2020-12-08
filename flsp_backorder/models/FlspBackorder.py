# -*- coding: utf-8 -*-
from odoo import models, _

class FlspBackorder(models.Model):
    """
        Classname:  FlspBackorder
        Purpose:    To write backorder status to done
        Note:       All the code below is inherited from the stock picking
        Date:       Dec/7th/2020/Monday
        Author:     Sami Byaruhanga
    """
    _inherit = "stock.picking"
    def _create_backorder(self):
        """ This method is called when the user chose to create a backorder. It will create a new
        picking, the backorder, and move the stock.moves that are not `done` or `cancel` into it.
        """
        backorders = self.env['stock.picking']
        for picking in self:
            moves_to_backorder = picking.move_lines.filtered(lambda x: x.state not in ('done', 'cancel'))
            if moves_to_backorder:
                backorder_picking = picking.copy({
                    'name': '/',
                    'move_lines': [],
                    'move_line_ids': [],
                    'backorder_id': picking.id
                })
                picking.message_post(
                    body=_('The backorder <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
                        backorder_picking.id, backorder_picking.name))
                moves_to_backorder.write({'picking_id': backorder_picking.id})
                moves_to_backorder.mapped('package_level_id').write({'picking_id':backorder_picking.id})
                moves_to_backorder.mapped('move_line_ids').write({'picking_id': backorder_picking.id})
                self.write({'state': 'done'})
                backorder_picking.action_assign()
                backorders |= backorder_picking
        return backorders
