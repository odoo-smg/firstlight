# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api
from datetime import timedelta
from datetime import datetime
from odoo.exceptions import UserError

class FlspMrppurchaseLine(models.Model):
    _name = 'flsp.mrp.purchase.line'
    _description = 'FLSP MRP purchase Line'

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
            planning = self.env['flsp.mrp.purchase.line'].search([('id', '=', self._origin.id)])
            if planning:
                planning.purchase_adjusted = self.product_id.uom_id._compute_quantity(self.adjusted_qty, self.product_id.uom_po_id)

    def _flsp_calc_purchase(self, standard_lead_time=1, standard_queue_time=1, indirect_lead_time=1, consider_drafts=True, consider_wip=True, consider_forecast=True):
        current_date = datetime.now()
        required_by = current_date
        route_mfg = self.env.ref('mrp.route_warehouse0_manufacture').id
        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id

        delivery_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')]).ids
        receipt_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Receipts')]).ids

        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')]).parent_path
        if not pa_location:
            raise UserError('WIP Stock Location is missing')
        pa_wip_locations = self.env['stock.location'].search([('parent_path', 'like', pa_location+'%')]).ids
        if not pa_wip_locations:
            raise UserError('WIP Stock Location is missing')

        mrp_purchase_product = self.env['flsp.mrp.purchase.line'].search([])
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
                move_bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', move.product_id.product_tmpl_id.id)], limit=1)
                if not move_bom:
                    open_moves.append([len(open_moves) + 1, 'Out  ', 'Sales   ',
                                       receipt.origin,
                                       move.product_id,
                                       move.product_uom_qty, move.product_uom,
                                       receipt.scheduled_date, 0, standard_lead_time ])
                else:
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
        open_moves.append(False) ## append the last item to print when the for ends.
        consumption = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        #print('---> After sorting')
        #for move in open_moves:
            #print(move[4].default_code+' - '+str(move[7])) ## Product + Date
            #print(move[7]) ## Date
            #print(move[4])  ## Product

        # First Item
        for item in open_moves:
            if item:
                if route_buy not in item[4].route_ids.ids:
                    continue
            rationale = "<pre>--------------------------------------------------------------------------------------------"
            rationale += "<br/>                                        | Movement     "
            rationale += "<br/>DATE        | QTY         |Balance      |Type |Source  |BOM Level|Mfg Lead time| Doc"
            rationale += "<br/>------------|-------------|-------------|-----|--------|---------|-------------|-----------"
            product = open_moves[1][4]
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
            required_by = False
            break

        for item in open_moves:
            new_prod = True
            if item:
                if route_buy not in item[4].route_ids.ids:
                    continue
                new_prod = (item[4] != product)
            if new_prod:
                rationale += "</pre>"
                purchase_line = self._include_prod(product, rationale, current_balance, required_by, consider_wip, consumption)
                if purchase_line:
                    purchase_line.level_bom = bom_level
                bom_level = 0
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
                    if current_balance < 0:
                        required_by = item[7]
                rationale += '<br/>'+item[7].strftime("%Y-%m-%d")+'  | '+'{:<12.4f}|'.format(item[5])+' ' + '{0: <12.2f}|'.format(current_balance) + item[1]+'|'+item[2]+'|'+'{0: <9}|'.format(item[8])+'{0: <13}|'.format(item[9])+item[3]
                product = item[4]
                if bom_level < item[8]:
                    bom_level = item[8]


        # ########################################
        # ### Other products without movements ###
        # ########################################
        products = self.env['product.product'].search(['&', ('type', '=', 'product'), ('route_ids', 'in', [route_buy])])
        required_by = current_date
        for product in products:
            purchase_planning = self.env['flsp.mrp.purchase.line'].search([('product_id', '=', product.id)])
            if not purchase_planning:
                current_balance = False
                rationale = 'No open movements - Product Selected based on Min qty.'
                purchase_line = self._include_prod(product, rationale, current_balance, required_by, consider_wip, consumption)

        # ########################################
        # ######## FORECAST   ####################
        # ########################################
        if consider_forecast:
            sales_forecast = self.env['flsp.sales.forecast'].search([])
            for forecast in sales_forecast:
                forecast_bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', forecast.product_id.product_tmpl_id.id)], limit=1)
                if forecast_bom:
                    forecast_components = self._get_flattened_totals(forecast_bom, 1)
                    for component in forecast_components:
                        purchase_planning = self.env['flsp.mrp.purchase.line'].search([('product_id', '=', component.id)],limit=1)
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
                            purchase_line = self._include_prod(product, rationale, False, current_date, consider_wip, False, forecasted)
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
                    if forecast.product_id.type == 'product' and route_buy in forecast.product_id.route_ids.ids:
                        purchase_planning = self.env['flsp.mrp.purchase.line'].search([('product_id', '=', forecast.product_id.id)],limit=1)
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
                            purchase_line = self._include_prod(product, rationale, current_balance, current_date, consider_wip, False, forecasted)
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

            purchase_planning = self.env['flsp.mrp.purchase.line'].search([])
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
                months_to_consider = int(planning.delay/31)
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
                if suggested_qty > 0 and planning.vendor_qty > 0:
                    if suggested_qty < planning.vendor_qty:
                            suggested_qty = planning.vendor_qty
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
                if suggested_qty > current_balance:
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

    def execute_suggestion(self):

        new_po = False
        ordered_by_vendor = []
        item_to_buy = []
        item_to_unlink = []

        for each in self:
            ordered_by_vendor.append([each, each.vendor_id.id])
        ordered_by_vendor.sort(key=lambda x: x[1])
        vendor = ordered_by_vendor[0][0].vendor_id

        for product in ordered_by_vendor:
            if vendor != product[0].vendor_id:
                if vendor:
                    new_po = self.env['purchase.order'].create({'partner_id': vendor.id,
                                                                'currency_id': self.env.company.currency_id.id,
                                                                'date_order': datetime.now(),
                                                                'order_line': item_to_buy})
                    if new_po:
                        for item in item_to_unlink:
                            item.unlink()
                item_to_buy = []
                item_to_unlink = []
            if product[0].vendor_id:
                item = product[0]
                item_to_buy.append(
                    (0, 0, {'product_id': item.product_id.id,
                            'name': item.product_tmpl_id.name,
                            'product_qty': item.purchase_adjusted,
                            'product_uom': item.purchase_uom.id,
                            'price_unit': item.vendor_price,
                            'date_planned': datetime.now()}))
                item_to_unlink.append(product[0])
            else:
                product[0].rationale += "</br> ***** PO not created. Please inform the Vendor in the Product."
            vendor = product[0].vendor_id

        if vendor:
            new_po = self.env['purchase.order'].create({'partner_id': vendor.id,
                                                        'currency_id': self.env.company.currency_id.id,
                                                        'date_order': datetime.now(),
                                                        'order_line': item_to_buy})
            if new_po:
                for item in item_to_unlink:
                    item.unlink()

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
                if not line.product_id.product_tmpl_id.flsp_backflush:
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

    def _include_prod(self, product, rationale, balance, required_by, consider_wip, consumption=False, forecast=False):

        if not consumption:
            consumption = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        if not forecast:
            forecast = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        total_forecast = 0
        for item in forecast:
            total_forecast += item

        ret = False
        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')]).parent_path
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
            if consider_wip:
                current_balance = product.qty_available
            else:
                current_balance = product.qty_available - pa_wip_qty
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

        # Minimal quantity:
        if current_balance < 0:
            suggested_qty = min_qty - current_balance
        else:
            if current_balance < min_qty:
                suggested_qty = min_qty - current_balance
            else:
                suggested_qty = 0
        # Checking supplier quantity:
        if prod_vendor:
            if suggested_qty > 0 and prod_vendor.min_qty > 0:
                if suggested_qty < prod_vendor.min_qty:
                    suggested_qty = prod_vendor.min_qty
        # checking multiple quantities
        if multiple > 1:
            if multiple > suggested_qty:
                suggested_qty += multiple - suggested_qty
            else:
                if (suggested_qty % multiple) > 0:
                    suggested_qty += multiple - (suggested_qty % multiple)
        # Checking Vendor lead time:
        if prod_vendor:
            if prod_vendor.delay and prod_vendor.delay > 0:
                if not required_by:
                    required_by = datetime.now()
                required_by = required_by - timedelta(days=prod_vendor.delay)

        if suggested_qty+total_forecast > 0:

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
                         'vendor_price': prod_vendor.price,
                         'stock_qty': product.qty_available - pa_wip_qty,
                         'wip_qty': pa_wip_qty,
                         'rationale': rationale,
                         'required_by': required_by,
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
                         'source': 'source', })
        return ret