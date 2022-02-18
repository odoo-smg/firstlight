# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class FlspwipTranferwiz(models.TransientModel):
    _name = 'flsp_wip_kanban.transfer.wiz'
    _description = "Wizard: Transfer"

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    kanban_id = fields.Many2one('flsp.wip.kanban', string='Kanban', readonly=True)
    standard_location = fields.Many2one('stock.location', string='Standard. Location', readonly=True)
    other_locations = fields.Char(string='Other Locations')

    location_a = fields.Many2one('stock.location', string='Location A', readonly=True)
    location_b = fields.Many2one('stock.location', string='Location B', readonly=True)
    location_c = fields.Many2one('stock.location', string='Location C', readonly=True)
    location_d = fields.Many2one('stock.location', string='Location D', readonly=True)
    location_e = fields.Many2one('stock.location', string='Location E', readonly=True)
    location_f = fields.Many2one('stock.location', string='Location F', readonly=True)
    location_g = fields.Many2one('stock.location', string='Location G', readonly=True)

    quantity_a = fields.Float("Quantity A")
    quantity_b = fields.Float("Quantity B")
    quantity_c = fields.Float("Quantity C")
    quantity_d = fields.Float("Quantity D")
    quantity_e = fields.Float("Quantity E")
    quantity_f = fields.Float("Quantity F")
    quantity_g = fields.Float("Quantity G")

    qty_transfer_a = fields.Float("Qty Transfer A")
    qty_transfer_b = fields.Float("Qty Transfer B")
    qty_transfer_c = fields.Float("Qty Transfer C")
    qty_transfer_d = fields.Float("Qty Transfer D")
    qty_transfer_e = fields.Float("Qty Transfer E")
    qty_transfer_f = fields.Float("Qty Transfer F")
    qty_transfer_g = fields.Float("Qty Transfer G")

    quantity_qa = fields.Float("QA Quantity")
    quantity_wh = fields.Float("Warehouse Quantity")

    po_date = fields.Date('Coming up')

    @api.model
    def default_get(self, fields):
        res = super(FlspwipTranferwiz, self).default_get(fields)
        kanban_id = self.env.context.get('kanban_id') ## or self.env.context.get('active_id')
        if kanban_id:
            kanban_to_transfer = self.env['flsp.wip.kanban'].search([('id', '=', kanban_id)])
        else:
            kanban_to_transfer = self.env['flsp.wip.kanban'].search([('completed', '=', False)])
        if kanban_to_transfer:
            for kaban in kanban_to_transfer:
                stock_quant = self.env['stock.quant'].search([('product_id', '=', kaban.product_id.id)])
                cage_locations = self.env['stock.location'].search(['|', ('complete_name', 'like', 'WH/Stock/E'), ('complete_name', 'like', 'WH/Stock/D')])
                qa_locations = self.env['stock.location'].search([('complete_name', 'like', 'WH/QA')])
                wh_locations = self.env['stock.location'].search([('complete_name', 'like', 'WH/Stock')])
                count_locations = 0
                last_location = False
                if 'product_id' in fields:
                    res['product_id'] = kaban.product_id.id
                if 'kanban_id' in fields:
                    res['kanban_id'] = kaban.id
                if 'standard_location' in fields:
                    res['standard_location'] = kaban.product_id.flsp_sd_location.id

                c_locations = self.find_locations(kaban.product_id.id)

                if 'other_locations' in fields:
                    res['other_locations'] = c_locations

                for stock in stock_quant:

                    if stock.location_id in qa_locations:
                        if 'quantity_qa' in fields:
                            if 'quantity_qa' in res:
                                res['quantity_qa'] += stock.quantity
                            else:
                                res['quantity_qa'] = stock.quantity
                    if stock.location_id in cage_locations:
                        if count_locations == 0:
                            if 'quantity_a' in fields:
                                if 'quantity_a' in res:
                                    res['quantity_a'] += stock.quantity
                                else:
                                    res['quantity_a'] = stock.quantity
                            if 'location_a' in fields:
                                res['location_a'] = stock.location_id
                        if count_locations == 1:
                            if 'quantity_b' in fields:
                                if 'quantity_b' in res:
                                    res['quantity_b'] += stock.quantity
                                else:
                                    res['quantity_b'] = stock.quantity
                            if 'location_b' in fields:
                                res['location_b'] = stock.location_id
                        if count_locations == 2:
                            if 'quantity_c' in fields:
                                if 'quantity_c' in res:
                                    res['quantity_c'] += stock.quantity
                                else:
                                    res['quantity_c'] = stock.quantity
                            if 'location_c' in fields:
                                res['location_c'] = stock.location_id
                        if count_locations == 3:
                            if 'quantity_d' in fields:
                                if 'quantity_d' in res:
                                    res['quantity_d'] += stock.quantity
                                else:
                                    res['quantity_d'] = stock.quantity
                            if 'location_d' in fields:
                                res['location_d'] = stock.location_id
                        if count_locations == 4:
                            if 'quantity_e' in fields:
                                if 'quantity_e' in res:
                                    res['quantity_e'] += stock.quantity
                                else:
                                    res['quantity_e'] = stock.quantity
                            if 'location_e' in fields:
                                res['location_e'] = stock.location_id
                        if count_locations == 5:
                            if 'quantity_f' in fields:
                                if 'quantity_f' in res:
                                    res['quantity_f'] += stock.quantity
                                else:
                                    res['quantity_f'] = stock.quantity
                            if 'location_f' in fields:
                                res['location_f'] = stock.location_id
                        if count_locations == 6:
                            if 'quantity_g' in fields:
                                if 'quantity_g' in res:
                                    res['quantity_g'] += stock.quantity
                                else:
                                    res['quantity_g'] = stock.quantity
                            if 'location_g' in fields:
                                res['location_g'] = stock.location_id
                        if stock.location_id != last_location:
                            count_locations += 1
                            last_location = stock.location_id
                    else:
                        if stock.location_id in wh_locations:
                            if 'quantity_wh' in fields:
                                if 'quantity_wh' in res:
                                    res['quantity_wh'] += stock.quantity
                                else:
                                    res['quantity_wh'] = stock.quantity
                if count_locations == 0:
                    open_pos = self.env['purchase.order.line'].search(['&', ('product_id', '=', kaban.product_id.id), ('state', 'not in', ['draft','cancel', 'done'])]).ids
                    open_moves = self.env['stock.move'].search(['&', ('purchase_line_id', 'in', open_pos), ('state', 'not in', ['draft', 'cancel', 'done'])]).sorted(lambda r: r.date_expected)
                    for move in open_moves:
                        if 'po_date' in fields:
                            res['po_date'] = move.date_expected
                        break


                break
        res = self._convert_to_write(res)
        return res

    def flsp_skip(self):
        kanban_to_transfer = self.env['flsp.wip.kanban'].search([('completed', '=', False)])
        next = False
        quit = False
        if kanban_to_transfer:
            for kaban in kanban_to_transfer:
                next = kaban
                if quit:
                    break
                if self.product_id == kaban.product_id:
                    quit = True
        if next:
            self.product_id = next.product_id
            action = self.env.ref('flsp_wip_transfer.launch_flsp_wip_kanban_transfer_wiz').read()[0]
            action['kanban_id'] = next.id
            action['context'] = dict(self._context, kanban_id=next.id, create=False)

        #action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
            return action


    def flsp_validate(self):
        kanban_to_transfer = self.env['flsp.wip.kanban'].search([('completed', '=', False)])
        next = False
        quit = False
        if kanban_to_transfer:
            for kaban in kanban_to_transfer:
                next = kaban
                if quit:
                    break
                if self.product_id == kaban.product_id:
                    quit = True
        if self.qty_transfer_a > 0:
            if self.wip_transfer(self.product_id, self.location_a, self.qty_transfer_a):
                self.kanban_id.completed = True
        else:
            self.kanban_id.completed = True
        if self.qty_transfer_b > 0:
            if self.wip_transfer(self.product_id, self.location_b, self.qty_transfer_b):
                self.kanban_id.completed = True
            else:
                self.kanban_id.completed = True
        if self.qty_transfer_c > 0:
            if self.wip_transfer(self.product_id, self.location_c, self.qty_transfer_c):
                self.kanban_id.completed = True
            else:
                self.kanban_id.completed = True
        if self.qty_transfer_d > 0:
            if self.wip_transfer(self.product_id, self.location_d, self.qty_transfer_d):
                self.kanban_id.completed = True
            else:
                self.kanban_id.completed = True
        if self.qty_transfer_e > 0:
            if self.wip_transfer(self.product_id, self.location_e, self.qty_transfer_e):
                self.kanban_id.completed = True
            else:
                self.kanban_id.completed = True
        if self.qty_transfer_f > 0:
            if self.wip_transfer(self.product_id, self.location_f, self.qty_transfer_f):
                self.kanban_id.completed = True
            else:
                self.kanban_id.completed = True
        if self.qty_transfer_g > 0:
            if self.wip_transfer(self.product_id, self.location_g, self.qty_transfer_g):
                self.kanban_id.completed = True
            else:
                self.kanban_id.completed = True

        if next:
            self.product_id = next.product_id
            action = self.env.ref('flsp_wip_transfer.launch_flsp_wip_kanban_transfer_wiz').read()[0]
            action['kanban_id'] = next.id
            action['context'] = dict(self._context, kanban_id=next.id, create=False)
            return action

    def wip_transfer(self, prod, location, qty):
        if not location or not prod or not qty:
            return False
        if qty <= 0:
            return False

        stock_quant = self.env['stock.quant'].search([('product_id', '=', prod.id), ('location_id', '=', location.id)])
        total_qty = 0
        has_lot = False
        has_package = False
        for stock in stock_quant:
            total_qty += stock.quantity
            if stock.lot_id:
                has_lot = True
            if stock.package_id:
                has_package = True
        if qty > total_qty:
            return False


        if not has_lot and not has_package:

            stock_picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'INT')])
            wip_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA/WIP')])
            create_val = {
                'origin': 'KANBAN-WIP',
                'picking_type_id': stock_picking_type.id,
                'location_id': location.id,
                'location_dest_id': wip_location.id,
                'state': 'assigned',
            }
            stock_picking = self.env['stock.picking'].create(create_val)

            stock_move = self.env['stock.move'].create({
                'name': prod.name,
                'product_id': prod.id,
                'product_uom': prod.uom_id.id,
                'product_uom_qty': qty,
                'origin': 'KANBAN-WIP',
                'picking_id': stock_picking.id,
                'location_id': location.id,
                'location_dest_id': wip_location.id,
                'state': 'assigned',
            })
            move_line = self.env['stock.move.line'].create({
                'product_id': prod.id,
                'product_uom_id': prod.uom_id.id,
                'qty_done': qty,
                'picking_id': stock_picking.id,
                'move_id': stock_move.id,
                'location_id': location.id,
                'origin': 'KANBAN-WIP',
                'location_dest_id': wip_location.id,
                'state': 'assigned',
                'done_move': True,
            })
            stock_picking.button_validate()
        else:
            remaining_qty = qty
            while remaining_qty > 0:
                qty_to_do = 0
                for stock in stock_quant:
                    if stock.quantity >= remaining_qty:
                        remaining_qty = 0
                        qty_to_do = qty
                    else:
                        remaining_qty = remaining_qty - stock.quantity
                        qty_to_do = stock.quantity

                    stock_picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'INT')])
                    wip_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA/WIP')])
                    create_val = {
                        'origin': 'KANBAN-WIP',
                        'picking_type_id': stock_picking_type.id,
                        'location_id': location.id,
                        'location_dest_id': wip_location.id,
                        'state': 'assigned',
                    }
                    stock_picking = self.env['stock.picking'].create(create_val)

                    stock_move = self.env['stock.move'].create({
                        'name': prod.name,
                        'product_id': prod.id,
                        'product_uom': prod.uom_id.id,
                        'product_uom_qty': qty_to_do,
                        'picking_id': stock_picking.id,
                        'origin': 'KANBAN-WIP',
                        'location_id': location.id,
                        'location_dest_id': wip_location.id,
                        'state': 'assigned',
                    })
                    move_line = self.env['stock.move.line'].create({
                        'product_id': prod.id,
                        'product_uom_id': prod.uom_id.id,
                        'qty_done': qty_to_do,
                        'picking_id': stock_picking.id,
                        'move_id': stock_move.id,
                        'location_id': location.id,
                        'lot_id': stock.lot_id.id,
                        'package_id': stock.package_id.id,
                        'origin': 'KANBAN-WIP',
                        'location_dest_id': wip_location.id,
                        'state': 'assigned',
                        'done_move': True,
                    })
                    stock_picking.button_validate()

            ###'lot_id': wip.negative_lot_id.id,

        return True

    def find_locations(self, prod_id):
        c_ret = ''

        query = '''
        select string_agg(name, ', ') as locations  from (
        select distinct name, grp  from (
        select '1' as grp, loc from (
        select distinct location_id as loc from stock_move_line where product_id = '''+str(prod_id)+'''
        union all
        select distinct location_dest_id as loc from stock_move_line where product_id = '''+str(prod_id)+'''
        ) A) B
        inner join stock_location sl
        on sl.id = B.loc
        where usage = 'internal'
        and   active = true) C
		group by grp

        '''

        self._cr.execute(query)
        retvalue = self._cr.fetchall()
        returned_registre = retvalue[0]
        for line in returned_registre:
            c_ret += line + ', '

        c_ret = c_ret[:-2]
        return c_ret
