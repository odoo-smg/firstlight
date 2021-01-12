# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        self.ensure_one()
        self.action_assign()
        res = super(MrpProduction, self).button_mark_done()
        self.backflush_flsp()
        return res

    def backflush_flsp(self):
        wip_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA/WIP')])
        stock_virtual_location = self.env['stock.location'].search([('complete_name', '=', 'Virtual Locations/My Company: Inventory adjustment')])
        virtual_production_location = self.env['stock.location'].search([('complete_name', '=', 'Virtual Locations/My Company: Production')])
        stock_picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'INT')])
        if not stock_picking_type:
            raise UserError('Picking type Internal is missing')
        if not stock_virtual_location:
            raise UserError('Stock Virtual Location is missing')
        if not virtual_production_location:
            raise UserError('Stock Virtual Production is missing')
        if not wip_location:
            raise UserError('WIP Stock Location is missing')

        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')]).parent_path
        if not pa_location:
            raise UserError('WIP Stock Location is missing')
        pa_wip_locations = self.env['stock.location'].search([('parent_path', 'like', pa_location+'%')]).ids
        if not pa_wip_locations:
            raise UserError('WIP Stock Location is missing')

        ## Verifing the quantity of any production sub part if negative make it zero:
        ## (The sub parts will not be transferred to WIP).
        for components in self.move_raw_ids:
            for line in components.move_line_ids:
                pa_stock_tmp = self.env['stock.quant'].search(['&', ('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id)])
                pa_stock_quantity = 0
                for serial_location in pa_stock_tmp:
                    pa_stock_quantity += serial_location.quantity

                if pa_stock_quantity < 0 and line.product_id.bom_count > 0:
                    create_val = {
                        'origin': 'FLSP-AUTO-PA-ADJUST',
                        'picking_type_id': stock_picking_type.id,
                        'location_id': stock_virtual_location.id,
                        'location_dest_id': line.location_id.id,
                        'state': 'done',
                    }
                    stock_picking = self.env['stock.picking'].create(create_val)
                    stock_move = self.env['stock.move'].create({
                        'name': line.product_id.name,
                        'product_id': line.product_id.id,
                        'product_uom': line.product_id.uom_id.id,
                        'product_uom_qty': line.qty_done,
                        'picking_id': stock_picking.id,
                        'location_id': stock_virtual_location.id,
                        'location_dest_id': line.location_id.id
                    })
                    move_line = self.env['stock.move.line'].create({
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_id.uom_id.id,
                        'qty_done': line.qty_done,
                        'lot_id': line.lot_id.id,
                        'picking_id': stock_picking.id,
                        'move_id' : stock_move.id,
                        'location_id': stock_virtual_location.id,
                        'location_dest_id': line.location_id.id,
                        'state': 'done',
                        'done_move': True,
                    })
                    stock_picking.button_validate()
                    #stock_picking.state = 'done'

        ## Verifing quantities of components in PA/WIP if available move the quantity needed on MO to virtual production:
        bom_components = self._get_flattened_totals(self.bom_id, self.product_qty)
        stock_picking = False
        for prod in bom_components:
            if bom_components[prod]['level'] == 1:
                continue
            if prod.type in ['service', 'consu']:
                continue
            if bom_components[prod]['total'] <= 0:
                continue

            if not stock_picking:
                create_val = {
                    'origin': 'FLSP-Backflush',
                    'picking_type_id': stock_picking_type.id,
                    'location_id': wip_location.id,
                    'location_dest_id': virtual_production_location.id,
                    'state': 'done',
                }
                stock_picking = self.env['stock.picking'].create(create_val)
            tracking = False
            wip_lot = {}
            if prod.tracking != 'none':
                tracking = prod.tracking
                ## Need to check if the quantity is available in WIP, if it is not do not transfer.
                stock_wip = self.env['stock.quant'].search(['&', ('product_id', '=', prod.id), ('location_id', 'in', pa_wip_locations)])
                qty_needed = bom_components[prod]['total']
                for lot in stock_wip:
                    if lot.quantity > 0:
                        if lot.quantity - qty_needed >= 0:
                            wip_lot[lot.lot_id] = {'qty': qty_needed, 'location': lot.location_id}
                            break
                        else:
                            wip_lot[lot.lot_id] = {'qty': lot.quantity, 'location': lot.location_id}
                            qty_needed -= lot.quantity

            stock_move = self.env['stock.move'].create({
                'name': prod.name,
                'product_id': prod.id,
                'product_uom': prod.uom_id.id,
                'product_uom_qty': bom_components[prod]['total'],
                'picking_id': stock_picking.id,
                'location_id': wip_location.id,
                'location_dest_id': virtual_production_location.id
            })
            if tracking:
                for lot in wip_lot:
                    move_line = self.env['stock.move.line'].create({
                        'product_id': prod.id,
                        'product_uom_id': prod.uom_id.id,
                        'qty_done': wip_lot[lot]['qty'],
                        'lot_id': lot.id,
                        'picking_id': stock_picking.id,
                        'move_id': stock_move.id,
                        'location_id': wip_lot[lot]['location'].id,
                        'location_dest_id': virtual_production_location.id,
                        'state': 'done',
                        'done_move': True,
                    })
            else:
                move_line = self.env['stock.move.line'].create({
                    'product_id': prod.id,
                    'product_uom_id': prod.uom_id.id,
                    'qty_done': bom_components[prod]['total'],
                    #'lot_id': line.lot_id.id,
                    'picking_id': stock_picking.id,
                    'move_id': stock_move.id,
                    'location_id': wip_location.id,
                    'location_dest_id': virtual_production_location.id,
                    'state': 'done',
                    'done_move': True,
                })
            stock_picking.button_validate()
            #stock_picking.state = 'done'


    def _get_flattened_totals(self, bom, factor=1, totals=None, level=None):
        """Calculate the **unitary** product requirements of flattened BOM.
        *Unit* means that the requirements are computed for one unit of the
        default UoM of the product.
        :returns: dict: keys are components and values are aggregated quantity
        in the product default UoM.
        """
        if level is None:
            level = 1
        if totals is None:
            totals = {}
        factor /= bom.product_uom_id._compute_quantity(
            bom.product_qty, bom.product_tmpl_id.uom_id
        )
        for line in bom.bom_line_ids:
            sub_bom = bom._bom_find(product=line.product_id)
            if sub_bom:
                new_factor = factor * line.product_uom_id._compute_quantity(
                    line.product_qty, line.product_id.uom_id
                )
                '''if totals.get(line.product_id):
                    totals[line.product_id]['total'] += (
                        factor
                        * line.product_uom_id._compute_quantity(
                            line.product_qty, line.product_id.uom_id, round=False
                        )
                    )
                else:
                    totals[line.product_id] = {'total':(
                        factor
                        * line.product_uom_id._compute_quantity(
                            line.product_qty, line.product_id.uom_id, round=False
                        )
                    ), 'level': level, 'bom': sub_bom.code}
                '''
                level += 1
                self._get_flattened_totals(sub_bom, new_factor, totals, level)
                level -= 1
            else:
                if totals.get(line.product_id):
                    totals[line.product_id]['total'] += (
                            factor
                            * line.product_uom_id._compute_quantity(
                        line.product_qty, line.product_id.uom_id
                    )
                    )
                else:
                    totals[line.product_id] = {'total': (
                            factor
                            * line.product_uom_id._compute_quantity(
                        line.product_qty, line.product_id.uom_id
                    )
                    ), 'level': level, 'bom': ''}
        return totals
