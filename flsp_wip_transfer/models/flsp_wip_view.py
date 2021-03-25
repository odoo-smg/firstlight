# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api
from datetime import datetime
from odoo.exceptions import UserError


class Flspwipview(models.Model):
    _name = 'flsp.wip.view'
    _auto = False
    _description = 'WIP Transfer'

    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product template', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    stock_qty = fields.Float(string='WH/Stock', readonly=True)
    pa_wip_qty = fields.Float(string='PA/WIP', readonly=True)
    source = fields.Char("MO", readonly=True)
    mfg_demand = fields.Float(string='Qty', readonly=True)
    suggested = fields.Float(string='Suggested', readonly=True)
    uom = fields.Many2one('uom.uom', 'Product Unit of Measure', readonly=True)
    adjusted = fields.Float(string='Adjusted')
    state = fields.Selection([
        ('transfer', 'to transfer'),
        ('negative', 'to adjust'),
        ('short', 'not available'),
        ('done', 'done'),
    ], string='State', readonly=True)
    stock_picking = fields.Many2one('stock.picking', string='Stock Picking', readonly=False)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', readonly=False)
    qty_items = fields.Integer('Items')

    purchase_uom = fields.Many2one('uom.uom', 'Purchase Unit of Measure', readonly=True)
    purchase_stock_qty = fields.Float(string='WH/Stock 2nd uom', readonly=True)
    purchase_pa_wip_qty = fields.Float(string='PA/WIP 2nd uom', readonly=True)
    purchase_mfg_demand = fields.Float(string='Qty 2nd uom', readonly=True)
    purchase_adjusted = fields.Float(string='Adjusted 2nd uom')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'flsp_wip_view')

        query = """
        CREATE or REPLACE VIEW flsp_wip_view AS (
        SELECT
        max(id) as id,
        max(description) as description,
        max(default_code) as default_code,
        max(product_tmpl_id) as product_tmpl_id,
        product_id,
        max(stock_qty) as stock_qty,
        max(pa_wip_qty) as pa_wip_qty,
        max(source) as source,
        sum(mfg_demand) as mfg_demand,
        sum(suggested) as suggested,
        max(uom) as uom,
        sum(adjusted) as adjusted,
        max(state) as state,
        max(stock_picking) as stock_picking,
        max(production_id) as production_id,
        count(id) as qty_items,
        max(purchase_uom) as purchase_uom,
        max(purchase_stock_qty) as purchase_stock_qty,
        max(purchase_pa_wip_qty) as purchase_pa_wip_qty,
        sum(purchase_mfg_demand) as purchase_mfg_demand,
        sum(purchase_adjusted) as purchase_adjusted
        FROM flsp_wip_transfer
        where state != 'done'
        group by product_id
        );
        """
        self.env.cr.execute(query)

    def name_get(self):
        return [(record.id, record.product_id.name) for record in self]

    def execute_suggestion(self):
        move_lines = []
        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')])
        wip_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA/WIP')])
        stock_location = self.env['stock.location'].search([('complete_name', '=', 'WH/Stock')])
        stock_picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'INT')])
        stock_virtual_location = self.env['stock.location'].search([('complete_name', '=', 'Virtual Locations/My Company: Inventory adjustment')])
        stock_virtual_production = self.env['stock.location'].search([('complete_name', '=', 'Virtual Locations/My Company: Production')])
        stock_picking = False
        if not stock_picking_type:
            raise UserError('Picking type Internal is missing')
        if not wip_location:
            raise UserError('WIP Stock Location is missing')
        if not stock_location:
            raise UserError('Stock Location is missing')
        if not stock_virtual_location:
            raise UserError('Stock Virtual Location is missing')
        if not stock_virtual_production:
            raise UserError('Virtual Production Location is missing')
        count_products = 0
        negative_adjust = False
        for product in self:
            if product.state == 'negative':
                negative_adjust = True
            count_products += 1

        product_done = {}
        if negative_adjust and count_products > 0:
            # Adjust negative quantities In PA and PA/WIP
            create_val = {
                'origin': ' WIP-NEGATIVE-ADJUST',
                'picking_type_id': stock_picking_type.id,
                'location_id': stock_virtual_location.id,
                'location_dest_id': pa_location.id,
                'state': 'assigned',
            }
            stock_picking = self.env['stock.picking'].create(create_val)
            for product in self:
                wip_transfer = self.env['flsp.wip.transfer'].search(['&', ('product_id', '=', product.product_id.id),('state', '=', 'negative')])
                for wip in wip_transfer:
                    # check if the serial number is available in Stock, if so transfer from there.
                    from_location_id = stock_virtual_location.id
                    if wip.product_id.tracking == 'serial' and wip.product_id.bom_count > 0:
                        stock_quant = self.env['stock.quant'].search(['&', '&', ('product_id', '=', wip.product_id.id), ('location_id', '=', stock_location.id), ('lot_id', '=', wip.negative_lot_id.id)])
                        if stock_quant:
                            if stock_quant.quantity > 0:
                                from_location_id = stock_location.id
                                wip.state = "done"
                                wip.stock_picking = stock_picking.id
                                #wip.stock_move_id = move_line.id
                                if wip.product_id.id in product_done:
                                    product_done[wip.product_id.id]['total'] += 1
                                else:
                                    product_done[wip.product_id.id] = {'total': 1}

                    stock_move = self.env['stock.move'].create({
                        'name': wip.product_id.name,
                        'product_id': wip.product_id.id,
                        'product_uom': wip.product_id.uom_id.id,
                        'product_uom_qty': wip.adjusted,
                        'picking_id': stock_picking.id,
                        'location_id': from_location_id,
                        'location_dest_id': wip.negative_location_id.id,
                        'state': 'assigned',
                    })
                    move_line = self.env['stock.move.line'].create({
                        'product_id': wip.product_id.id,
                        'product_uom_id': wip.product_id.uom_id.id,
                        'qty_done': wip.adjusted,
                        'lot_id': wip.negative_lot_id.id,
                        'picking_id': stock_picking.id,
                        'move_id': stock_move.id,
                        'location_id': from_location_id,
                        'location_dest_id': wip.negative_location_id.id,
                        'state': 'assigned',
                        'done_move': True,
                    })

        if negative_adjust and count_products > 0 and stock_picking:
            stock_picking.button_validate()
        if count_products > 0:
            if negative_adjust:
                create_val = {
                    'origin': 'FLSP-WIP-TRANSFER',
                    'picking_type_id': stock_picking_type.id,
                    'location_id': stock_location.id,
                    'location_dest_id': stock_virtual_production.id,
                }
            else:
                create_val = {
                    'origin': 'FLSP-WIP-TRANSFER',
                    'picking_type_id': stock_picking_type.id,
                    'location_id': stock_location.id,
                    'location_dest_id': wip_location.id,
                }
            stock_picking = self.env['stock.picking'].create(create_val)

            for product in self:

                quantity_transfer = product.adjusted
                if product.product_id.id in product_done:
                    quantity_transfer -= product_done[product.product_id.id]['total']

                if quantity_transfer <= 0:
                    if count_products <= 1:
                        stock_picking = False
                    else:
                        count_products -= 1
                    if not negative_adjust:
                        # Ticket #308 - To clean suggestion when it was adjusted to zero.
                        wip_transfer = self.env['flsp.wip.transfer'].search(
                            ['&', ('product_id', '=', product.product_id.id), ('state', '!=', 'done')])
                        for wip_line in wip_transfer:
                            wip_line.state = "done"
                    continue
                if negative_adjust:
                    move_line = self.env['stock.move'].create({
                        'name': "[wip-transfer]"+product.product_id.name,
                        'product_id': product.product_id.id,
                        'product_uom': product.product_id.uom_id.id,
                        'product_uom_qty': quantity_transfer,
                        #'product_qty': product.adjusted,
                        'picking_id': stock_picking.id,
                        'location_id': stock_location.id,
                        'location_dest_id': stock_virtual_production.id
                    })
                else:
                    move_line = self.env['stock.move'].create({
                        'name': "[wip-transfer]"+product.product_id.name,
                        'product_id': product.product_id.id,
                        'product_uom': product.product_id.uom_id.id,
                        'product_uom_qty': quantity_transfer,
                        #'product_qty': product.adjusted,
                        'picking_id': stock_picking.id,
                        'location_id': stock_location.id,
                        'location_dest_id': wip_location.id
                    })
                wip_transfer = self.env['flsp.wip.transfer'].search(['&',('product_id', '=', product.product_id.id), ('state', '!=', 'done')])
                for wip_line in wip_transfer:
                    wip_line.state = "done"
                    wip_line.stock_picking = stock_picking.id
                    wip_line.stock_move_id = move_line.id
        if stock_picking:
            stock_picking.action_confirm()
            stock_picking.action_assign()
            self.env['flspautoemails.bpmemails'].send_email(stock_picking, 'WIP001')

        return

    def action_open_wip_transfer(self):
        self.ensure_one()
        action = self.env.ref('flsp_wip_transfer.flsp_wip_transfer_action').read()[0]
        action['domain'] = ['&', ('product_id', '=', self.product_id.id), ('state', '!=', 'done')]
        #action['domain'] = [('product_id', '=', self.product_id.id)]
        return action
