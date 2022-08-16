from odoo import models, fields, api
from datetime import datetime


class FlspOpenMoves(models.Model):
    _name = 'flsp.open.moves'
    _description = 'FLSP Open Moves'

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    type = fields.Selection([('in', 'IN'),('out', 'OUT')], string='Type', readonly=True)
    source = fields.Selection([('po', 'Purchase'), ('mo', 'Manufacture'), ('so', 'Sales')], string='Source', readonly=True)
    doc = fields.Char(string='Document', readonly=True)
    qty = fields.Float(string='Quantity', readonly=True)
    uom = fields.Many2one('uom.uom', 'U of M', readonly=True)
    date = fields.Datetime(string="Date", readonly=True)
    avg_sbs = fields.Float(string='Avg SBS')
    avg_ssa = fields.Float(string='Avg SSA')
    level = fields.Integer(string='level')
    lead_time = fields.Integer(string='Lead Time')
    user_id = fields.Many2one('res.users', string="User")

    def clean_up_all(self):
        for each in self:
            each.unlink()
        actual_moves = self.env['flsp.current.month.moves'].search([])
        for each in actual_moves:
            each.unlink()

    def calculate_purchase_mrp(self, purchase_mrp_id, product_from, product_to):

        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id
        receipt_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Receipts')]).ids
        delivery_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')]).ids
        current_date = datetime.now()
        standard_lead_time = 14
        indirect_lead_time = 1

        open_moves = []
        actual_mvs = {}
        # index  type, source,     doc,          product_id,   qty,  uom   date                  level  lead time  avg-sbs avg-ssa
        #         IN   Purchase    WH/IN/P0001       32          5   each  2020-01-01 00:00:00     1        1         99     99
        #         IN   Manufacture WH/MO/M0001       32          5   each  2020-01-01 00:00:00     1        1         99     99
        #        OUT   Sales       WH/OUT/P0001      33          8   each  2020-01-01 00:00:00     1        1         99     99
        #        OUT   Manufacture WH/MO/M0001       32          5   each  2020-01-01 00:00:00     1        1         99     99

        # *******************************************************************************
        # ***************************** Purchase Orders *********************************
        # *******************************************************************************
        if purchase_mrp_id.consider_po:
            open_receipts = self.env['stock.picking'].search(['&', ('state', 'not in', ['done', 'cancel', 'draft']), ('picking_type_id', 'in', receipt_stock_type)])
            for receipt in open_receipts: # .with_progress("sub-operation - Purchase"):
                stock_move_product = self.env['stock.move'].search([('picking_id', '=', receipt.id)])
                for move in stock_move_product:
                    if receipt.origin:
                        doc = (receipt.origin + '                 ')[0:17]
                    else:
                        doc = '                 '
                    if move.product_id.type in ['service', 'consu']:
                        continue
                    if move.product_id.id < product_from or move.product_id.id > product_to or route_buy not in move.product_id.route_ids.ids:
                        continue

                    open_moves.append([len(open_moves) + 1, 'In   ', 'Purchase',
                                       doc,
                                       move.product_id,
                                       move.product_uom_qty, move.product_uom,
                                       move.date, 0, 0, 0, 0])
                    self.create({
                                    'product_id': move.product_id.id,
                                    'type': 'in',
                                    'source': 'po',
                                    'doc': doc,
                                    'qty': move.product_uom_qty,
                                    'uom': move.product_uom.id,
                                    'date': move.date_expected,
                                })

        # *******************************************************************************
        # ***************************** Sales Orders ************************************
        # *******************************************************************************
        if purchase_mrp_id.consider_so:
            open_deliveries = self.env['stock.picking'].search(['&', ('state', 'not in', ['cancel', 'draft']), ('picking_type_id', 'in', delivery_stock_type)])
            for delivery in open_deliveries: # .with_progress("sub-operation - Sales Orders"):
                if delivery.state == 'done':
                    if delivery.date_done.month != current_date.month or delivery.date_done.year != current_date.year:
                        continue
                    stock_move_product = self.env['stock.move'].search([('picking_id', '=', delivery.id)])
                    for move in stock_move_product:
                        move_bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', move.product_id.product_tmpl_id.id)],limit=1)
                        if not move_bom:
                            if move.product_id.type in ['service', 'consu']:
                                continue
                            if move.product_id.id < product_from or move.product_id.id > product_to or route_buy not in move.product_id.route_ids.ids:
                                continue

                            actual_move = self.env['flsp.current.month.moves'].search([('product_id', '=', move.product_id.id)])
                            if actual_move:
                                actual_move.qty += move.product_uom_qty
                            else:
                                self.env['flsp.current.month.moves'].create({
                                            'product_id': move.product_id.id,
                                            'qty': move.product_uom_qty,
                                        })

                            if move.product_id.id not in actual_mvs:
                                actual_mvs[move.product_id.id] = move.product_uom_qty
                            else:
                                actual_mvs[move.product_id.id] += move.product_uom_qty

                        else:
                            move_components = self._get_flattened_totals(move_bom, move.product_uom_qty, {}, 0, True)
                            for prod in move_components:
                                if prod.type in ['service', 'consu']:
                                    continue
                                if move_components[prod]['total'] <= 0:
                                    continue
                                if prod.id < product_from or prod.id > product_to or route_buy not in prod.route_ids.ids:
                                    continue
                                actual_move = self.env['flsp.current.month.moves'].search([('product_id', '=', prod.id)])
                                if actual_move:
                                    actual_move.qty += move_components[prod]['total']
                                else:
                                    self.env['flsp.current.month.moves'].create({
                                                'product_id': prod.id,
                                                'qty': move_components[prod]['total'],
                                            })
                                if prod.id not in actual_mvs:
                                    actual_mvs[prod.id] = move_components[prod]['total']
                                else:
                                    actual_mvs[prod.id] += move_components[prod]['total']

                else: # delivery.state != 'done':
                    stock_move_product = self.env['stock.move'].search([('picking_id', '=', delivery.id)])
                    for move in stock_move_product:
                        move_bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', move.product_id.product_tmpl_id.id)],
                                                              limit=1)
                        if not move_bom:
                            avg_per_sbs = 0
                            avg_per_ssa = 0
                            if move.product_id.categ_id.flsp_name_report == 'ISBS':
                                avg_per_sbs = move.product_uom_qty
                            if move.product_id.categ_id.flsp_name_report == 'FISA':
                                avg_per_ssa = move.product_uom_qty
                            if delivery.origin:
                                doc = (delivery.origin + '                 ')[0:17]
                            else:
                                doc = '                 '

                            if move.product_id.type in ['service', 'consu']:
                                continue
                            if move.product_id.id < product_from or move.product_id.id > product_to or route_buy not in move.product_id.route_ids.ids:
                                continue
                            open_moves.append([len(open_moves) + 1, 'Out  ', 'Sales   ',
                                               doc,
                                               move.product_id,
                                               move.product_uom_qty, move.product_uom,
                                               delivery.scheduled_date, 0, standard_lead_time, avg_per_sbs, avg_per_ssa])
                            self.create({
                                'product_id': move.product_id.id,
                                'type': 'out',
                                'source': 'so',
                                'doc': doc,
                                'qty': move.product_uom_qty,
                                'uom': move.product_uom.id,
                                'date': delivery.scheduled_date,
                                'level': 0,
                                'lead_time': standard_lead_time,
                                'avg_sbs': avg_per_sbs,
                                'avg_ssa': avg_per_ssa,
                            })

                        else:
                            move_components = self._get_flattened_totals(move_bom, move.product_uom_qty, {}, 0, True)
                            for prod in move_components:
                                avg_per_sbs = 0
                                avg_per_ssa = 0
                                if prod.type in ['service', 'consu']:
                                    continue
                                if move_components[prod]['total'] <= 0:
                                    continue
                                if move.product_id.categ_id.flsp_name_report == 'ISBS':
                                    if 'SET' in move.product_id.name:
                                        avg_per_sbs = move_components[prod]['total']/(move.product_uom_qty*2)
                                    else:
                                        avg_per_sbs = move_components[prod]['total'] / move.product_uom_qty
                                if move.product_id.categ_id.flsp_name_report == 'FISA':
                                    avg_per_ssa = move_components[prod]['total']/move.product_uom_qty
                                if delivery.origin:
                                    doc = (delivery.origin + '                 ')[0:17]
                                else:
                                    doc = '                 '

                                if prod.id < product_from or prod.id > product_to or route_buy not in prod.route_ids.ids:
                                    continue
                                self.create({
                                    'product_id': prod.id,
                                    'type': 'out',
                                    'source': 'so',
                                    'doc': doc,
                                    'qty': move_components[prod]['total'],
                                    'uom': prod.uom_id.id,
                                    'date': delivery.scheduled_date,
                                    'level': move_components[prod]['level'],
                                    'lead_time': standard_lead_time + (indirect_lead_time * move_components[prod]['level']),
                                    'avg_sbs': avg_per_sbs,
                                    'avg_ssa': avg_per_ssa,
                                })
                                open_moves.append([len(open_moves) + 1, 'Out  ', 'Sales   ',
                                                   doc,
                                                   prod,
                                                   move_components[prod]['total'], prod.uom_id.id,
                                                   delivery.scheduled_date, move_components[prod]['level'],
                                                   standard_lead_time + (indirect_lead_time * move_components[prod]['level']), avg_per_sbs, avg_per_ssa])
                                subs = self.env['flsp.mrp.substitution.line'].search(['&', ('product_id', '=', prod.id),
                                     ('flsp_bom_id', '=', move_bom.id)]).product_substitute_id
                                if subs:
                                    for substitute_product in subs:
                                        if substitute_product.type in ['service', 'consu']:
                                            continue
                                        open_moves.append([len(open_moves) + 1, 'Out  ', 'Sales   ',
                                                           doc,
                                                           substitute_product,
                                                           move_components[prod]['total'], substitute_product.uom_id.id,
                                                           delivery.scheduled_date, move_components[prod]['level'],
                                                           standard_lead_time + (
                                                                       indirect_lead_time * move_components[prod][
                                                                   'level']), avg_per_sbs, avg_per_ssa])
                                        self.create({
                                            'product_id': substitute_product.id,
                                            'type': 'out',
                                            'source': 'so',
                                            'doc': doc,
                                            'qty': move_components[prod]['total'],
                                            'uom': prod.uom_id.id,
                                            'date': delivery.scheduled_date,
                                            'level': move_components[prod]['level'],
                                            'lead_time': standard_lead_time + (
                                                        indirect_lead_time * move_components[prod]['level']),
                                            'avg_sbs': avg_per_sbs,
                                            'avg_ssa': avg_per_ssa,
                                        })

        # *******************************************************************************
        # ************************ Manufacturing Orders *********************************
        # *******************************************************************************
        if purchase_mrp_id.consider_mo:
            if purchase_mrp_id.consider_mo_drafts:
                production_orders = self.env['mrp.production'].search([('state', 'not in', ['done', 'cancel'])])
            else:
                production_orders = self.env['mrp.production'].search([('state', 'not in', ['done', 'cancel', 'draft'])])
            for production in production_orders:
                move_components = self._get_flattened_totals(production.bom_id, production.product_qty, {}, 0,True)

                for prod in move_components:
                    if move_components[prod]['level'] == 1:
                        if prod.id < product_from or prod.id > product_to or route_buy not in prod.route_ids.ids:
                            continue
                        open_moves.append([len(open_moves) + 1, 'In   ', 'MO      ',
                                           (production.name + '                 ')[0:17],
                                           prod,
                                           move_components[prod]['total'], prod.uom_id.id,
                                           production.date_planned_start, move_components[prod]['level'],
                                           standard_lead_time + (move_components[prod]['level'] * indirect_lead_time), 0, 0])
                        subs = self.env['flsp.mrp.substitution.line'].search(
                            ['&', ('product_id', '=', prod.id), ('flsp_bom_id', '=', production.bom_id.id)]).product_substitute_id
                        if subs:
                            for substitute_product in subs:
                                open_moves.append([len(open_moves) + 1, 'In   ', 'MO      ',
                                                   (production.name + '                 ')[0:17],
                                                   substitute_product,
                                                   move_components[prod]['total'], substitute_product.uom_id.id,
                                                   production.date_planned_start, move_components[prod]['level'],
                                                   standard_lead_time + (move_components[prod]['level'] * indirect_lead_time), 0, 0])
                        continue
                    if prod.type in ['service', 'consu']:
                        continue
                    if move_components[prod]['total'] <= 0:
                        continue
                    if production.name:
                        doc = (production.name + '                 ')[0:-17]
                    else:
                        doc = '                 '

                    if prod.id < product_from or prod.id > product_to or route_buy not in prod.route_ids.ids:
                        continue

                    open_moves.append([len(open_moves) + 1, 'Out  ', 'MO      ',
                                       doc,
                                       prod,
                                       move_components[prod]['total'], prod.uom_id.id,
                                       production.date_planned_start, move_components[prod]['level'],
                                       standard_lead_time + (indirect_lead_time * move_components[prod]['level']), 0, 0])
                    subs = self.env['flsp.mrp.substitution.line'].search(['&', ('product_id', '=', prod.id),
                         ('flsp_bom_id', '=', production.bom_id.id)]).product_substitute_id
                    if subs:
                        for substitute_product in subs:
                            open_moves.append([len(open_moves) + 1, 'Out  ', 'MO      ',
                                               doc,
                                               substitute_product,
                                               move_components[prod]['total'], substitute_product.uom_id.id,
                                               production.date_planned_start, move_components[prod]['level'],
                                               standard_lead_time + (indirect_lead_time * move_components[prod]['level']),
                                               0, 0])

        return [open_moves, actual_mvs]


    def _get_flattened_totals(self, bom, factor=1, totals=None, level=None, backflush=False, substitute=False):
        """Calculate the **unitary** product requirements of flattened BOM.
        *Unit* means that the requirements are computed for one unit of the
        default UoM of the product.
        :returns: dict: keys are components and values are aggregated quantity
        in the product default UoM.
        """
        route_mfg = self.env.ref('mrp.route_warehouse0_manufacture').id
        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id

        if level is None:
            level = 0
        if totals is None:
            totals = {}
        factor /= bom.product_uom_id._compute_quantity(
            bom.product_qty, bom.product_tmpl_id.uom_id, round=False
        )
        if substitute:
            for line in bom.flsp_substitution_line_ids:
                #sub_bom = bom._bom_find(product=line.product_substitute_id)
                # Considering we don't have any sub-assembly
                sub_bom = False
                if route_buy in line.product_substitute_id.route_ids.ids:
                    sub_bom = False
                if sub_bom:
                    # if backflush and not line.product_id.product_tmpl_id.flsp_backflush:
                    if totals.get(line.product_substitute_id):
                        totals[line.product_substitute_id]['total'] += (
                                factor
                                * line.product_substitute_uom_id._compute_quantity(
                            line.product_substitute_qty, line.product_substitute_id.uom_id, round=False
                        )
                        )
                    else:
                        totals[line.product_substitute_id] = {'total': (
                                factor
                                * line.product_substitute_uom_id._compute_quantity(
                            line.product_substitute_qty, line.product_substitute_id.uom_id, round=False
                        )
                        ), 'level': level, 'bom': sub_bom.code}
                    #                continue
                    #                else:
                    new_factor = factor * line.product_substitute_uom_id._compute_quantity(
                        line.product_substitute_qty, line.product_substitute_id.uom_id, round=False
                    )

                    level += 1
                    self._get_flattened_totals(sub_bom, new_factor, totals, level, backflush, substitute)
                    level -= 1
                else:
                    if totals.get(line.product_substitute_id):
                        totals[line.product_substitute_id]['total'] += (
                                factor
                                * line.product_substitute_uom_id._compute_quantity(
                            line.product_substitute_qty, line.product_substitute_id.uom_id, round=False
                        )
                        )
                    else:
                        totals[line.product_substitute_id] = {'total': (
                                factor
                                * line.product_substitute_uom_id._compute_quantity(
                            line.product_substitute_qty, line.product_substitute_id.uom_id, round=False
                        )
                        ), 'level': level, 'bom': ''}

        for line in bom.bom_line_ids:

            # ****** Version 15 ******
            # sub_bom = bom._bom_find(line.product_id)[line.product_id]


            # ****** Version 13 ******
            sub_bom = bom._bom_find(product=line.product_id)
            if route_buy in line.product_id.route_ids.ids:
                sub_bom = False
            if sub_bom:
                #if backflush and not line.product_id.product_tmpl_id.flsp_backflush:
                if totals.get(line.product_id):
                    totals[line.product_id]['total'] += (
                            factor
                            * line.product_uom_id._compute_quantity(
                        line.product_qty, line.product_id.uom_id, round=False
                    )
                    )
                else:
                    totals[line.product_id] = {'total': (
                            factor
                            * line.product_uom_id._compute_quantity(
                        line.product_qty, line.product_id.uom_id, round=False
                    )
                    ), 'level': level, 'bom': sub_bom.code}
#                continue
#                else:
                new_factor = factor * line.product_uom_id._compute_quantity(
                    line.product_qty, line.product_id.uom_id, round=False
                )

                level += 1
                self._get_flattened_totals(sub_bom, new_factor, totals, level, backflush, substitute)
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
                    totals[line.product_id] = {'total': (
                            factor
                            * line.product_uom_id._compute_quantity(
                        line.product_qty, line.product_id.uom_id, round=False
                    )
                    ), 'level': level, 'bom': ''}
        return totals


class FlspActualMoves(models.Model):
    _name = 'flsp.current.month.moves'
    _description = 'Current Month Consumption'

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    qty = fields.Float(string='Quantity', readonly=True)
