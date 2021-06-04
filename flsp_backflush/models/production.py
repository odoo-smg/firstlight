# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    flsp_qty_backflushed = fields.Float(string="Qty Backflushed")

    def open_produce_product(self):
        self.ensure_one()
        self.action_assign()
        res = super(MrpProduction, self).open_produce_product()
        #if self.product_id.tracking in ['none', 'lot']:
            # needs the total quantity
        raw_moves = self.env['stock.move'].search([('raw_material_production_id', '=', self.id)])
        for move in raw_moves:
            if move.flsp_backflush:
                qtt_to_wip = move.product_uom_qty - move.reserved_availability
                if qtt_to_wip > 0:
                    self.create_wip_qty(move.product_id, qtt_to_wip)
                    self.action_assign()
#        else:
#            # needs only qty to produce 1
            #            raw_moves = self.env['stock.move'].search([('raw_material_production_id', '=', self.id)])
            #for move in raw_moves:
                    #                if move.flsp_backflush:
                    #qtt_to_wip = move.product_uom_qty - move.reserved_availability
                    #if qtt_to_wip > 0:
                        #                        self.create_wip_qty(move.product_id, 1)
                        #self.action_assign()
        return res

    def button_mark_done(self):
        self.ensure_one()
        self.action_assign()
        backflush_qty = self.product_qty - self.flsp_qty_backflushed
        self.new_backflush_flsp(backflush_qty)
        self.flsp_qty_backflushed = self.product_qty
        res = super(MrpProduction, self).button_mark_done()
        return res

    def post_inventory(self):
        self.ensure_one()
        self.action_assign()
        self.backflush_partials_flsp()
        res = super(MrpProduction, self).post_inventory()
        return res

    def backflush_partials_flsp(self):

        stock_move_done = self.env['stock.move'].search(
        ['&', '&', '&', ('product_id', '=', self.product_id.id),
                        ('production_id', '=', self.id),
                        ('is_done', '=', True),
                        ('scrapped', '=', False)])
        total_backflushable = 0
        for move in stock_move_done:
            total_backflushable += move.product_qty

        if self.flsp_qty_backflushed:
            total_to_backflush = total_backflushable - self.flsp_qty_backflushed
        else:
            total_to_backflush = total_backflushable

        self.new_backflush_flsp(total_to_backflush)
        if self.flsp_qty_backflushed:
            self.flsp_qty_backflushed += total_to_backflush
        else:
            self.flsp_qty_backflushed = total_to_backflush

    def new_backflush_flsp(self, backflush_qty=0):

        wip_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA/WIP')])
        stock_virtual_location = self.env['stock.location'].search([('complete_name', '=', 'Virtual Locations/My Company: Inventory adjustment')])
        virtual_production_location = self.env['stock.location'].search([('complete_name', '=', 'Virtual Locations/My Company: Production')])
        stock_picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'INT')])
        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')]).parent_path
        pa_wip_locations = self.env['stock.location'].search([('parent_path', 'like', pa_location+'%')]).ids
        if not stock_picking_type:
            raise UserError('Picking type Internal is missing')
        if not stock_virtual_location:
            raise UserError('Stock Virtual Location is missing')
        if not virtual_production_location:
            raise UserError('Stock Virtual Production is missing')
        if not wip_location:
            raise UserError('WIP Stock Location is missing')
        if not pa_location:
            raise UserError('WIP Stock Location is missing')
        if not pa_wip_locations:
            raise UserError('WIP Stock Location is missing')

        ## Check if backflush is already done
        if backflush_qty <= 0:
            backflush_qty = self.product_qty - self.flsp_qty_backflushed
        if backflush_qty <= 0:
            return

        ## Verifing quantities of components in PA/WIP if available move the quantity needed on MO to virtual production:
        bom_components = self._get_flattened_totals(self.bom_id, backflush_qty)
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
                    'origin': self.name + ' FLSP-Backflush',
                    'picking_type_id': stock_picking_type.id,
                    'location_id': wip_location.id,
                    'location_dest_id': virtual_production_location.id,
                    'state': 'assigned',
                }
                stock_picking = self.env['stock.picking'].create(create_val)
            tracking = False
            wip_lot = {}
            if prod.tracking != 'none':
                tracking = prod.tracking
                ## Need to check if the quantity is available in WIP, if it is not do not transfer.
                stock_wip = self.env['stock.quant'].search(['&', ('product_id', '=', prod.id), ('location_id', 'in', pa_wip_locations)])
                qty_needed = bom_components[prod]['total']
                pa_wip_qty = 0
                for stock_lin in stock_wip:
                    pa_wip_qty += stock_lin.quantity
                qty_needed = bom_components[prod]['total']
                if qty_needed > pa_wip_qty:
                    qtt = qty_needed - pa_wip_qty
                    self.create_wip_qty(prod, qtt)
                    stock_wip = self.env['stock.quant'].search(['&', ('product_id', '=', prod.id), ('location_id', 'in', pa_wip_locations)])

                for lot in stock_wip:
                    if lot.quantity > 0:
                        if lot.quantity - qty_needed >= 0:
                            wip_lot[lot.lot_id] = {'qty': qty_needed, 'location': lot.location_id}
                            qty_needed = 0
                            break
                        else:
                            wip_lot[lot.lot_id] = {'qty': lot.quantity, 'location': lot.location_id}
                            qty_needed -= lot.quantity
                # In case we don't have the total quantity available will create a lot 999999_000000
                if qty_needed > 0:
                    if prod.tracking == 'lot':
                        new_lot = self.create_lot(prod, 1)
                        if new_lot:
                            wip_lot[new_lot[0]] = {'qty': qty_needed, 'location': wip_location}
                    else:
                        new_lot = self.create_lot(prod, int(qty_needed))
                        for lot in new_lot:
                            wip_lot[lot] = {'qty': 1, 'location': wip_location}
            else:
                qty_needed = bom_components[prod]['total']
                pa_wip_qty = 0
                stock_wip = self.env['stock.quant'].search(['&', ('product_id', '=', prod.id), ('location_id', 'in', pa_wip_locations)])
                for stock_lin in stock_wip:
                    pa_wip_qty += stock_lin.quantity
                qty_needed = bom_components[prod]['total']

                if qty_needed > pa_wip_qty:
                    qtt = qty_needed - pa_wip_qty
                    self.create_wip_qty(prod, qtt)
                    stock_wip = self.env['stock.quant'].search(['&', ('product_id', '=', prod.id), ('location_id', 'in', pa_wip_locations)])

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
                        'state': 'assigned',
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
                    'state': 'assigned',
                    'done_move': True,
                })
        if stock_picking:
            stock_picking.button_validate()

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
            bom.product_qty, bom.product_tmpl_id.uom_id, round=False
        )
        for line in bom.bom_line_ids:
            sub_bom = bom._bom_find(product=line.product_id)
            if sub_bom:
                if not line.product_tmpl_id.flsp_backflush:
                    if totals.get(line.product_id):
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
                    continue
                else:
                    new_factor = factor * line.product_uom_id._compute_quantity(
                        line.product_qty, line.product_id.uom_id, round=False
                    )

                level += 1
                self._get_flattened_totals(sub_bom, new_factor, totals, level)
                level -= 1
            else:
                if totals.get(line.product_id):
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
                    ), 'level': level, 'bom': ''}
        return totals


    def create_lot(self, prod, qty):
        ret = []
        company_id = self.env.company.id
        self._cr.execute("select max(name) as code from stock_production_lot where name like '999999%' ")
        retvalue = self._cr.fetchall()
        returned_registre = retvalue[0]
        latest_lot = returned_registre[0]
        if latest_lot:
            next_lot = ('00000'+str(int(latest_lot[-5:])+1))[-5:]
        else:
            next_lot = '00001'
        for x in range(0,qty):
            lot = self.env['stock.production.lot'].create({
                'name': '999999_'+next_lot,
                'product_id': prod.id,
                'ref': 'Backflush Adjust',
                'company_id': company_id,
            })
            next_lot = ('00000' + str(int(next_lot[1:6]) + 1))[-5:]
            ret.append(lot)
        return ret

    def create_wip_qty(self, prod, qty):
        wip_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA/WIP')])
        stock_virtual_location = self.env['stock.location'].search([('complete_name', '=', 'Virtual Locations/My Company: Inventory adjustment')])
        stock_picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'INT')])
        if qty <= 0:
            return
        prod.flsp_bf_check = True
        if prod.tracking == 'none':
            create_val = {
                 'origin': self.name + ' FLSP-BF-ADJUST',
                 'picking_type_id': stock_picking_type.id,
                 'location_id': stock_virtual_location.id,
                 'location_dest_id': wip_location.id,
                 'state': 'assigned',}
            stock_picking = self.env['stock.picking'].create(create_val)
            stock_move = self.env['stock.move'].create({
                     'name': prod.name,
                     'product_id': prod.id,
                     'product_uom': prod.uom_id.id,
                     'product_uom_qty': qty,
                     'picking_id': stock_picking.id,
                     'location_id': stock_virtual_location.id,
                     'location_dest_id': wip_location.id,
                     'state': 'assigned',
                 })
            move_line = self.env['stock.move.line'].create({
                     'product_id': prod.id,
                     'product_uom_id': prod.uom_id.id,
                     'qty_done': qty,
                     'picking_id': stock_picking.id,
                     'move_id' : stock_move.id,
                     'location_id': stock_virtual_location.id,
                     'location_dest_id': wip_location.id,
                     'state': 'assigned',
                     'done_move': True,
                 })
            stock_picking.button_validate()
        elif prod.tracking == 'lot':
            new_lot = self.create_lot(prod, 1)
            create_val = {
                 'origin': self.name + ' FLSP-BF-ADJUST',
                 'picking_type_id': stock_picking_type.id,
                 'location_id': stock_virtual_location.id,
                 'location_dest_id': wip_location.id,
                 'state': 'assigned',}
            stock_picking = self.env['stock.picking'].create(create_val)
            stock_move = self.env['stock.move'].create({
                     'name': prod.name,
                     'product_id': prod.id,
                     'product_uom': prod.uom_id.id,
                     'product_uom_qty': qty,
                     'picking_id': stock_picking.id,
                     'location_id': stock_virtual_location.id,
                     'location_dest_id': wip_location.id,
                     'state': 'assigned',
                 })
            move_line = self.env['stock.move.line'].create({
                     'product_id': prod.id,
                     'product_uom_id': prod.uom_id.id,
                     'qty_done': qty,
                     'picking_id': stock_picking.id,
                     'move_id' : stock_move.id,
                     'lot_id': new_lot[0].id,
                     'location_id': stock_virtual_location.id,
                     'location_dest_id': wip_location.id,
                     'state': 'assigned',
                     'done_move': True,
                 })
            stock_picking.button_validate()
        else:
            new_lot = self.create_lot(prod, int(qty))
            create_val = {
                 'origin': self.name + ' FLSP-BF-ADJUST',
                 'picking_type_id': stock_picking_type.id,
                 'location_id': stock_virtual_location.id,
                 'location_dest_id': wip_location.id,
                 'state': 'assigned',}
            stock_picking = self.env['stock.picking'].create(create_val)
            stock_move = self.env['stock.move'].create({
                     'name': prod.name,
                     'product_id': prod.id,
                     'product_uom': prod.uom_id.id,
                     'product_uom_qty': qty,
                     'picking_id': stock_picking.id,
                     'location_id': stock_virtual_location.id,
                     'location_dest_id': wip_location.id,
                     'state': 'assigned',
                 })
            for lot in new_lot:
                move_line = self.env['stock.move.line'].create({
                         'product_id': prod.id,
                         'product_uom_id': prod.uom_id.id,
                         'qty_done': 1,
                         'picking_id': stock_picking.id,
                         'move_id': stock_move.id,
                         'lot_id': lot.id,
                         'location_id': stock_virtual_location.id,
                         'location_dest_id': wip_location.id,
                         'state': 'assigned',
                         'done_move': True,
                     })
            stock_picking.button_validate()
