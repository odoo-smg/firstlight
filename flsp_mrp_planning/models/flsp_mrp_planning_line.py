# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api
from datetime import timedelta
from datetime import datetime

class FlspMrpPlanningLine(models.Model):
    _name = 'flsp.mrp.planning.line'
    _description = 'FLSP MRP Planning Line'

    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    stock_picking = fields.Many2one('stock.picking', string='Stock Picking', readonly=False)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', readonly=False)
    product_min_qty = fields.Float('Min. Qty', readonly=True)
    qty_multiple = fields.Float('Qty Multiple', readonly=True)
    product_qty = fields.Float(string='Qty on Hand', readonly=True)
    qty_mo = fields.Float(string='Qty of Draft MO', readonly=True)
    curr_outs = fields.Float(String="Demand", readonly=True, help="Includes all confirmed sales orders and manufacturing orders")
    curr_ins = fields.Float(String="Replenishment", readonly=True, help="Includes all confirmed purchase orders and manufacturing orders")
    average_use = fields.Float(String="Avg Use", readonly=True, help="Average usage of the past 3 months.")
    month1_use = fields.Float(String="2020-06 Usage", readonly=True, help="Total usage of last month.")
    month2_use = fields.Float(String="2020-05 Usage", readonly=True, help="Total usage of 2 months ago.")
    month3_use = fields.Float(String="2020-04 Usage", readonly=True, help="Total usage of 3 months ago.")
    suggested_qty = fields.Float(String="Suggested Qty", readonly=True, help="Quantity suggested to buy or produce.")
    adjusted_qty = fields.Float(String="Adjusted Qty", help="Adjust the quantity to be executed.")
    qty_rfq = fields.Float(String="RFQ Qty", readonly=True, help="Total Quantity of Requests for Quotation.")
    level_bom = fields.Integer(String="BOM Level", readonly=True, help="Position of the product inside of a BOM.")
    route_buy = fields.Selection([('buy', 'To Buy'),('na' , 'Non Applicable'),], string='To Buy', readonly=True)
    route_mfg = fields.Selection([('mfg', 'To Manufacture'),('na' , 'Non Applicable'),], string='To Produce', readonly=True)
    state = fields.Selection([
        ('buy', 'To Buy'),
        ('ok' , 'No Action'),
        ('po' , 'Confirm PO'),
        ('mo' , 'Confirm MO'),
        ('mfg', 'To Manufacture'),
    ], string='State', readonly=True)
    type = fields.Char(string='Type', readonly=True)
    start_date = fields.Date(String="Start Date", readonly=True)
    deadline_date = fields.Date(String="Deadline", readonly=True)
    rationale = fields.Html(string='Rationale')
    source = fields.Char(string='Source')
    source_description = fields.Char(string='Source Description')
    calculated = fields.Boolean('Calculated Flag')

    def _flsp_calc_planning(self, calculate_sub_levels=False, standard_lead_time=1, standard_queue_time=1, indirect_lead_time=1, consider_drafts=True):
        route_mfg = self.env.ref('mrp.route_warehouse0_manufacture').id
        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id
        delivery_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')]).ids
        receipt_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Receipts')]).ids

        mrp_planning_product = self.env['flsp.mrp.planning.line'].search([])
        for planning in mrp_planning_product:  ##delete not used
            planning.unlink()

        #calculating planning
        products_templates = self.env['product.template'].search([('type', '=', 'product')])
        for product_template in products_templates:
            lead_time = product_template.produce_delay

            if route_mfg not in product_template.route_ids.ids:
                continue
            product = self.env['product.product'].search([('product_tmpl_id', '=', product_template.id)])
            order_point = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', product.id)], limit=1)
            if order_point:
                min_qty = order_point.product_min_qty
                max_qty = order_point.product_max_qty
                multiple = order_point.qty_multiple
            else:
                min_qty = 0.0
                max_qty = 0.0
                multiple = 1
            mrp_planning_product = self.env['flsp.mrp.planning.line'].search([('product_tmpl_id', '=', product_template.id)])
            for planning in mrp_planning_product:  ##Clean the flag to delete later
                planning.calculated = False

            current_balance = product.qty_available

            open_moves = []
            # index  type, source,    doc,          picking_id, production_id, qty, date
            #         IN   Purchase   WH/IN/P0001       32          0           5    2020-01-01 00:00:00
            #        OUT   Sales      WH/OUT/P0001      33          0           8    2020-01-01 00:00:00
            # ******************* quantity coming up***************************
            # Purchase Orders
            if route_buy in product_template.route_ids.ids:
                open_receipts = self.env['stock.picking'].search(['&', '&', ('product_id', '=', product.id), ('state', 'not in', ['done', 'cancel', 'draft']),('picking_type_id', 'in', receipt_stock_type)])
                for receipt in open_receipts:
                    stock_move_product = self.env['stock.move'].search(['&', ('picking_id', '=', receipt.id), ('product_id', '=', product.id)])
                    total_moved = 0
                    for move in stock_move_product:
                        total_moved += move.product_uom_qty
                    open_moves.append([len(open_moves)+1,'In ', 'Purchase  ', receipt.origin, receipt.id, 0, total_moved, receipt.scheduled_date])
            # Manufacturing Orders
            if route_mfg in product_template.route_ids.ids:
                if consider_drafts:
                    production_orders = self.env['mrp.production'].search(['&', ('state', 'not in', ['done', 'cancel']), ('product_id', '=', product.id)])
                else:
                    production_orders = self.env['mrp.production'].search(['&', ('state', 'not in', ['done', 'cancel', 'draft']), ('product_id', '=', product.id)])
                for production in production_orders:
                    open_moves.append([len(open_moves)+1, 'In ', 'Production', production.name, 0, production.id, production.product_qty, production.date_planned_finished])

            # ******************* quantity going out ***************************
            #Sales Orders
            open_deliveries = self.env['stock.picking'].search(['&', '&', ('product_id', '=', product.id), ('state', 'not in', ['done', 'cancel', 'draft']), ('picking_type_id', 'in', delivery_stock_type)])
            for delivery in open_deliveries:
                stock_move_product = self.env['stock.move'].search(['&', ('picking_id', '=', delivery.id), ('product_id', '=', product.id)])
                total_moved = 0
                for move in stock_move_product:
                    total_moved += move.product_uom_qty
                open_moves.append([len(open_moves)+1, 'Out', 'Sale      ', delivery.origin, delivery.id, 0, total_moved, delivery.scheduled_date])

            #Manufacturing Orders
            if consider_drafts:
                production_orders = self.env['mrp.production'].search(['&', ('state', 'not in', ['done', 'cancel']), ('move_raw_ids.product_id', '=', product.id)])
            else:
                production_orders = self.env['mrp.production'].search(['&', ('state', 'not in', ['done', 'cancel', 'draft']), ('move_raw_ids.product_id', '=', product.id)])
            for production in production_orders:
                if production.origin:
                    open_moves.append([len(open_moves)+1, 'Out', 'Production', production.origin +"-"+ production.name, 0, production.id, production.product_qty, production.date_planned_finished])
                else:
                    open_moves.append([len(open_moves)+1, 'Out', 'Production', production.name, 0, production.id, production.product_qty, production.date_planned_finished])

            if len(open_moves) > 0:
                open_moves.sort(key=lambda l: l[7])
                open_moves_sorted = []
                for x in open_moves:
                    tmp = [len(open_moves_sorted)+1]
                    for y in x:
                        tmp.append(y)
                    open_moves_sorted.append(tmp)
                current_day = open_moves_sorted[0][8].date()
                last_day_moves = []
                suggested_qty = 0
                rationale = 'Initial Balance: ' + str(current_balance) + " on " + str(current_day)  + '<br/>'
                for x in open_moves_sorted:
                    rationale += "Movement: " + x[2] + " | Source: " + x[3] + " | Doc: " + x[4] + " | Qty: " + str(
                        x[7]) + " | Date: " + str(x[8].date()) + '<br/>'
                    if current_day != x[8].date():
                        #rationale = "Movement: " + x[1] + "source" + x[2] + str(x[8].date()) + "=" + str(x[7]) + '<br/>'
                        if current_balance-min_qty < 0.0:
                            suggested_qty = min_qty - current_balance
                            if (max_qty > 0.0) & ((suggested_qty+current_balance) < max_qty):
                                suggested_qty = max_qty
                            source = ''
                            desc_source = ''
                            picking_id = False
                            production_id = False
                            for y in last_day_moves:
                                if y[2] == 'Out':
                                    if source != '':
                                        source += ', '
                                    if desc_source != '':
                                        desc_source = 'Multiple orders'
                                    else:
                                        desc_source = y[3]
                                        picking_id = y[5]
                                        production_id = y[6]
                                    source += y[4]

                            #Checking multiple quantities
                            if multiple > 1:
                                if multiple > suggested_qty:
                                    suggested_qty += multiple-suggested_qty
                                else:
                                    if (suggested_qty % multiple) > 0:
                                        suggested_qty += multiple-(suggested_qty % multiple)

                            rationale += 'Balance on ' + str(current_day) + ' will be: ' + str(current_balance) + '<br/>'
                            rationale += 'Min qty =' + str(min_qty) + '<br/>'
                            rationale += 'Max qty =' + str(max_qty) + '<br/>'
                            rationale += 'Multiple qty =' + str(multiple) + '<br/>'
                            rationale += 'Lead time on product =' + str(lead_time) + ' days <br/>'
                            if lead_time == 0:
                                if not production_id:
                                    lead_time = standard_lead_time
                                    rationale += '-->Using direct demand lead time =' + str(lead_time) + ' days <br/>'
                                else:
                                    lead_time = indirect_lead_time
                                    rationale += '-->Using indirect demand lead time =' + str(lead_time) + ' days <br/>'

                            rationale += '* Planning for qty required =' + str(suggested_qty) + '<br/>'

                            self.create({'product_tmpl_id': product_template.id,
                                         'product_id': product.id,
                                         'description': product_template.name,
                                         'default_code': product_template.default_code,
                                         'suggested_qty': suggested_qty,
                                         'start_date': current_day + timedelta(days=-1 * lead_time),
                                         'deadline_date': current_day,
                                         'calculated': True,
                                         'stock_picking': picking_id,
                                         'production_id': production_id,
                                         'source_description': desc_source,
                                         'rationale': rationale,
                                         'source': source, })
                        current_balance += suggested_qty
                        current_day = x[8].date()
                        last_day_moves = []
                    if x[2] == 'Out':
                        current_balance -= x[7]
                        last_day_moves.append(x)
                    else:
                        current_balance += x[7]
                        last_day_moves.append(x)

                if len(last_day_moves) > 0:
                    current_day = x[8].date()
                    if current_balance - min_qty < 0:
                        suggested_qty = min_qty - current_balance
                        if (max_qty > 0.0) & ((suggested_qty+current_balance) < max_qty):
                            suggested_qty = max_qty
                        source = ''
                        desc_source = ''
                        picking_id = False
                        production_id = False
                        for y in last_day_moves:
                            if y[2] == 'Out':
                                if source != '':
                                    source += ', '
                                if desc_source != '':
                                    desc_source = 'Multiple orders'
                                else:
                                    desc_source = y[3]
                                    picking_id = y[5]
                                    production_id = y[6]
                                source += y[4]

                        #checking multiple quantities
                        if multiple > 1:
                            if multiple > suggested_qty:
                                suggested_qty += multiple - suggested_qty
                            else:
                                if (suggested_qty % multiple) > 0:
                                    suggested_qty += multiple - (suggested_qty % multiple)

                        rationale += 'Balance on ' + str(current_day) + ' will be: ' + str(current_balance) + '<br/>'
                        rationale += 'Min qty =' + str(min_qty) + '<br/>'
                        rationale += 'Max qty =' + str(max_qty) + '<br/>'
                        rationale += 'Multiple qty =' + str(multiple) + '<br/>'
                        rationale += 'Lead time on product =' + str(lead_time) + ' days <br/>'
                        if lead_time == 0:
                            if not production_id:
                                lead_time = standard_lead_time
                                rationale += '-->Using direct demand lead time =' + str(lead_time) + ' days <br/>'
                            else:
                                lead_time = indirect_lead_time
                                rationale += '-->Using indirect demand lead time =' + str(lead_time) + ' days <br/>'

                        rationale += '* Planning for Qty required =' + str(suggested_qty) + '<br/>'

                        self.create({'product_tmpl_id': product_template.id,
                                     'product_id': product.id,
                                     'description': product_template.name,
                                     'default_code': product_template.default_code,
                                     'suggested_qty': suggested_qty,
                                     'start_date': current_day + timedelta(days=-1 * lead_time),
                                     'deadline_date': current_day,
                                     'calculated': True,
                                     'stock_picking': picking_id,
                                     'production_id': production_id,
                                     'source_description': desc_source,
                                     'rationale' : rationale,
                                     'source': source, })

        return

    def execute_suggestion(self):
        for item in self:
            bom_id = self.env['mrp.bom'].search([('product_tmpl_id', '=', item.product_tmpl_id.id)], limit=1)
            if not bom_id:
                item.rationale += "<br/> |"
                item.rationale += "<br/> |"
                item.rationale += "<br/>A T T E N T I O N: "
                item.rationale += "<br/> **** The attempt to create MO has failed *** "
                item.rationale += "<br/> Product has no Bill of Materials."
                item.rationale += "<br/> User: " + self.env['res.users'].search([('id', '=', self._uid)]).name
                continue

            mo = self.env['mrp.production'].create({
                'product_id': item.product_id.id,
                'bom_id': bom_id.id,
                'product_uom_id': item.product_id.uom_id.id,
                'product_qty': item.suggested_qty,
                'date_planned_start': datetime.combine(item.start_date, datetime.now().time()),
                'date_planned_finished': datetime.combine(item.deadline_date, datetime.now().time()),
                'date_deadline': datetime.combine(item.deadline_date, datetime.now().time()),
                'origin': item.source,
            })


            list_move_raw = [(4, move.id) for move in mo.move_raw_ids.filtered(lambda m: not m.bom_line_id)]
            moves_raw_values = mo._get_moves_raw_values()
            move_raw_dict = {move.bom_line_id.id: move for move in mo.move_raw_ids.filtered(lambda m: m.bom_line_id)}
            for move_raw_values in moves_raw_values:
                if move_raw_values['bom_line_id'] in move_raw_dict:
                    # update existing entries
                    list_move_raw += [(1, move_raw_dict[move_raw_values['bom_line_id']].id, move_raw_values)]
                else:
                    # add new entries
                    list_move_raw += [(0, 0, move_raw_values)]
            mo.move_raw_ids = list_move_raw
            item.unlink()

        action = self.env.ref('mrp.mrp_production_action').read()[0]
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action
