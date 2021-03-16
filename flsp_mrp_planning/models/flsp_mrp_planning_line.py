# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api
from datetime import timedelta
from datetime import datetime
from odoo.exceptions import UserError

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
    product_max_qty = fields.Float('Max. Qty', readonly=True)
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
    purchase_adjusted = fields.Float(string='Adjusted 2nd uom')
    purchase_suggested = fields.Float(String="Suggested 2nd uom", readonly=True, help="Quantity suggested to buy or produce.")

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

    stock_qty    = fields.Float(string='Stock Qty', readonly=True)
    wip_qty      = fields.Float(string='WIP Qty', readonly=True)
    vendor_id    = fields.Many2one('res.partner', string='Supplier')
    vendor_qty   = fields.Float(string='Quantity', readonly=True)
    vendor_price = fields.Float(string='Price', readonly=True)
    delay = fields.Integer(string="Delivery Lead Time")
    produce_delay = fields.Integer(string="Mfg Lead Time")
    required_by = fields.Date(String="Required by", readonly=True)
    balance = fields.Float(string='Balance', readonly=True)

    uom = fields.Many2one('uom.uom', 'Product Unit of Measure', readonly=True)
    purchase_uom = fields.Many2one('uom.uom', 'Purchase Unit of Measure', readonly=True)

    qty_month1 = fields.Float(string='January')
    qty_month2 = fields.Float(string='February')
    qty_month3 = fields.Float(string='March')
    qty_month4 = fields.Float(string='April')
    qty_month5 = fields.Float(string='May')
    qty_month6 = fields.Float(string='June')
    qty_month7 = fields.Float(string='July')
    qty_month8 = fields.Float(string='August')
    qty_month9 = fields.Float(string='September')
    qty_month10 = fields.Float(string='October')
    qty_month11 = fields.Float(string='November')
    qty_month12 = fields.Float(string='December')

    consumption_month1 = fields.Float(string='Consumption January')
    consumption_month2 = fields.Float(string='Consumption February')
    consumption_month3 = fields.Float(string='Consumption March')
    consumption_month4 = fields.Float(string='Consumption April')
    consumption_month5 = fields.Float(string='Consumption May')
    consumption_month6 = fields.Float(string='Consumption June')
    consumption_month7 = fields.Float(string='Consumption July')
    consumption_month8 = fields.Float(string='Consumption August')
    consumption_month9 = fields.Float(string='Consumption September')
    consumption_month10 = fields.Float(string='Consumption October')
    consumption_month11 = fields.Float(string='Consumption November')
    consumption_month12 = fields.Float(string='Consumption December')

    def name_get(self):
        return [(
            record.id,
            record.default_code
        ) for record in self]


    @api.onchange('adjusted_qty')
    def onchange_adjusted_qty(self):
        self.purchase_adjusted = self.product_id.uom_id._compute_quantity(self.adjusted_qty, self.product_id.uom_po_id)
        if self._origin.id:
            planning = self.env['flsp.mrp.planning.line'].search([('id', '=', self._origin.id)])
            if planning:
                planning.purchase_adjusted = self.product_id.uom_id._compute_quantity(self.adjusted_qty, self.product_id.uom_po_id)

    def _flsp_calc_planning(self, standard_lead_time=1, standard_queue_time=1, indirect_lead_time=1, consider_drafts=True, consider_wip=True, consider_forecast=True):

        current_date = datetime.now()
        required_by = current_date
        route_mfg = self.env.ref('mrp.route_warehouse0_manufacture').id
        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id

        delivery_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')]).ids
        receipt_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Receipts')]).ids

        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')], limit=1).parent_path
        if not pa_location:
            raise UserError('WIP Stock Location is missing')
        pa_wip_locations = self.env['stock.location'].search([('parent_path', 'like', pa_location+'%')]).ids
        if not pa_wip_locations:
            raise UserError('WIP Stock Location is missing')

        mrp_purchase_product = self.env['flsp.mrp.planning.line'].search([])
        for purchase in mrp_purchase_product:  ##delete not used
            purchase.unlink()

        # components within BOM
        # bom_components = self._get_flattened_totals(self.bom_id, self.product_qty)
        open_moves = []
        # index  type, source,     doc,          product_id,   qty,  uom   date                  level  lead time
        #         IN   Purchase    WH/IN/P0001       32          5   each  2020-01-01 00:00:00     1        1
        #         IN   Manufacture WH/MO/M0001       32          5   each  2020-01-01 00:00:00     1        1
        #        OUT   Sales       WH/OUT/P0001      33          8   each  2020-01-01 00:00:00     1        1
        #        OUT   Manufacture WH/MO/M0001       32          5   each  2020-01-01 00:00:00     1        1

        # *******************************************************************************
        # ***************************** Purchase Orders *********************************
        # *******************************************************************************
        open_receipts = self.env['stock.picking'].search(['&', ('state', 'not in', ['done', 'cancel', 'draft']),('picking_type_id', 'in', receipt_stock_type)])
        for receipt in open_receipts:
            stock_move_product = self.env['stock.move'].search([('picking_id', '=', receipt.id)])
            for move in stock_move_product:
                if route_mfg not in move.product_id.route_ids.ids:
                    continue
                open_moves.append([len(open_moves) + 1, 'In   ', 'Purchase',
                                   receipt.origin,
                                   move.product_id,
                                   move.product_uom_qty, move.product_uom,
                                   receipt.scheduled_date, 0, 0])
        # *******************************************************************************
        # ***************************** Sales Orders ************************************
        # *******************************************************************************
        open_deliveries = self.env['stock.picking'].search(['&', ('state', 'not in', ['done', 'cancel', 'draft']), ('picking_type_id', 'in', delivery_stock_type)])
        for delivery in open_deliveries:
            stock_move_product = self.env['stock.move'].search([('picking_id', '=', delivery.id)])
            for move in stock_move_product:
                if route_mfg not in move.product_id.route_ids.ids:
                    continue
                move_bom = False # self.env['mrp.bom'].search([('product_tmpl_id', '=', move.product_id.product_tmpl_id.id)], limit=1)
                if not move_bom:
                    open_moves.append([len(open_moves) + 1, 'Out  ', 'Sales   ',
                                       delivery.origin,
                                       move.product_id,
                                       move.product_uom_qty, move.product_uom,
                                       delivery.scheduled_date, 0, standard_lead_time ])
                else:
                    open_moves.append([len(open_moves) + 1, 'Out  ', 'Sales   ',
                                       delivery.origin,
                                       move.product_id,
                                       move.product_uom_qty, move.product_uom,
                                       delivery.scheduled_date, 0, standard_lead_time ])
                    move_components = self._get_flattened_totals(move_bom, move.product_uom_qty)
                    for prod in move_components:
                        if prod.type in ['service', 'consu']:
                            continue
                        if move_components[prod]['total'] <= 0:
                            continue
                        open_moves.append([len(open_moves) + 1, 'Out  ', 'Sales   ',
                                           delivery.origin,
                                           prod,
                                           move_components[prod]['total'], prod.uom_id.id,
                                           delivery.scheduled_date, move_components[prod]['level'], standard_lead_time+(indirect_lead_time*move_components[prod]['level'])])

        # *******************************************************************************
        # ************************ Manufacturing Orders *********************************
        # *******************************************************************************
        if consider_drafts:
            production_orders = self.env['mrp.production'].search([('state', 'not in', ['done', 'cancel'])])
        else:
            production_orders = self.env['mrp.production'].search([('state', 'not in', ['done', 'cancel', 'draft'])])
        for production in production_orders:
            move_components = self._get_flattened_totals(production.bom_id, production.product_qty)
            open_moves.append([len(open_moves) + 1, 'In   ', 'MO      ',
                               production.name,
                               production.product_id,
                               production.product_qty, production.product_id.uom_id.id,
                               production.date_planned_start, 0,
                               standard_lead_time + standard_lead_time])
            for prod in move_components:
                if move_components[prod]['level'] == 1:
                    open_moves.append([len(open_moves) + 1, 'In   ', 'MO      ',
                                       production.name,
                                       prod,
                                       move_components[prod]['total'], prod.uom_id.id,
                                       production.date_planned_start, move_components[prod]['level'], standard_lead_time+(move_components[prod]['level']*indirect_lead_time)])
                    continue
                if prod.type in ['service', 'consu']:
                    continue
                if move_components[prod]['total'] <= 0:
                    continue
                open_moves.append([len(open_moves) + 1, 'Out  ', 'MO      ',
                                   production.name,
                                   prod,
                                   move_components[prod]['total'], prod.uom_id.id,
                                   production.date_planned_start, move_components[prod]['level'], standard_lead_time+(indirect_lead_time*move_components[prod]['level'])])
        #print(open_moves)

        #for move in open_moves:
            #print(move[4].default_code+' - '+str(move[7])) ## Product + Date
            #print(move[4])  ## Product

        #open_moves.sort(key=lambda x: x[4].id) # Sort by product
        #open_moves.sort(key=lambda x: x[7])  # Sort by date
        open_moves.sort(key=lambda x: (x[4].id, x[7]))  # Sort by product and then date
        open_moves = self.calc_open_moves(open_moves, standard_lead_time)

        previous_product = ''
        for item in open_moves:
            product = item[4]
            if previous_product != product:
                balance = product.qty_available
            if item[1] == 'Out  ':
                balance -= item[5]
            else:
                balance += item[5]
            previous_product = product


        rationale = {}

        product = open_moves[0][4]
        rationale[product.id] = ''

        rationale[product] = "<pre>--------------------------------------------------------------------------------------------"
        rationale[product] += "<br/>                                        | Movement     "
        rationale[product] += "<br/>DATE        | QTY         |Balance      |Type |Source  |BOM Level|Mfg Lead time| Doc"
        rationale[product] += "<br/>------------|-------------|-------------|-----|--------|---------|-------------|-----------"
        current_balance = product.qty_available
        rationale[product] += '<br/>            |             | ' + '{0: <12.2f}|'.format(current_balance) + '     |        |         |             |Initial Balance'
        for item in open_moves:
            if product != item[4]:
                rationale[product] += "</pre>"
                product = item[4]
                rationale[product] = "<pre>--------------------------------------------------------------------------------------------"
                rationale[product] += "<br/>                                        | Movement     "
                rationale[product] += "<br/>DATE        | QTY         |Balance      |Type |Source  |BOM Level|Mfg Lead time| Doc"
                rationale[product] += "<br/>------------|-------------|-------------|-----|--------|---------|-------------|-----------"
                current_balance = product.qty_available
                rationale[product] += '<br/>            |             | ' + '{0: <12.2f}|'.format(current_balance) + '     |        |         |             |Initial Balance'
                if item[1] == 'Out  ':
                    current_balance -= item[5]
                else:
                    current_balance += item[5]
                rationale[product] += '<br/>' + item[7].strftime("%Y-%m-%d") + '  | ' + '{:<12.4f}|'.format(item[5]) + ' ' + '{0: <12.2f}|'.format(current_balance) + item[1] + '|' + item[2] + '|' + '{0: <9}|'.format(item[8]) + '{0: <13}|'.format(item[9]) + item[3]
            else:
                if item[1] == 'Out  ':
                    current_balance -= item[5]
                else:
                    current_balance += item[5]
                rationale[product] += '<br/>' + item[7].strftime("%Y-%m-%d") + '  | ' + '{:<12.4f}|'.format(item[5]) + ' ' + '{0: <12.2f}|'.format(current_balance) + item[1] + '|' + item[2] + '|' + '{0: <9}|'.format(item[8]) + '{0: <13}|'.format(item[9]) + item[3]
            product = item[4]

        if product:
            #print(product.name)
            rationale[product] += "</pre>"
            #print(rationale[product])

        for item in open_moves:
            product = item[4]
            if item[10]:
                purchase_line = self._include_prod(product, rationale[product], item[10], item[5], 0, item[7],consider_wip, False, False, standard_lead_time, indirect_lead_time)


        # ########################################
        # ### Other products without movements ###
        # ########################################
        products = self.env['product.product'].search(['&', ('type', '=', 'product'), ('route_ids', 'in', [route_mfg])])
        required_by = current_date
        for product in products:
            if product.flsp_backflush:
                continue
            purchase_planning = self.env['flsp.mrp.planning.line'].search([('product_id', '=', product.id)])
            if not purchase_planning:
                current_balance = False
                consumption = False
                suggested_qty = 0
                if product in rationale:
                    note = rationale[product]
                else:
                    note = 'No open movements - Product Selected based on Min qty.'
                purchase_line = self._include_prod(product, note, "min", suggested_qty, current_balance, required_by, consider_wip, consumption, False     , standard_lead_time, indirect_lead_time)

        # ########################################
        # ######## FORECAST   ####################
        # ########################################
        if consider_forecast:
            sales_forecast = self.env['flsp.sales.forecast'].search([])
            for forecast in sales_forecast:
                if forecast.product_id.type == 'product' and route_mfg in forecast.product_id.route_ids.ids:
                    product = forecast.product_id
                    current_balance = False
                    forecasted = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    consumption = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

                    for item in open_moves:
                        if product == item[4]:
                            if item[1] == 'Out  ':
                                if current_date.month == item[7].month:
                                    consumption[item[7].month] += item[5]

                    forecasted[1] = forecast.qty_month1
                    forecasted[2] = forecast.qty_month2
                    forecasted[3] = forecast.qty_month3
                    forecasted[4] = forecast.qty_month4
                    forecasted[5] = forecast.qty_month5
                    forecasted[6] = forecast.qty_month6
                    forecasted[7] = forecast.qty_month7
                    forecasted[8] = forecast.qty_month8
                    forecasted[9] = forecast.qty_month9
                    forecasted[10] = forecast.qty_month10
                    forecasted[11] = forecast.qty_month11
                    forecasted[12] = forecast.qty_month12

                    if product in rationale:
                        note = rationale[product]
                    else:
                        note = 'No open movements - Product Selected based on Min qty.'
                    purchase_line = self._include_prod(product, note, "forecast", 0, current_balance, current_date, consider_wip, consumption, forecasted, standard_lead_time, indirect_lead_time)

            purchase_planning = self.env['flsp.mrp.planning.line'].search([])
            months = ['', 'January         ', 'February        ', 'March           ', 'April           ',
                          'May             ', 'June            ', 'July            ', 'August          ',
                          'October         ', 'September       ', 'November        ', 'December        ']
            next_6_months = []
            key = current_date.month
            count = 1
            for month in months:
                if count >= 7:
                    break
                if key > 12:
                    key = 1
                next_6_months.append(months[key])
                key += 1
                count += 1
            for planning in purchase_planning:
                if planning.source != 'forecast':
                    continue
                rationale = "<pre>------------------------------------------------- Forecast ----------------------------------------------------<br/>"
                rationale += '        |'
                for month in next_6_months:
                    rationale += month + "|"
                rationale += "<br/>"
                key = current_date.month
                rationale += 'Forecast|'
                for month in next_6_months:
                    field_name = 'qty_month'+str(key)
                    rationale += '{0: <16.2f}|'.format(getattr(planning, field_name))
                    key += 1
                    if key > 12:
                        key = 1
                rationale += '<br/>Actual  |'
                key = current_date.month
                for month in next_6_months:
                    field_name = 'consumption_month'+str(key)
                    rationale += '{0: <16.2f}|'.format(getattr(planning, field_name))
                    key += 1
                    if key > 12:
                        key = 1
                rationale += '<br/>Diff    |'
                key = current_date.month
                for month in next_6_months:
                    field_name = 'qty_month'+str(key)
                    diff = getattr(planning, field_name)
                    field_name = 'consumption_month'+str(key)
                    diff -= getattr(planning, field_name)
                    rationale += '{0: <16.2f}|'.format(diff)
                    key += 1
                    if key > 12:
                        key = 1
                rationale += "<br/>---------------------------------------------------------------------------------------------------------------<br/>"
                months_to_consider = int(planning.produce_delay/31)
                value_to_consider = 0
                if months_to_consider >= 1:
                    months_to_consider += 1
                if months_to_consider <= 0:
                    months_to_consider = 1
                rationale += '-------'
                key = current_date.month
                for current_month in range(7):
                    if current_month < months_to_consider:
                        field_name = 'qty_month' + str(key)
                        diff = getattr(planning, field_name)
                        field_name = 'consumption_month' + str(key)
                        diff -= getattr(planning, field_name)
                        if diff > 0:
                            value_to_consider += diff
                    if current_month+1 == months_to_consider:
                        rationale += '>|'+'{0: <16.2f}'.format(value_to_consider)
                    elif current_month < months_to_consider:
                        if months_to_consider >= 6 and current_month > 5:
                            rationale += '>|' + '{0: <16.2f}'.format(value_to_consider)
                        else:
                            rationale += '-----------------'
                    else:
                        rationale += '                 '
                    key += 1
                    if key > 12:
                        key = 1
                rationale += '</pre>'

                # Current balance calculated
                original_balance = 0
                product = planning.product_id
                current_balance = product.qty_available
                for item in open_moves:
                    if product == item[4]:
                        if item[1] == 'Out  ':
                            current_balance -= item[5]
                        else:
                            current_balance += item[5]

                original_balance = current_balance
                suggested_qty = 0
                if current_balance < value_to_consider:
                    suggested_qty = value_to_consider - current_balance

                # Checking Minimal Quantity
                if suggested_qty > 0:
                    if suggested_qty < planning.product_min_qty:
                        if suggested_qty < 0:
                            suggested_qty = planning.product_min_qty - suggested_qty
                        else:
                            suggested_qty = planning.product_min_qty

                # checking multiple quantities
                if suggested_qty > 0:
                    if planning.qty_multiple > 1:
                        if planning.qty_multiple > suggested_qty:
                            suggested_qty += planning.qty_multiple - suggested_qty
                        else:
                            if (suggested_qty % planning.qty_multiple) > 0:
                                suggested_qty += planning.qty_multiple - (suggested_qty % planning.qty_multiple)
                if consider_wip:
                    current_balance = planning.product_qty
                else:
                    current_balance = planning.product_qty - planning.wip_qty

                if value_to_consider > 0:
                    planning.suggested_qty = suggested_qty
                    planning.adjusted_qty = suggested_qty
                    planning.purchase_adjusted = planning.product_id.uom_id._compute_quantity(suggested_qty, planning.product_id.uom_po_id)
                    planning.purchase_suggested = planning.product_id.uom_id._compute_quantity(suggested_qty, planning.product_id.uom_po_id)
                planning.rationale += rationale

            # if not purchase_planning:
            #    print(forecast.product_id.name)
            # else:
            #    print('product already in there.......')

        return
        #open_moves.append(False) ## append the last item to print when the for ends.
        #consumption = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


        #print('---> After sorting')
        #for move in open_moves:
            #print(move[4].default_code+' - '+str(move[7])) ## Product + Date
            #print(move[7]) ## Date
            #print(move[4])  ## Product




        # First Item
        previous_date = False
        source = ""
        rationale = False
        product = False
        suggested_qty = False
        current_balance = False
        bom_level = False
        for item in open_moves:
            if item:
                if route_mfg not in item[4].route_ids.ids:
                    continue
            rationale = "<pre>--------------------------------------------------------------------------------------------"
            rationale += "<br/>                                        | Movement     "
            rationale += "<br/>DATE        | QTY         |Balance      |Type |Source  |BOM Level|Mfg Lead time| Doc"
            rationale += "<br/>------------|-------------|-------------|-----|--------|---------|-------------|-----------"
            product = open_moves[1][4]
            previous_date = open_moves[1][7].date()
            source = item[3]
            order_point = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', product.id)], limit=1)
            if order_point:
                min_qty = order_point.product_min_qty
                max_qty = order_point.product_max_qty
                multiple = order_point.qty_multiple
            else:
                min_qty = 0.0
                max_qty = 0.0
                multiple = 1
            current_balance = product.qty_available
            pa_wip_qty = 0
            stock_quant = self.env['stock.quant'].search(
                ['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', product.id)])
            for stock_lin in stock_quant:
                pa_wip_qty += stock_lin.quantity

            if consider_wip:
                current_balance = product.qty_available
            else:
                current_balance = product.qty_available - pa_wip_qty
            rationale += '<br/>            |             | '+'{0: <12.2f}|'.format(current_balance)+'     |        |         |             |Initial Balance'
            bom_level = item[8]
            suggested_qty = item[5]
            required_by = item[7]
            rationale += '<br/>' + item[7].strftime("%Y-%m-%d") + '  | ' + '{:<12.4f}|'.format(item[5]) + ' ' + '{0: <12.2f}|'.format(current_balance) + item[1] + '|' + item[2] + '|' + '{0: <9}|'.format(item[8]) + '{0: <13}|'.format(item[9]) + item[3]
            break

        count_item=0
        for item in open_moves:
            new_prod = True
            new_date = True
            #print(source+"--------------------------------------")
            if item:
                #print("--->" + str(item[7]) + "  - " + item[3] + " // " + item[4].name + " -> " + str(item[5]))
                if route_mfg not in item[4].route_ids.ids:
                    continue
                new_prod = (item[4] != product)
                previous_date = item[7].date()
                new_date = (item[7].date() != previous_date)
            if new_prod or new_date:
                rationale += "</pre>"
                #print(suggested_qty)
                purchase_line = self._include_prod(product, rationale, source, suggested_qty, current_balance, required_by, consider_wip, consumption, False,     standard_lead_time, indirect_lead_time)
                if purchase_line:
                    purchase_line.level_bom = bom_level
                bom_level = 0
                suggested_qty = 0
                consumption = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

                if not item:
                    break
                product = item[4]
                rationale = "<pre>--------------------------------------------------------------------------------------------"
                rationale += "<br/>                                        | Movement     "
                rationale += "<br/>DATE        | QTY         |Balance      |Type |Source  |BOM Level|Mfg Lead time| Doc"
                rationale += "<br/>------------|-------------|-------------|-----|--------|---------|-------------|-----------"
                required_by = False
                pa_wip_qty = 0
                stock_quant = self.env['stock.quant'].search(
                    ['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', product.id)])
                for stock_lin in stock_quant:
                    pa_wip_qty += stock_lin.quantity

                if consider_wip:
                    current_balance = product.qty_available
                else:
                    current_balance = product.qty_available - pa_wip_qty
                rationale += '<br/>            |             | ' + '{0: <12.2f}|'.format(current_balance) + '     |        |         |             |Initial Balance'

            if item:
                if item[1] == 'Out  ':
                    current_balance -= item[5]
                    # Do not account the past
                    if current_date < item[7]:
                        consumption[item[7].month] += item[5]
                else:
                    current_balance += item[5]
                if not required_by:
                    required_by = item[7]
                rationale += '<br/>'+item[7].strftime("%Y-%m-%d")+'  | '+'{:<12.4f}|'.format(item[5])+' ' + '{0: <12.2f}|'.format(current_balance) + item[1]+'|'+item[2]+'|'+'{0: <9}|'.format(item[8])+'{0: <13}|'.format(item[9])+item[3]
                product = item[4]
                if bom_level < item[8]:
                    bom_level = item[8]
                if new_prod or new_date or (count_item<=2):
                    suggested_qty = item[5]
                    source = item[3]
                    if consider_wip:
                        current_balance = product.qty_available
                    else:
                        current_balance = product.qty_available - pa_wip_qty
                    rationale = "<pre>--------------------------------------------------------------------------------------------"
                    rationale += "<br/>                                        | Movement     "
                    rationale += "<br/>DATE        | QTY         |Balance      |Type |Source  |BOM Level|Mfg Lead time| Doc"
                    rationale += "<br/>------------|-------------|-------------|-----|--------|---------|-------------|-----------"
                    rationale += '<br/>            |             | ' + '{0: <12.2f}|'.format(current_balance) + '     |        |         |             |Initial Balance'
                    if item[1] == 'Out  ':
                        current_balance -= item[5]
                        # Do not account the past
                        if current_date < item[7]:
                            consumption[item[7].month] += item[5]
                    else:
                        current_balance += item[5]
                    rationale += '<br/>' + item[7].strftime("%Y-%m-%d") + '  | ' + '{:<12.4f}|'.format(item[5]) + ' ' + '{0: <12.2f}|'.format(current_balance) + item[1] + '|' + item[2] + '|' + '{0: <9}|'.format(item[8]) + '{0: <13}|'.format(item[9]) + item[3]
                else:
                    suggested_qty += item[5]
                    source += item[3]
                count_item += 1

        # ########################################
        # ### Other products without movements ###
        # ########################################
        products = self.env['product.product'].search(['&', ('type', '=', 'product'), ('route_ids', 'in', [route_buy])])
        required_by = current_date
        for product in products:
            if route_mfg not in product.route_ids.ids:
                continue
            if product.flsp_backflush:
                continue
            purchase_planning = self.env['flsp.mrp.planning.line'].search([('product_id', '=', product.id)])
            if not purchase_planning:
                current_balance = False
                suggested_qty = 0
                rationale = 'No open movements - Product Selected based on Min qty.'
                purchase_line = self._include_prod(product, rationale, "min", suggested_qty, current_balance, required_by, consider_wip, consumption, False     , standard_lead_time, indirect_lead_time)
        # ########################################
        # ######## FORECAST   ####################
        # ########################################
        if consider_forecast:
            sales_forecast = self.env['flsp.sales.forecast'].search([])
            for forecast in sales_forecast:
                forecast_bom = False # self.env['mrp.bom'].search([('product_tmpl_id', '=', forecast.product_id.product_tmpl_id.id)], limit=1)
                if forecast_bom:
                    if forecast.product_id.type == 'product' and route_mfg in forecast.product_id.route_ids.ids:
                        purchase_planning = self.env['flsp.mrp.planning.line'].search([('product_id', '=', forecast.product_id.id)],limit=1)
                        if not purchase_planning:
                            product = forecast.product_id
                            current_balance = False
                            rationale = 'No movement. Product Selected based on Forecast.'
                            forecasted = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                            forecasted[1] = forecast.qty_month1
                            forecasted[2] = forecast.qty_month2
                            forecasted[3] = forecast.qty_month3
                            forecasted[4] = forecast.qty_month4
                            forecasted[5] = forecast.qty_month5
                            forecasted[6] = forecast.qty_month6
                            forecasted[7] = forecast.qty_month7
                            forecasted[8] = forecast.qty_month8
                            forecasted[9] = forecast.qty_month9
                            forecasted[10] = forecast.qty_month10
                            forecasted[11] = forecast.qty_month11
                            forecasted[12] = forecast.qty_month12
                            suggested_qty = 0
                            purchase_line = self._include_prod(product, rationale, "forecast", suggested_qty, current_balance, current_date, consider_wip, False, forecasted, standard_lead_time, indirect_lead_time)
                        else:
                            purchase_planning.qty_month1 += forecast.qty_month1
                            purchase_planning.qty_month2 += forecast.qty_month2
                            purchase_planning.qty_month3 += forecast.qty_month3
                            purchase_planning.qty_month4 += forecast.qty_month4
                            purchase_planning.qty_month5 += forecast.qty_month5
                            purchase_planning.qty_month6 += forecast.qty_month6
                            purchase_planning.qty_month7 += forecast.qty_month7
                            purchase_planning.qty_month8 += forecast.qty_month8
                            purchase_planning.qty_month9 += forecast.qty_month9
                            purchase_planning.qty_month10 += forecast.qty_month10
                            purchase_planning.qty_month11 += forecast.qty_month11
                            purchase_planning.qty_month12 += forecast.qty_month12
                    forecast_components = self._get_flattened_totals(forecast_bom, 1)
                    for component in forecast_components:
                        if route_mfg not in component.route_ids.ids:
                            continue
                        if component.flsp_backflush:
                            continue
                        purchase_planning = self.env['flsp.mrp.planning.line'].search([('product_id', '=', component.id)],limit=1)
                        if not purchase_planning:
                            product = component
                            rationale = 'No open movements - Product Selected based on Forecast.'
                            forecasted = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                            forecasted[1] = forecast.qty_month1*forecast_components[component]['total']
                            forecasted[2] = forecast.qty_month2*forecast_components[component]['total']
                            forecasted[3] = forecast.qty_month3*forecast_components[component]['total']
                            forecasted[4] = forecast.qty_month4*forecast_components[component]['total']
                            forecasted[5] = forecast.qty_month5*forecast_components[component]['total']
                            forecasted[6] = forecast.qty_month6*forecast_components[component]['total']
                            forecasted[7] = forecast.qty_month7*forecast_components[component]['total']
                            forecasted[8] = forecast.qty_month8*forecast_components[component]['total']
                            forecasted[9] = forecast.qty_month9*forecast_components[component]['total']
                            forecasted[10] = forecast.qty_month10*forecast_components[component]['total']
                            forecasted[11] = forecast.qty_month11*forecast_components[component]['total']
                            forecasted[12] = forecast.qty_month12*forecast_components[component]['total']
                            purchase_line = self._include_prod(product, rationale, "forecast", 0 ,False, current_date, consider_wip, False, forecasted, standard_lead_time, indirect_lead_time)
                        else:
                            purchase_planning.qty_month1 += forecast.qty_month1*forecast_components[component]['total']
                            purchase_planning.qty_month2 += forecast.qty_month2*forecast_components[component]['total']
                            purchase_planning.qty_month3 += forecast.qty_month3*forecast_components[component]['total']
                            purchase_planning.qty_month4 += forecast.qty_month4*forecast_components[component]['total']
                            purchase_planning.qty_month5 += forecast.qty_month5*forecast_components[component]['total']
                            purchase_planning.qty_month6 += forecast.qty_month6*forecast_components[component]['total']
                            purchase_planning.qty_month7 += forecast.qty_month7*forecast_components[component]['total']
                            purchase_planning.qty_month8 += forecast.qty_month8*forecast_components[component]['total']
                            purchase_planning.qty_month9 += forecast.qty_month9*forecast_components[component]['total']
                            purchase_planning.qty_month10 += forecast.qty_month10*forecast_components[component]['total']
                            purchase_planning.qty_month11 += forecast.qty_month11*forecast_components[component]['total']
                            purchase_planning.qty_month12 += forecast.qty_month12*forecast_components[component]['total']
                else:
                    #print(' No no bom:---------------- ')
                    if forecast.product_id.type == 'product' and route_mfg in forecast.product_id.route_ids.ids:
                        purchase_planning = self.env['flsp.mrp.planning.line'].search([('product_id', '=', forecast.product_id.id)],limit=1)
                        if not purchase_planning:
                            product = forecast.product_id
                            current_balance = False
                            rationale = 'No movement. Product Selected based on Forecast.'
                            forecasted = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                            forecasted[1] = forecast.qty_month1
                            forecasted[2] = forecast.qty_month2
                            forecasted[3] = forecast.qty_month3
                            forecasted[4] = forecast.qty_month4
                            forecasted[5] = forecast.qty_month5
                            forecasted[6] = forecast.qty_month6
                            forecasted[7] = forecast.qty_month7
                            forecasted[8] = forecast.qty_month8
                            forecasted[9] = forecast.qty_month9
                            forecasted[10] = forecast.qty_month10
                            forecasted[11] = forecast.qty_month11
                            forecasted[12] = forecast.qty_month12
                            purchase_line = self._include_prod(product, rationale, "forecast", 0, current_balance, current_date, consider_wip, False, forecasted, standard_lead_time, indirect_lead_time)
                        else:
                            purchase_planning.qty_month1 += forecast.qty_month1
                            purchase_planning.qty_month2 += forecast.qty_month2
                            purchase_planning.qty_month3 += forecast.qty_month3
                            purchase_planning.qty_month4 += forecast.qty_month4
                            purchase_planning.qty_month5 += forecast.qty_month5
                            purchase_planning.qty_month6 += forecast.qty_month6
                            purchase_planning.qty_month7 += forecast.qty_month7
                            purchase_planning.qty_month8 += forecast.qty_month8
                            purchase_planning.qty_month9 += forecast.qty_month9
                            purchase_planning.qty_month10 += forecast.qty_month10
                            purchase_planning.qty_month11 += forecast.qty_month11
                            purchase_planning.qty_month12 += forecast.qty_month12

            purchase_planning = self.env['flsp.mrp.planning.line'].search([])
            months = ['', 'January         ', 'February        ', 'March           ', 'April           ',
                          'May             ', 'June            ', 'July            ', 'August          ',
                          'October         ', 'September       ', 'November        ', 'December        ']
            next_6_months = []
            key = current_date.month
            count = 1
            for month in months:
                if count >= 7:
                    break
                if key > 12:
                    key = 1
                next_6_months.append(months[key])
                key += 1
                count += 1
            for planning in purchase_planning:
                rationale = "<pre>------------------------------------------------- Forecast ----------------------------------------------------<br/>"
                rationale += '        |'
                for month in next_6_months:
                    rationale += month + "|"
                rationale += "<br/>"
                key = current_date.month
                rationale += 'Forecast|'
                for month in next_6_months:
                    field_name = 'qty_month'+str(key)
                    rationale += '{0: <16.2f}|'.format(getattr(planning, field_name))
                    key += 1
                    if key > 12:
                        key = 1
                rationale += '<br/>Actual  |'
                key = current_date.month
                for month in next_6_months:
                    field_name = 'consumption_month'+str(key)
                    rationale += '{0: <16.2f}|'.format(getattr(planning, field_name))
                    key += 1
                    if key > 12:
                        key = 1
                rationale += '<br/>Diff    |'
                key = current_date.month
                for month in next_6_months:
                    field_name = 'qty_month'+str(key)
                    diff = getattr(planning, field_name)
                    field_name = 'consumption_month'+str(key)
                    diff -= getattr(planning, field_name)
                    rationale += '{0: <16.2f}|'.format(diff)
                    key += 1
                    if key > 12:
                        key = 1
                rationale += "<br/>---------------------------------------------------------------------------------------------------------------<br/>"
                months_to_consider = int(planning.produce_delay/31)
                value_to_consider = 0
                if months_to_consider >= 1:
                    months_to_consider += 1
                if months_to_consider <= 0:
                    months_to_consider = 1
                rationale += '-------'
                key = current_date.month
                for current_month in range(7):
                    if current_month < months_to_consider:
                        field_name = 'qty_month' + str(key)
                        diff = getattr(planning, field_name)
                        field_name = 'consumption_month' + str(key)
                        diff -= getattr(planning, field_name)
                        if diff > 0:
                            value_to_consider += diff
                    if current_month+1 == months_to_consider:
                        rationale += '>|'+'{0: <16.2f}'.format(value_to_consider)
                    elif current_month < months_to_consider:
                        if months_to_consider >= 6 and current_month > 5:
                            rationale += '>|' + '{0: <16.2f}'.format(value_to_consider)
                        else:
                            rationale += '-----------------'
                    else:
                        rationale += '                 '
                    key += 1
                    if key > 12:
                        key = 1
                rationale += '</pre>'
                current_balance = planning.balance - value_to_consider
                # Checking Minimal Quantity
                if current_balance < 0:
                    suggested_qty = planning.product_min_qty - current_balance
                else:
                    if current_balance < planning.product_min_qty:
                        suggested_qty = planning.product_min_qty - current_balance
                    else:
                        suggested_qty = 0

                # Checking supplier quantity:
                #if suggested_qty > 0 and planning.vendor_qty > 0:
                #    if suggested_qty < planning.vendor_qty:
                #            suggested_qty = planning.vendor_qty

                # checking multiple quantities
                if planning.qty_multiple > 1:
                    if planning.qty_multiple > suggested_qty:
                        suggested_qty += planning.qty_multiple - suggested_qty
                    else:
                        if (suggested_qty % planning.qty_multiple) > 0:
                            suggested_qty += planning.qty_multiple - (suggested_qty % planning.qty_multiple)
                if consider_wip:
                    current_balance = planning.product_qty
                else:
                    current_balance = planning.product_qty - planning.wip_qty

                if suggested_qty > 0:
                    planning.suggested_qty = suggested_qty
                    planning.adjusted_qty = suggested_qty
                    planning.purchase_adjusted = planning.product_id.uom_id._compute_quantity(suggested_qty, planning.product_id.uom_po_id)
                    planning.purchase_suggested = planning.product_id.uom_id._compute_quantity(suggested_qty, planning.product_id.uom_po_id)
                planning.rationale += rationale
            # if not purchase_planning:
            #    print(forecast.product_id.name)
            # else:
            #    print('product already in there.......')

        return


    def _get_flattened_totals(self, bom, factor=1, totals=None, level=None):
        """Calculate the **unitary** product requirements of flattened BOM.
        *Unit* means that the requirements are computed for one unit of the
        default UoM of the product.
        :returns: dict: keys are components and values are aggregated quantity
        in the product default UoM.
        """
        if level is None:
            level = 0
        if totals is None:
            totals = {}
        factor /= bom.product_uom_id._compute_quantity(
            bom.product_qty, bom.product_tmpl_id.uom_id, round=False
        )
        for line in bom.bom_line_ids:
            sub_bom = bom._bom_find(product=line.product_id)
            if sub_bom:
                if line.product_id.product_tmpl_id.flsp_backflush:
                    new_factor = factor * line.product_uom_id._compute_quantity(
                        line.product_qty, line.product_id.uom_id, round=False
                    )
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
                        ), 'level': level, 'bom': sub_bom.code}
                    new_factor = factor * line.product_uom_id._compute_quantity(
                        line.product_qty, line.product_id.uom_id, round=False
                    )

                level += 1
                self._get_flattened_totals(sub_bom, new_factor, totals, level)
                level -= 1
        return totals

    def _include_prod(self, product, rationale, source, suggested_qty, balance, required_by, consider_wip, consumption=False, forecast=False, standard_lead_time=1, indirect_lead_time=1):

        if not consumption:
            consumption = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        if not forecast:
            forecast = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        total_forecast = 0
        for item in forecast:
            total_forecast += item

        ret = False
        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')], limit=1).parent_path
        if not pa_location:
            raise UserError('WIP Stock Location is missing')
        pa_wip_locations = self.env['stock.location'].search([('parent_path', 'like', pa_location+'%')]).ids
        if not pa_wip_locations:
            raise UserError('WIP Stock Location is missing')

        pa_wip_qty = 0
        stock_quant = self.env['stock.quant'].search(
            ['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', product.id)])
        for stock_lin in stock_quant:
            pa_wip_qty += stock_lin.quantity

        if not balance:
            current_balance = product.qty_available
            balance = current_balance
        else:
            current_balance = balance

        prod_vendor = self.env['product.supplierinfo'].search([('product_tmpl_id', '=', product.product_tmpl_id.id)],limit=1)
        order_point = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', product.id)], limit=1)
        if order_point:
            min_qty = order_point.product_min_qty
            max_qty = order_point.product_max_qty
            multiple = order_point.qty_multiple
        else:
            min_qty = 0.0
            max_qty = 0.0
            multiple = 1

        if suggested_qty <= 0:
            # Minimal quantity:
            if current_balance < 0:
                suggested_qty = min_qty - current_balance
            else:
                if current_balance < min_qty:
                    suggested_qty = min_qty - current_balance
                # else:
                    # suggested_qty = 0
        # Checking supplier quantity:
        #if prod_vendor:
        #    if suggested_qty > 0 and prod_vendor.min_qty > 0:
        #        if suggested_qty < prod_vendor.min_qty:
        #            suggested_qty = prod_vendor.min_qty

        # checking multiple quantities
        if multiple > 1:
            if multiple > suggested_qty:
                suggested_qty += multiple - suggested_qty
            else:
                if (suggested_qty % multiple) > 0:
                    suggested_qty += multiple - (suggested_qty % multiple)
        # Checking mfg lead time:
        if not required_by:
            required_by = datetime.now()
            if product.produce_delay and product.produce_delay > 0:
                required_by = required_by - timedelta(days=product.produce_delay)
            else:
                required_by = required_by - timedelta(days=standard_lead_time)

        if suggested_qty+total_forecast > 0 or source=='forecast':

            ret = self.create({'product_tmpl_id': product.product_tmpl_id.id,
                         'product_id': product.id,
                         'description': product.product_tmpl_id.name,
                         'default_code': product.product_tmpl_id.default_code,
                         'suggested_qty': suggested_qty,
                         'adjusted_qty': suggested_qty,
                         'purchase_adjusted': product.uom_id._compute_quantity(suggested_qty,product.uom_po_id),
                         'purchase_suggested': product.uom_id._compute_quantity(suggested_qty,product.uom_po_id),
                         'uom': product.uom_id.id,
                         'purchase_uom': product.uom_po_id.id,
                         'calculated': True,
                         'product_qty': product.qty_available,
                         'product_min_qty': min_qty,
                         'product_max_qty': max_qty,
                         'qty_multiple': multiple,
                         'vendor_id': prod_vendor.name.id,
                         'vendor_qty': prod_vendor.min_qty,
                         'delay': prod_vendor.delay,
                         'produce_delay': product.produce_delay,
                         'vendor_price': prod_vendor.price,
                         'stock_qty': product.qty_available - pa_wip_qty,
                         'wip_qty': pa_wip_qty,
                         'rationale': rationale,
                         'required_by': required_by,
                         'start_date': required_by,
                         'deadline_date': required_by,
                         'consumption_month1': consumption[1],
                         'consumption_month2': consumption[2],
                         'consumption_month3': consumption[3],
                         'consumption_month4': consumption[4],
                         'consumption_month5': consumption[5],
                         'consumption_month6': consumption[6],
                         'consumption_month7': consumption[7],
                         'consumption_month8': consumption[8],
                         'consumption_month9': consumption[9],
                         'consumption_month10': consumption[10],
                         'consumption_month11': consumption[11],
                         'consumption_month12': consumption[12],
                         'qty_month1': forecast[1],
                         'qty_month2': forecast[2],
                         'qty_month3': forecast[3],
                         'qty_month4': forecast[4],
                         'qty_month5': forecast[5],
                         'qty_month6': forecast[6],
                         'qty_month7': forecast[7],
                         'qty_month8': forecast[8],
                         'qty_month9': forecast[9],
                         'qty_month10': forecast[10],
                         'qty_month11': forecast[11],
                         'qty_month12': forecast[12],
                         'balance': balance,
                         'source': source, })
        return ret

    def execute_suggestion(self):
        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')], limit=1)
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
                'date_planned_start': datetime.combine(item.required_by, datetime.now().time()),
                'date_planned_finished': datetime.combine(item.required_by, datetime.now().time()),
                'date_deadline': datetime.combine(item.required_by, datetime.now().time()),
                'location_src_id': pa_location.id,
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

    def calc_open_moves(self, open_moves, standard_lead_time):
        new_open_moves = []
        previous_product = ''
        for line in open_moves:
            product = line[4]
            order_point = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', product.id)], limit=1)
            if order_point:
                min_qty = order_point.product_min_qty
                max_qty = order_point.product_max_qty
                multiple = order_point.qty_multiple
            else:
                min_qty = 0.0
                max_qty = 0.0
                multiple = 1
            if previous_product != product:
                balance = product.qty_available
            if line[1] == 'Out  ':
                balance -= line[5]
            else:
                balance += line[5]
            previous_product = product
            if balance-min_qty < 0:
                suggested = (balance - min_qty)*(-1)
                # checking multiple quantities
                if multiple > 1:
                    if multiple > suggested:
                        suggested += multiple - suggested
                    else:
                        if (suggested % multiple) > 0:
                            suggested += multiple - (suggested % multiple)

                # Checking mfg lead time:
                required_by = line[7]
                if product.produce_delay and product.produce_delay > 0:
                    required_by = required_by - timedelta(days=product.produce_delay)
                else:
                    required_by = required_by - timedelta(days=standard_lead_time)

                new_open_moves.append([len(new_open_moves) + 1, 'In   ', 'MO      ',
                                   "Suggested quantity source: "+line[3],
                                   product,
                                   suggested, product.uom_id.id,
                                   required_by, 0, 14, line[3]])
                balance = min_qty


            tmp = []
            first = True
            for item in line:
                if first:
                    tmp.append(len(new_open_moves) + 1)
                    first = False
                else:
                    tmp.append(item)
            tmp.append('')
            new_open_moves.append(tmp)

        new_open_moves.sort(key=lambda x: (x[4].id, x[7]))  # Sort by product and then date

        return new_open_moves
