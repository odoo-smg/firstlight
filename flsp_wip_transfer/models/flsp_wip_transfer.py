# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import datetime


class FlspMrpPlanningLine(models.Model):
    _name = 'flsp.wip.transfer'
    _description = 'FLSP Weekly Transfer'

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

    adjusted = fields.Float(string='Adjusted', states={'negative': [('readonly', False)]})
    state = fields.Selection([
        ('transfer', 'to transfer'),
        ('negative', 'to adjust'),
        ('short', 'not available'),
        ('done', 'done'),
    ], string='State', readonly=True)
    stock_picking = fields.Many2one('stock.picking', string='Stock Picking', readonly=False)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', readonly=False)
    stock_move_id = fields.Many2one('stock.move', string='Move Line Id', readonly=True)

    purchase_uom = fields.Many2one('uom.uom', 'Purchase Unit of Measure', readonly=True)
    purchase_stock_qty = fields.Float(string='WH/Stock 2nd uom', readonly=True)
    purchase_pa_wip_qty = fields.Float(string='PA/WIP 2nd uom', readonly=True)
    purchase_mfg_demand = fields.Float(string='Qty 2nd uom', readonly=True)
    purchase_adjusted = fields.Float(string='Adjusted 2nd uom')

    negative_location_id = fields.Many2one('stock.location', string="Negative Location")
    negative_lot_id = fields.Many2one('stock.production.lot', string="Negative Serial/Lot")

    @api.onchange('adjusted')
    def onchange_adjusted(self):
        self.purchase_adjusted = self.product_id.uom_id._compute_quantity(self.adjusted, self.product_id.uom_po_id)
        wip_trans = self.env['flsp.wip.transfer'].search([('id', '=', self._origin.id)])
        if wip_trans:
            wip_trans.purchase_adjusted = self.product_id.uom_id._compute_quantity(self.adjusted, self.product_id.uom_po_id)



    def _flsp_calc_demands(self, days_ahead, bring_negative):

        cur_date = datetime.datetime.now().date()
        date_mo = (cur_date + relativedelta(days=+ days_ahead))

        production_orders = self.env['mrp.production'].search(
            ['&', ('state', 'not in', ['done', 'cancel', 'draft']), ('date_planned_start', '<=', date_mo)])


        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')]).parent_path
        if not pa_location:
            raise UserError('WIP Stock Location is missing')
        pa_wip_locations = self.env['stock.location'].search([('parent_path', 'like', pa_location+'%')]).ids
        if not pa_wip_locations:
            raise UserError('WIP Stock Location is missing')

        ## Remove production orders done or negative:
        wip_transfers = self.env['flsp.wip.transfer'].search([('state', 'in', ['transfer', 'negative'])])

        for wip_trans in wip_transfers:
            delete_wip = True
            #for production in production_orders:
            #    if wip_trans.source == production.name:
            #        delete_wip = False
            if delete_wip:
                wip_trans.unlink()

        # Add products with negative quantity in WIP:
        if bring_negative:
            negative_stock_quant = self.env['stock.quant'].search(['&', ('location_id', 'in', pa_wip_locations), ('quantity', '<', 0)])
            for item in negative_stock_quant:
                if item.product_id.type not in ['service', 'consu']:
                    stock_quant = self.env['stock.quant'].search(
                        ['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', item.product_id.id)])
                    pa_wip_qty = 0
                    for stock_lin in stock_quant:
                        pa_wip_qty += stock_lin.quantity
                    lot_id = False
                    if item.product_id.tracking == 'none':
                        lot_name = ''
                        lot_id = False
                    else:
                        if item.lot_id:
                            lot_name = ' lot: '+ item.lot_id.name
                            lot_id = item.lot_id.id
                        else:
                            lot_name = ''
                            lot_id = False

                    # insert new
                    wip = self.env['flsp.wip.transfer'].create({
                        'description': item.product_id.name,
                        'default_code': item.product_id.default_code,
                        'product_id': item.product_id.id,
                        'uom': item.product_id.uom_id.id,
                        'stock_qty': item.product_id.qty_available - pa_wip_qty,
                        'pa_wip_qty': pa_wip_qty,
                        'source': 'Negative Adjustment - location: '+item.location_id.name+lot_name,
                        'mfg_demand': item.quantity * (-1),
                        'suggested': 1,
                        'adjusted': item.quantity * (-1),
                        'state': 'negative',
                        'negative_location_id': item.location_id.id,
                        'negative_lot_id': lot_id,
                        'purchase_uom': item.product_id.uom_po_id.id,
                        'purchase_stock_qty': item.product_id.uom_id._compute_quantity(item.product_id.qty_available - pa_wip_qty,
                                                                            item.product_id.uom_po_id),
                        'purchase_pa_wip_qty': item.product_id.uom_id._compute_quantity(pa_wip_qty, item.product_id.uom_po_id),
                        'purchase_mfg_demand': item.product_id.uom_id._compute_quantity(item.quantity * (-1),
                                                                             item.product_id.uom_po_id),
                        'purchase_adjusted': item.product_id.uom_id._compute_quantity(item.quantity * (-1),
                                                                           item.product_id.uom_po_id),
                        })
        else:
            for production in production_orders:
                if production.origin:
                    if production.origin[0:1] != 'S' or production.origin == 'Stock':
                        continue
                else:
                    continue
                components = self._get_flattened_totals(production.bom_id, production.product_qty)
                for prod in components:
                    if prod.type in ['service', 'consu']:
                        continue
                    if components[prod]['total'] > 0:
                        wip_trans = self.env['flsp.wip.transfer'].search(['&', ('product_id', '=', prod.id), ('state', '=', 'transfer')])
                        stock_quant = self.env['stock.quant'].search(['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', prod.id)])
                        pa_wip_qty = 0
                        for stock_lin in stock_quant:
                            pa_wip_qty += stock_lin.quantity

                        if wip_trans:
                            #update current
                            wip_trans.mfg_demand = wip_trans.mfg_demand + components[prod]['total']
                            wip_trans.suggested = 1
                            wip_trans.adjusted = wip_trans.mfg_demand
                            wip_trans.stock_qty = prod.qty_available - pa_wip_qty
                            wip_trans.pa_wip_qty = pa_wip_qty
                            wip_trans.purchase_uom = prod.uom_po_id.id
                            wip_trans.purchase_stock_qty = prod.uom_id._compute_quantity(prod.qty_available - pa_wip_qty, prod.uom_po_id)
                            wip_trans.purchase_pa_wip_qty = prod.uom_id._compute_quantity(pa_wip_qty, prod.uom_po_id)
                            wip_trans.purchase_mfg_demand = wip_trans.purchase_mfg_demand + prod.uom_id._compute_quantity(components[prod]['total'],prod.uom_po_id)
                            wip_trans.purchase_adjusted = wip_trans.purchase_mfg_demand
                            #wip_trans.source = wip_trans.source + ' / ' + production.name

                        else:
                            #insert new
                            wip = self.env['flsp.wip.transfer'].create({
                                'description': prod.name,
                                'default_code': prod.default_code,
                                'product_id': prod.id,
                                'uom': prod.uom_id.id,
                                'stock_qty': prod.qty_available - pa_wip_qty,
                                'pa_wip_qty': pa_wip_qty,
                                'source': production.name,
                                'mfg_demand': components[prod]['total'],
                                'suggested': 1,
                                'adjusted': components[prod]['total'],
                                'state': 'transfer',
                                'production_id': production.id,
                                'purchase_uom': prod.uom_po_id.id,
                                'purchase_stock_qty': prod.uom_id._compute_quantity(prod.qty_available - pa_wip_qty, prod.uom_po_id),
                                'purchase_pa_wip_qty': prod.uom_id._compute_quantity(pa_wip_qty, prod.uom_po_id),
                                'purchase_mfg_demand': prod.uom_id._compute_quantity(components[prod]['total'], prod.uom_po_id),
                                'purchase_adjusted': prod.uom_id._compute_quantity(components[prod]['total'], prod.uom_po_id),
                            })

            ## Minimal quantity
            # products already suggested:
            wip_trans = self.env['flsp.wip.transfer'].search([])
            products = self.env['product.product'].search([('id', 'in', wip_trans.mapped('product_id').ids)])
            for product in products:
                pa_wip_qty = 0

                wips_total = self.env['flsp.wip.transfer'].search(['&', ('product_id', '=', product.id), ('state', '=', 'transfer')])
                already_suggested = sum(wips_total.mapped('mfg_demand'))
                stock_quant = self.env['stock.quant'].search(['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', product.id)])
                for stock_lin in stock_quant:
                    pa_wip_qty += stock_lin.quantity

                current_balance = pa_wip_qty
                wip_order_point = self.env['stock.warehouse.orderpoint'].search(['&', ('product_id', '=', product.id), ('location_id', 'in', pa_wip_locations)], limit=1)
                if wip_order_point:
                    min_qty = wip_order_point.product_min_qty
                    max_qty = wip_order_point.product_max_qty
                    multiple = wip_order_point.qty_multiple
                else:
                    min_qty = 0.0
                    max_qty = 0.0
                    multiple = 1

                # Minimal quantity:
                if current_balance < 0:
                    suggested_qty = min_qty - current_balance
                else:
                    if current_balance+already_suggested < min_qty:
                        suggested_qty = min_qty - (current_balance+already_suggested)
                    else:
                        suggested_qty = 0
                # checking multiple quantities - including the already suggested qty
                if multiple > 1:
                    if multiple > suggested_qty+already_suggested:
                        suggested_qty += multiple - suggested_qty+already_suggested
                    else:
                        if ((suggested_qty+already_suggested) % multiple) > 0:
                            suggested_qty += multiple-((suggested_qty+already_suggested) % multiple)

                if suggested_qty > 0:
                    wip = self.env['flsp.wip.transfer'].create({
                        'description': product.name,
                        'default_code': product.default_code,
                        'product_id': product.id,
                        'uom': product.uom_id.id,
                        'stock_qty': product.qty_available - pa_wip_qty,
                        'pa_wip_qty': pa_wip_qty,
                        'source': 'Min Qty',
                        'mfg_demand': suggested_qty,
                        'suggested': 1,
                        'adjusted': suggested_qty,
                        'state': 'transfer',
                        'purchase_uom': product.uom_po_id.id,
                        'purchase_stock_qty': product.uom_id._compute_quantity(product.qty_available - pa_wip_qty,
                                                                            product.uom_po_id),
                        'purchase_pa_wip_qty': product.uom_id._compute_quantity(pa_wip_qty, product.uom_po_id),
                        'purchase_mfg_demand': product.uom_id._compute_quantity(suggested_qty, product.uom_po_id),
                        'purchase_adjusted': product.uom_id._compute_quantity(suggested_qty, product.uom_po_id),
                    })

            # products not suggested yet:
            wip_trans = self.env['flsp.wip.transfer'].search([])
            products = self.env['product.product'].search([('id', 'not in', wip_trans.mapped('product_id').ids)])
            for product in products:
                pa_wip_qty = 0
                stock_quant = self.env['stock.quant'].search(['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', product.id)])
                for stock_lin in stock_quant:
                    pa_wip_qty += stock_lin.quantity

                current_balance = pa_wip_qty
                wip_order_point = self.env['stock.warehouse.orderpoint'].search(['&', ('product_id', '=', product.id), ('location_id', 'in', pa_wip_locations)], limit=1)
                if wip_order_point:
                    min_qty = wip_order_point.product_min_qty
                    max_qty = wip_order_point.product_max_qty
                    multiple = wip_order_point.qty_multiple
                else:
                    min_qty = 0.0
                    max_qty = 0.0
                    multiple = 1
                if multiple == False:
                    multiple = 1
                if multiple <= 0:
                    multiple = 1
                # Minimal quantity:
                if current_balance < 0:
                    suggested_qty = min_qty - current_balance
                else:
                    if current_balance < min_qty:
                        suggested_qty = min_qty - current_balance
                    else:
                        suggested_qty = 0

                # checking multiple quantities - just because it haven't being suggested yet
                if multiple > 1:
                    if multiple > suggested_qty:
                        suggested_qty += multiple - suggested_qty
                    else:
                        if (suggested_qty % multiple) > 0:
                            suggested_qty += multiple - (suggested_qty % multiple)

                if suggested_qty > 0:
                    wip = self.env['flsp.wip.transfer'].create({
                        'description': product.name,
                        'default_code': product.default_code,
                        'product_id': product.id,
                        'uom': product.uom_id.id,
                        'stock_qty': product.qty_available - pa_wip_qty,
                        'pa_wip_qty': pa_wip_qty,
                        'source': 'Min Qty',
                        'mfg_demand': suggested_qty,
                        'suggested': 1,
                        'adjusted': suggested_qty,
                        'state': 'transfer',
                        'purchase_uom': product.uom_po_id.id,
                        'purchase_stock_qty': product.uom_id._compute_quantity(product.qty_available - pa_wip_qty,
                                                                            product.uom_po_id),
                        'purchase_pa_wip_qty': product.uom_id._compute_quantity(pa_wip_qty, product.uom_po_id),
                        'purchase_mfg_demand': product.uom_id._compute_quantity(suggested_qty, product.uom_po_id),
                        'purchase_adjusted': product.uom_id._compute_quantity(suggested_qty, product.uom_po_id),
                    })
        return

    def _compute_quantity(self):
        for mps in self:
            mps.moves_qty = sum(mps.move_ids.filtered(lambda m: m.picking_id).mapped('product_qty'))
            mps.manufacture_qty = sum(mps.move_ids.filtered(lambda m: m.production_id).mapped('product_qty'))
            mps.rfq_qty = sum([l.product_uom._compute_quantity(l.product_qty, l.product_id.uom_id) for l in mps.purchase_order_line_ids])
            mps.total_qty = mps.moves_qty + mps.manufacture_qty + mps.rfq_qty


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
                negative_adjust = False
            count_products += 1
        negative_adjust = False
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