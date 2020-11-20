# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api
from datetime import timedelta
from datetime import date

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

    def _flsp_calc_planning(self, calculate_sub_levels=False, standard_lead_time=1, standard_queue_time=1):
        route_mfg = self.env.ref('mrp.route_warehouse0_manufacture').id
        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id
        delivery_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')]).ids
        receipt_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Receipts')]).ids
        current_date = datetime.date.today()

        mrp_planning_product = self.env['flsp.mrp.planning.line'].search([])
        for planning in mrp_planning_product:  ##delete not used
            planning.unlink()

        print('------------->Calc planning')

        products_templates = self.env['product.template'].search([('type', '=', 'product')])
        for product_template in products_templates:
            if route_mfg not in product_template.route_ids.ids:
                continue
            product = self.env['product.product'].search([('product_tmpl_id', '=', product_template.id)])
            order_point = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', product.id)], limit=1)
            if order_point:
                min_qty = order_point.product_min_qty
                max_qty = order_point.product_max_qty
            else:
                min_qty = 0.0
                max_qty = 0.0
            mrp_planning_product = self.env['flsp.mrp.planning.line'].search([('product_tmpl_id', '=', product_template.id)])
            for planning in mrp_planning_product:  ##Clean the flag to delete later
                planning.calculated = False

            current_balance = product.qty_available

            open_moves = []
            # type, source, doc, picking_id, production_id, qty, date

            # ******************* quantity coming up***************************
            # Purchase Orders
            if route_buy in product_template.route_ids.ids:
                open_receipts = self.env['stock.picking'].search(['&', '&', ('product_id', '=', product.id), ('state', 'not in', ['done', 'cancel', 'draft']),('picking_type_id', 'in', receipt_stock_type)])
                for receipt in open_receipts:
                    stock_move_product = self.env['stock.move'].search(['&', ('picking_id', '=', receipt.id), ('product_id', '=', product.id)])
                    total_moved = 0
                    for move in stock_move_product:
                        total_moved += move.product_uom_qty
                    open_moves.append([len(open_moves)+1,'In', 'Purchase', receipt.origin, receipt.id, 0, total_moved, receipt.scheduled_date])
            # Manufacturing Orders
            if route_mfg in product_template.route_ids.ids:
                production_orders = self.env['mrp.production'].search(['&', ('state', 'not in', ['done', 'cancel']), ('product_id', '=', product.id)])
                for production in production_orders:
                    open_moves.append([len(open_moves)+1, 'In', 'Production', production.name, 0, production.id, production.product_qty, production.date_planned_finished])

                #open_stock_picking = self.env['stock.picking'].search(['&', '&', ('product_id', '=', product.id), ('state', 'not in', ['done', 'cancel', 'draft']), ('picking_type_id', 'in', delivery_stock_type)], order="scheduled_date")

            # ******************* quantity going out ***************************
            #Sales Orders
            open_deliveries = self.env['stock.picking'].search(['&', '&', ('product_id', '=', product.id), ('state', 'not in', ['done', 'cancel', 'draft']), ('picking_type_id', 'in', delivery_stock_type)])
            for delivery in open_deliveries:
                stock_move_product = self.env['stock.move'].search(['&', ('picking_id', '=', delivery.id), ('product_id', '=', product.id)])
                total_moved = 0
                for move in stock_move_product:
                    total_moved += move.product_uom_qty
                open_moves.append([len(open_moves)+1, 'Out', 'Sale', delivery.origin, delivery.id, 0, total_moved, delivery.scheduled_date])

            #Manufacturing Orders
            production_orders = self.env['mrp.production'].search(['&', ('state', 'not in', ['done', 'cancel']), ('move_raw_ids.product_id', '=', product.id)])
            for production in production_orders:
                open_moves.append([len(open_moves)+1, 'Out', 'Production', production.name, 0, production.id, production.product_qty, production.date_planned_finished])

            if len(open_moves) > 0:
                open_moves.sort(key=lambda l: l[7])
                open_moves_sorted = []
                for x in open_moves:
                    tmp = [len(open_moves_sorted)+1]
                    for y in x:
                        tmp.append(y)
                    open_moves_sorted.append(tmp)
                print('=========================================my list==============================')
                for x in open_moves_sorted:
                    print(x)
                print('*********************************** start calc for product: ' + product_template.name + ' balance: '+str(current_balance))
                current_day = open_moves_sorted[0][8].date()
                last_day_moves = []
                suggested_qty = 0
                for x in open_moves_sorted:
                    if current_day != x[8].date():
                        print('balance on ' + str(current_day) + ': ' + str(current_balance))
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

                            rationale = 'balance on ' + str(current_day) + ' will be: ' + str(current_balance) + '<br/>'
                            rationale += 'min qty =' + str(min_qty) + '<br/>'
                            rationale += 'max qty =' + str(max_qty) + '<br/>'
                            rationale += 'Qty required =' + str(suggested_qty) + '<br/>'

                            self.create({'product_tmpl_id': product_template.id,
                                         'product_id': product.id,
                                         'description': product_template.name,
                                         'default_code': product_template.default_code,
                                         'suggested_qty': suggested_qty,
                                         'start_date': current_day + timedelta(days=-1 * standard_lead_time),
                                         'deadline_date': current_day,
                                         'calculated': True,
                                         'stock_picking': picking_id,
                                         'production_id': production_id,
                                         'source_description': desc_source,
                                         'rationale': rationale,
                                         'source': source, })

                            print('Suggest to produce:' + str(suggested_qty))

                        for y in last_day_moves:
                            print(y)
                        current_day = x[8].date()
                        last_day_moves = []
                    if x[2] == 'Out':
                        current_balance -= x[7]
                    else:
                        current_balance += x[7]
                    last_day_moves.append(x)

                if len(last_day_moves) > 0:
                    current_day = x[8].date()
                    print('balance on ' + str(current_day) + ': ' + str(current_balance))
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

                            rationale = 'balance on ' + str(current_day) + ' will be: ' + str(current_balance) + '<br/>'
                            rationale += 'min qty =' + str(min_qty) + '<br/>'
                            rationale += 'max qty =' + str(max_qty) + '<br/>'
                            rationale += 'Qty required =' + str(suggested_qty) + '<br/>'

                        self.create({'product_tmpl_id': product_template.id,
                                     'product_id': product.id,
                                     'description': product_template.name,
                                     'default_code': product_template.default_code,
                                     'suggested_qty': suggested_qty,
                                     'start_date': current_day + timedelta(days=-1 * standard_lead_time),
                                     'deadline_date': current_day,
                                     'calculated': True,
                                     'stock_picking': picking_id,
                                     'production_id': production_id,
                                     'source_description': desc_source,
                                     'rationale' : rationale,
                                     'source': source, })
                        print('Suggest to produce:' + str(suggested_qty))
                    for y in last_day_moves:
                        print(y)

        return







        # Sales
        open_stock_picking = []
        product = 0
        for delivery in open_stock_picking:
            mrp_planning_product = self.env['flsp.mrp.planning.line'].search([('source', '=', delivery.origin)])
            stock_move_product = self.env['stock.move'].search(['&', ('picking_id', '=', delivery.id), ('product_id', '=', product_product.id)])
            total_transfer = 0
            for move in stock_move_product:
                total_transfer += move.product_uom_qty
            if mrp_planning_product:
                mrp_planning_product.product_qty = product.qty_available
                mrp_planning_product.suggested_qty = total_transfer
                mrp_planning_product.source = delivery.origin
                mrp_planning_product.calculated = True
                mrp_planning_product.start_date = delivery.scheduled_date + timedelta(days=-1*standard_lead_time)
                mrp_planning_product.deadline_date = delivery.scheduled_date + timedelta(days=-1)
                mrp_planning_product.source_description = 'Sales'
            else:
                mrp_planning_product.source = delivery.origin
            #rationale += self.rationale_delivery_doc(delivery)
        #rationale += '</table>'
        #rationale += self.generate_rationale()
        mrp_planning_product = self.env['flsp.mrp.planning.line'].search([('product_tmpl_id', '=', product.id)])
        for planning in mrp_planning_product:  ##delete not used
                planning.unlink()


    def rationale_header(self):
        ret_header = '''
                <tr>
                <td></td>
                <td colspan="30" style="border: 1px solid grey; text-align: center;" >November</td></tr>
                <tr>
                <td></td>
                <td style="border: 1px solid grey">1</td>
                <td style="border: 1px solid grey">2</td>
                <td style="border: 1px solid grey">3</td>
                <td style="border: 1px solid grey">4</td>
                <td style="border: 1px solid grey">5</td>
                <td style="border: 1px solid grey">6</td>
                <td style="border: 1px solid grey">7</td>
                <td style="border: 1px solid grey">8</td>
                <td style="border: 1px solid grey; background-color: #fafab0">9</td>
                <td style="border: 1px solid grey">10</td>
                <td style="border: 1px solid grey">11</td>
                <td style="border: 1px solid grey">12</td>
                <td style="border: 1px solid grey">13</td>
                <td style="border: 1px solid grey">14</td>
                <td style="border: 1px solid grey">15</td>
                <td style="border: 1px solid grey">16</td>
                <td style="border: 1px solid grey">17</td>
                <td style="border: 1px solid grey">18</td>
                <td style="border: 1px solid grey">19</td>
                <td style="border: 1px solid grey">20</td>
                <td style="border: 1px solid grey">21</td>
                <td style="border: 1px solid grey">22</td>
                <td style="border: 1px solid grey">23</td>
                <td style="border: 1px solid grey">24</td>
                <td style="border: 1px solid grey">25</td>
                <td style="border: 1px solid grey">26</td>
                <td style="border: 1px solid grey">27</td>
                <td style="border: 1px solid grey">28</td>
                <td style="border: 1px solid grey">29</td>
                <td style="border: 1px solid grey">30</td>
                </tr>
        '''
        return ret_header

    def rationale_delivery_doc(self, delivery):
        ret_value = '''
                <tr>
                <td>''' + delivery.origin + '''</td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey; background-color: #fafab0"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey; text-align: center; background-color: #fccfa9">5</td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                </tr>
        '''
        return ret_value
    def generate_rationale(self):
        ret_value = '''
            <table style="border-collapse: collapse">
                <tr>
                <td>MO0001</td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey; background-color: #fafab0"></td>
                <td colspan="8" style="border: 1px solid grey; text-align: center; background-color: #bedcfc">5</td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                </tr>
                <tr>
                <td>MO0003</td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey; background-color: #fafab0"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td colspan="8" style="border: 1px solid grey; text-align: center; background-color: #bedcfc">7</td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                </tr>
                <tr>
                    <td style="border: 2px solid black; text-align: center; color: grey ">Suggested</td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center; background-color: #fafab0"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td colspan="8" style="border: 2px solid black; text-align: center; background-color: #ecedee">8</td>
                    <td style="border: 2px solid black; text-align: center"></td>
                    <td style="border: 2px solid black; text-align: center"></td>
                </tr>
                <tr>
                <td>S00155</td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey; background-color: #fafab0"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey; text-align: center; background-color: #fccfa9">15</td>
                <td style="border: 1px solid grey"></td>
                </tr>
                <tr>
                <td>Quantity</td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey"></td>
                <td style="border: 1px solid grey; background-color: #fafab0">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">5</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">7</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                <td style="border: 1px solid grey">0</td>
                </tr>
            </table>

        '''
        return ret_value
