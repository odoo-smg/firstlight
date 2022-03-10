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
    reserved = fields.Float(string='Qty Reserved', readonly=True)
    reserved_wip = fields.Float(string='Qty Reserved WIP', readonly=True)
    qty_mo = fields.Float(string='Qty of Draft MO', readonly=True)
    curr_outs = fields.Float(String="Demand", readonly=True,
                             help="Includes all confirmed sales orders and manufacturing orders")
    curr_ins = fields.Float(String="Replenishment", readonly=True,
                            help="Includes all confirmed purchase orders and manufacturing orders")
    average_use = fields.Float(String="Avg Use", readonly=True, help="Average usage of the past 3 months.")
    month1_use = fields.Float(String="2020-06 Usage", readonly=True, help="Total usage of last month.")
    month2_use = fields.Float(String="2020-05 Usage", readonly=True, help="Total usage of 2 months ago.")
    month3_use = fields.Float(String="2020-04 Usage", readonly=True, help="Total usage of 3 months ago.")
    suggested_qty = fields.Float(String="Suggested Qty", readonly=True, help="Quantity suggested to buy or produce.")
    adjusted_qty = fields.Float(String="Adjusted Qty", help="Adjust the quantity to be executed.")
    purchase_adjusted = fields.Float(string='Adjusted 2nd uom')
    purchase_suggested = fields.Float(String="Suggested 2nd uom", readonly=True,
                                      help="Quantity suggested to buy or produce.")
    po_qty = fields.Float(string='Qty Open PO')
    rfq_qty = fields.Float(string='Qty RFQ')

    qty_rfq = fields.Float(String="RFQ Qty", readonly=True, help="Total Quantity of Requests for Quotation.")
    level_bom = fields.Integer(String="BOM Level", readonly=True, help="Position of the product inside of a BOM.")
    route_buy = fields.Selection([('buy', 'To Buy'), ('na', 'Non Applicable'), ], string='To Buy', readonly=True)
    route_mfg = fields.Selection([('mfg', 'To Manufacture'), ('na', 'Non Applicable'), ], string='To Produce',
                                 readonly=True)
    state = fields.Selection([
        ('buy', 'To Buy'),
        ('ok', 'No Action'),
        ('po', 'Confirm PO'),
        ('mo', 'Confirm MO'),
        ('mfg', 'To Manufacture'),
    ], string='State', readonly=True)
    type = fields.Char(string='Type', readonly=True)
    start_date = fields.Date(String="Start Date", readonly=True)
    deadline_date = fields.Date(String="Deadline", readonly=True)
    rationale = fields.Html(string='Rationale')
    source = fields.Char(string='Source')
    source_description = fields.Char(string='Source Description')
    calculated = fields.Boolean('Calculated Flag')

    stock_qty = fields.Float(string='Stock Qty', readonly=True)
    wip_qty = fields.Float(string='WIP Qty', readonly=True)
    vendor_id = fields.Many2one('res.partner', string='Supplier')
    vendor_qty = fields.Float(string='Quantity', readonly=True)
    vendor_price = fields.Float(string='Unit Price', readonly=True)
    delay = fields.Integer(string="Delivery Lead Time")
    required_by = fields.Date(String="Required by", readonly=True)
    balance = fields.Float(string='Balance', readonly=True)
    late_delivery = fields.Float(string='Balance', readonly=True)
    total_price = fields.Float(string='Total Price', readonly=True)

    balance_neg = fields.Float(string='Negative Balance', readonly=True)
    negative_by = fields.Date(String="Negative by", readonly=True)

    avg_per_sbs = fields.Float(string='Avg per SBS', readonly=True)
    avg_per_ssa = fields.Float(string='Avg per SA', readonly=True)

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

    six_month_forecast = fields.Float(string='6 Months Forecast')
    twelve_month_forecast = fields.Float(string='12 Months Forecast')

    six_month_actual = fields.Float(string='6 Months Actual')
    twelve_month_actual = fields.Float(string='12 Months Actual')

    open_demand = fields.Float(string='Open Demand')

    active = fields.Boolean(default=True)

    new_update = fields.Boolean(default=False)


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
                planning.purchase_adjusted = self.product_id.uom_id._compute_quantity(self.adjusted_qty,
                                                                                      self.product_id.uom_po_id)

    def _flsp_calc_purchase(self, supplier_lead_time, standard_lead_time=14, standard_queue_time=1, indirect_lead_time=1,
                            consider_drafts=True, consider_wip=True, consider_forecast=True, consider_mo=False, consider_so=True, consider_reserved=False):
        current_date = datetime.now()
        required_by = current_date
        route_mfg = self.env.ref('mrp.route_warehouse0_manufacture').id
        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id

        delivery_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')]).ids
        receipt_stock_type = self.env['stock.picking.type'].search([('name', '=', 'Receipts')]).ids

        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')]).parent_path
        if not pa_location:
            raise UserError('WIP Stock Location is missing')
        pa_wip_locations = self.env['stock.location'].search([('parent_path', 'like', pa_location + '%')]).ids
        if not pa_wip_locations:
            raise UserError('WIP Stock Location is missing')
        stock_location = self.env['stock.location'].search([('complete_name', '=', 'WH/Stock')]).parent_path
        if not stock_location:
            raise UserError('Stock Location is missing')
        wh_stock_locations = self.env['stock.location'].search([('parent_path', 'like', stock_location + '%')]).ids
        if not wh_stock_locations:
            raise UserError('Stock Location is missing')

        mrp_purchase_product = self.env['flsp.mrp.purchase.line'].search(['|',('active', '=', True),('active', '=', False)])

        for planning in mrp_purchase_product:  ##delete not used
            if planning.active:
                planning.active = False
            else:
                planning.unlink()

        # components within BOM
        # bom_components = self._get_flattened_totals(self.bom_id, self.product_qty)
        open_moves = []
        # index  type, source,     doc,          product_id,   qty,  uom   date                  level  lead time  avg-sbs avg-ssa
        #         IN   Purchase    WH/IN/P0001       32          5   each  2020-01-01 00:00:00     1        1         99     99
        #         IN   Manufacture WH/MO/M0001       32          5   each  2020-01-01 00:00:00     1        1         99     99
        #        OUT   Sales       WH/OUT/P0001      33          8   each  2020-01-01 00:00:00     1        1         99     99
        #        OUT   Manufacture WH/MO/M0001       32          5   each  2020-01-01 00:00:00     1        1         99     99

        # *******************************************************************************
        # ***************************** Purchase Orders *********************************
        # *******************************************************************************
        open_receipts = self.env['stock.picking'].search(
            ['&', ('state', 'not in', ['done', 'cancel', 'draft']), ('picking_type_id', 'in', receipt_stock_type)])
        for receipt in open_receipts:
            stock_move_product = self.env['stock.move'].search([('picking_id', '=', receipt.id)])
            for move in stock_move_product:
                if receipt.origin:
                    doc = (receipt.origin + '                 ')[0:17]
                else:
                    doc = '                 '
                open_moves.append([len(open_moves) + 1, 'In   ', 'Purchase',
                                   doc,
                                   move.product_id,
                                   move.product_uom_qty, move.product_uom,
                                   move.date_expected, 0, 0, 0, 0])
        # *******************************************************************************
        # ***************************** Sales Orders ************************************
        # *******************************************************************************
        if consider_so:
            open_deliveries = self.env['stock.picking'].search(
                ['&', ('state', 'not in', ['done', 'cancel', 'draft']), ('picking_type_id', 'in', delivery_stock_type)])
            for delivery in open_deliveries:
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
                        open_moves.append([len(open_moves) + 1, 'Out  ', 'Sales   ',
                                           doc,
                                           move.product_id,
                                           move.product_uom_qty, move.product_uom,
                                           receipt.scheduled_date, 0, standard_lead_time, avg_per_sbs, avg_per_ssa])
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
                            open_moves.append([len(open_moves) + 1, 'Out  ', 'Sales   ',
                                               doc,
                                               prod,
                                               move_components[prod]['total'], prod.uom_id.id,
                                               delivery.scheduled_date, move_components[prod]['level'],
                                               standard_lead_time + (indirect_lead_time * move_components[prod]['level']), avg_per_sbs, avg_per_ssa])
        # *******************************************************************************
        # ************************ Manufacturing Orders *********************************
        # *******************************************************************************
        if consider_mo:
            if consider_drafts:
                production_orders = self.env['mrp.production'].search([('state', 'not in', ['done', 'cancel'])])
            else:
                production_orders = self.env['mrp.production'].search([('state', 'not in', ['done', 'cancel', 'draft'])])
            for production in production_orders:
                move_components = self._get_flattened_totals(production.bom_id, production.product_qty, {}, 0,True)

                for prod in move_components:
                    if move_components[prod]['level'] == 1:
                        open_moves.append([len(open_moves) + 1, 'In   ', 'MO      ',
                                           production.name,
                                           prod,
                                           move_components[prod]['total'], prod.uom_id.id,
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
                    open_moves.append([len(open_moves) + 1, 'Out  ', 'MO      ',
                                       doc,
                                       prod,
                                       move_components[prod]['total'], prod.uom_id.id,
                                       production.date_planned_start, move_components[prod]['level'],
                                       standard_lead_time + (indirect_lead_time * move_components[prod]['level']), 0, 0])
        # print(open_moves)

        # for move in open_moves:
        # print(move[4].default_code+' - '+str(move[7])) ## Product + Date
        # print(move[4])  ## Product

        # open_moves.sort(key=lambda x: x[4].id) # Sort by product
        # open_moves.sort(key=lambda x: x[7])  # Sort by date
        open_moves.sort(key=lambda x: (x[4].id, x[7]))  # Sort by product and then date
        open_moves.append(False)  ## append the last item to print when the for ends.
        consumption = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # print('---> After sorting')
        # for move in open_moves:
        # print(move[4].default_code+' - '+str(move[7])) ## Product + Date
        # print(move[7]) ## Date
        # print(move[4])  ## Product
        po_qty = 0
        rfq_qty = 0
        balance_neg = 0
        negative_by = False
        avg_per_sbs = 0
        avg_per_ssa = 0
        late_delivery = 0
        open_demand = 0

        # First Item
        for item in open_moves:
            if item:
                postpone = False
                if item[4].flsp_start_buy:
                    if item[4].flsp_start_buy > date.today():
                        postpone = True
                if postpone or route_buy not in item[4].route_ids.ids:
                    continue
            rationale = "<pre>-----------------------------------------------------------------------------------------------------------------"
            rationale += "<br/>                                        | Movement                                               |  AVG"
            rationale += "<br/>DATE        | QTY         |Balance      |Type |Source  |BOM Level|Mfg Lead time| Doc             | SBS  | SA   |"
            rationale += "<br/>------------|-------------|-------------|-----|--------|---------|-------------|-----------------|------|------|"
            if item:
                product = item[4]
            order_point = self.env['stock.warehouse.orderpoint'].search(
                ['&', ('product_id', '=', product.id), ('location_id', 'in', wh_stock_locations)], limit=1)
            if order_point:
                min_qty = order_point.product_min_qty
                max_qty = order_point.product_max_qty
                multiple = order_point.qty_multiple
            else:
                min_qty = 0.0
                max_qty = 0.0
                multiple = 1
            current_balance = product.qty_available
            late_delivery = 0
            pa_wip_qty = 0
            stock_quant = self.env['stock.quant'].search(
                ['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', product.id)])
            for stock_lin in stock_quant:
                pa_wip_qty += stock_lin.quantity

            stock_quant = self.env['stock.quant'].search(
                ['&', ('product_id', '=', product.id), ('location_id', 'in', pa_wip_locations)])
            stock_reserverd = 0
            wip_reserverd = 0
            for each in stock_quant:
                wip_reserverd += each.reserved_quantity
            stock_quant = self.env['stock.quant'].search(
                ['&', ('product_id', '=', product.id), ('location_id', 'not in', pa_wip_locations)])
            for each in stock_quant:
                stock_reserverd += each.reserved_quantity

            if consider_wip:
                if consider_reserved:
                    current_balance = product.qty_available
                else:
                    current_balance = product.qty_available - stock_reserverd
            else:
                if consider_reserved:
                    if not product.flsp_is_wip_stock:
                        current_balance = product.qty_available - pa_wip_qty
                    else:
                        current_balance = product.qty_available
                else:
                    if not product.flsp_is_wip_stock:
                        current_balance = product.qty_available - pa_wip_qty - wip_reserverd
                    else:
                        current_balance = product.qty_available - wip_reserverd
            rationale += '<br/>            |             | ' + '{0: <12.2f}|'.format(
                current_balance) + '     |        |         |             |Initial Balance  |      |      |'
            bom_level = item[8]
            required_by = False
            break

        for item in open_moves:
            new_prod = True
            if item:
                postpone = False
                if item[4].flsp_start_buy:
                    if item[4].flsp_start_buy > date.today():
                        postpone = True
                if postpone or route_buy not in item[4].route_ids.ids:
                    continue
                new_prod = (item[4] != product)
            if new_prod:
                rationale += "</pre>"
                purchase_line = self._include_prod(supplier_lead_time, product, rationale, current_balance, required_by, late_delivery, consider_wip, balance_neg, negative_by, avg_per_sbs, avg_per_ssa,
                                                   consumption, False, po_qty, open_demand, consider_reserved)
                #    _include_prod(self, supplier_lead_time, product, rationale, balance, required_by, late_delivery, consider_wip, balance_neg, negative_by, avg_per_sbs, avg_per_ssa, consumption=False, forecast=False, po_qty=0.0, open_demand=0.0, consider_reserved=False):


                if purchase_line:
                    purchase_line.level_bom = bom_level
                bom_level = 0
                consumption = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                po_qty = 0
                late_delivery = 0
                open_demand = 0

                if not item:
                    break
                product = item[4]
                rationale = "<pre>-----------------------------------------------------------------------------------------------------------------"
                rationale += "<br/>                                        | Movement                                               |  AVG"
                rationale += "<br/>DATE        | QTY         |Balance      |Type |Source  |BOM Level|Mfg Lead time| Doc             | SBS  | SA   |"
                rationale += "<br/>------------|-------------|-------------|-----|--------|---------|-------------|-----------------|------|------|"
                required_by = False
                negative_by = False
                avg_per_sbs = 0
                avg_per_ssa = 0
                balance_neg = 0
                pa_wip_qty = 0
                stock_quant = self.env['stock.quant'].search(
                    ['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', product.id)])
                for stock_lin in stock_quant:
                    pa_wip_qty += stock_lin.quantity

                stock_quant = self.env['stock.quant'].search(
                    ['&', ('product_id', '=', product.id), ('location_id', 'in', pa_wip_locations)])
                stock_reserverd = 0
                wip_reserverd = 0
                for each in stock_quant:
                    wip_reserverd += each.reserved_quantity
                stock_quant = self.env['stock.quant'].search(
                    ['&', ('product_id', '=', product.id), ('location_id', 'not in', pa_wip_locations)])
                for each in stock_quant:
                    stock_reserverd += each.reserved_quantity

                if consider_wip:
                    if consider_reserved:
                        current_balance = product.qty_available
                    else:
                        current_balance = product.qty_available - stock_reserverd
                else:
                    if consider_reserved:
                        if not product.flsp_is_wip_stock:
                            current_balance = product.qty_available - pa_wip_qty
                        else:
                            current_balance = product.qty_available
                    else:
                        if not product.flsp_is_wip_stock:
                            current_balance = product.qty_available - pa_wip_qty - wip_reserverd
                        else:
                            current_balance = product.qty_available - wip_reserverd
                rationale += '<br/>            |             | ' + '{0: <12.2f}|'.format(
                    current_balance) + '     |        |         |             |Initial Balance  |      |      |'
            if item:
                if item[1] == 'Out  ':
                    current_balance -= item[5]
                    # Do not account the past
                    if current_date < item[7]:
                        consumption[item[7].month] += item[5]
                    else:
                        late_delivery += item[5]
                    open_demand += item[5]
                else:
                    current_balance += item[5]
                if not required_by:
                    if current_balance < 0:
                        balance_neg = current_balance
                        negative_by = item[7]
                        required_by = item[7]
                if not item[3]:
                    item[3] = ''
                rationale += '<br/>' + item[7].strftime("%Y-%m-%d") + '  | ' + '{:<12.4f}|'.format(
                    item[5]) + ' ' + '{0: <12.2f}|'.format(current_balance) + item[1] + '|' + item[
                                 2] + '|' + '{0: <9}|'.format(item[8]) + '{0: <13}|'.format(item[9]) + item[3]+'|'+'{0:<6.2f}|'.format(item[10]) +'{0:<6.2f}|'.format(item[11])
                if item[10] > 0:
                    avg_per_sbs = (avg_per_sbs+item[10])/2
                if item[11] > 0:
                    avg_per_ssa = (avg_per_ssa+item[11])/2

                if item[2] == "Purchase":
                    po_qty = po_qty + item[5]

                product = item[4]
                if bom_level < item[8]:
                    bom_level = item[8]

        # ########################################
        # ### Other products without movements ###
        # ########################################
        balance_neg = 0
        negative_by = False
        products = self.env['product.product'].search(['&', ('type', '=', 'product'), ('route_ids', 'in', [route_buy])])
        required_by = current_date
        for product in products:
            if product.flsp_start_buy:
                if product.flsp_start_buy > date.today():
                    continue

            purchase_planning = self.env['flsp.mrp.purchase.line'].search([('product_id', '=', product.id)])
            if not purchase_planning:
                current_balance = False
                rationale = 'No open movements - Product Selected based on Min qty.'
                late_delivery = 0
                purchase_line = self._include_prod(supplier_lead_time, product, rationale, current_balance, required_by, late_delivery, consider_wip, balance_neg, negative_by, 0, 0,  consumption, False, 0, 0, consider_reserved)
                #              _include_prod(self, supplier_lead_time, product, rationale, balance,         required_by, late_delivery, consider_wip, balance_neg, negative_by, avg_per_sbs, avg_per_ssa, consumption=False, forecast=False, po_qty=0.0, open_demand=0.0, consider_reserved=False):


        # ########################################
        # ######## FORECAST   ####################
        # ########################################
        if consider_forecast:
            balance_neg = 0
            negative_by = False
            sales_forecast = self.env['flsp.sales.forecast'].search([])
            for forecast in sales_forecast:
                forecast_bom = self.env['mrp.bom'].search(
                    [('product_tmpl_id', '=', forecast.product_id.product_tmpl_id.id)], limit=1)
                if forecast_bom:
                    forecast_components = self._get_flattened_totals(forecast_bom, 1)
                    for component in forecast_components:
                        if route_buy not in component.route_ids.ids:
                            continue
                        if product.flsp_start_buy:
                            if product.flsp_start_buy > date.today():
                                continue

                        purchase_planning = self.env['flsp.mrp.purchase.line'].search(
                            [('product_id', '=', component.id)], limit=1)
                        if not purchase_planning:
                            product = component
                            rationale = 'No open movements - Product Selected based on Forecast.'
                            forecasted = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                            forecasted[1] = forecast.qty_month1 * forecast_components[component]['total']
                            forecasted[2] = forecast.qty_month2 * forecast_components[component]['total']
                            forecasted[3] = forecast.qty_month3 * forecast_components[component]['total']
                            forecasted[4] = forecast.qty_month4 * forecast_components[component]['total']
                            forecasted[5] = forecast.qty_month5 * forecast_components[component]['total']
                            forecasted[6] = forecast.qty_month6 * forecast_components[component]['total']
                            forecasted[7] = forecast.qty_month7 * forecast_components[component]['total']
                            forecasted[8] = forecast.qty_month8 * forecast_components[component]['total']
                            forecasted[9] = forecast.qty_month9 * forecast_components[component]['total']
                            forecasted[10] = forecast.qty_month10 * forecast_components[component]['total']
                            forecasted[11] = forecast.qty_month11 * forecast_components[component]['total']
                            forecasted[12] = forecast.qty_month12 * forecast_components[component]['total']
                            late_delivery = 0
                            purchase_line = self._include_prod(supplier_lead_time, product, rationale, False, current_date, late_delivery, consider_wip, balance_neg, negative_by, 0, 0,
                                                               False, forecasted, 0, 0, consider_reserved)
                            #   include_prod(self, supplier_lead_time, product, rationale, balance,         required_by, late_delivery, consider_wip, balance_neg, negative_by, avg_per_sbs, avg_per_ssa, consumption=False, forecast=False, po_qty=0.0, open_demand=0.0, consider_reserved=False):

                        else:
                            purchase_planning.qty_month1 += forecast.qty_month1 * forecast_components[component][
                                'total']
                            purchase_planning.qty_month2 += forecast.qty_month2 * forecast_components[component][
                                'total']
                            purchase_planning.qty_month3 += forecast.qty_month3 * forecast_components[component][
                                'total']
                            purchase_planning.qty_month4 += forecast.qty_month4 * forecast_components[component][
                                'total']
                            purchase_planning.qty_month5 += forecast.qty_month5 * forecast_components[component][
                                'total']
                            purchase_planning.qty_month6 += forecast.qty_month6 * forecast_components[component][
                                'total']
                            purchase_planning.qty_month7 += forecast.qty_month7 * forecast_components[component][
                                'total']
                            purchase_planning.qty_month8 += forecast.qty_month8 * forecast_components[component][
                                'total']
                            purchase_planning.qty_month9 += forecast.qty_month9 * forecast_components[component][
                                'total']
                            purchase_planning.qty_month10 += forecast.qty_month10 * forecast_components[component][
                                'total']
                            purchase_planning.qty_month11 += forecast.qty_month11 * forecast_components[component][
                                'total']
                            purchase_planning.qty_month12 += forecast.qty_month12 * forecast_components[component][
                                'total']
                else:
                    not_postpone = True
                    if forecast.product_id.flsp_start_buy:
                        if forecast.product_id.flsp_start_buy > date.today():
                            not_postpone = False
                    if not_postpone and forecast.product_id.type == 'product' and route_buy in forecast.product_id.route_ids.ids:

                        purchase_planning = self.env['flsp.mrp.purchase.line'].search(
                            [('product_id', '=', forecast.product_id.id)], limit=1)
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
                            late_delivery = 0
                            purchase_line = self._include_prod(supplier_lead_time, product, rationale, current_balance, current_date, late_delivery,
                                                               consider_wip, balance_neg, negative_by, 0, 0, False, forecasted, 0, 0, consider_reserved)
                            #    include_prod(self, supplier_lead_time, product, rationale, balance,         required_by, late_delivery, consider_wip, balance_neg, negative_by, avg_per_sbs, avg_per_ssa, consumption=False, forecast=False, po_qty=0.0, open_demand=0.0, consider_reserved=False):


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
                      'September       ', 'October         ', 'November        ', 'December        ']
            next_6_months = []
            key = current_date.month
            count = 1
            for month in months:
                if count > 12:
                    break
                if key > 12:
                    key = 1
                next_6_months.append(months[key])
                key += 1
                count += 1
            for planning in purchase_planning:
                six_month_forecast = 0
                rationale = "<pre>------------------------------------------------- Forecast ----------------------------------------------------<br/>"
                rationale += '        |'
                for month in next_6_months:
                    rationale += month + "|"
                rationale += "<br/>"
                key = current_date.month
                rationale += 'Forecast|'
                count_to_six=0
                for month in next_6_months:
                    field_name = 'qty_month' + str(key)
                    rationale += '{0: <16.2f}|'.format(getattr(planning, field_name))
                    if count_to_six < 6:
                        six_month_forecast += getattr(planning, field_name)
                    count_to_six += 1
                    key += 1
                    if key > 12:
                        key = 1
                rationale += '<br/>Actual  |'
                key = current_date.month
                for month in next_6_months:
                    field_name = 'consumption_month' + str(key)
                    rationale += '{0: <16.2f}|'.format(getattr(planning, field_name))
                    key += 1
                    if key > 12:
                        key = 1
                rationale += '<br/>Diff    |'
                key = current_date.month
                for month in next_6_months:
                    field_name = 'qty_month' + str(key)
                    diff = getattr(planning, field_name)
                    field_name = 'consumption_month' + str(key)
                    diff -= getattr(planning, field_name)
                    rationale += '{0: <16.2f}|'.format(diff)
                    key += 1
                    if key > 12:
                        key = 1
                rationale += "<br/>---------------------------------------------------------------------------------------------------------------<br/>"
                months_to_consider = int(planning.delay / 31)
                value_to_consider = 0
                if months_to_consider >= 1:
                    months_to_consider += 1
                if months_to_consider <= 0:
                    months_to_consider = 1
                rationale += '-------'
                key = current_date.month
                for current_month in range(13):
                    if current_month < months_to_consider:
                        field_name = 'qty_month' + str(key)
                        diff = getattr(planning, field_name)
                        field_name = 'consumption_month' + str(key)
                        diff -= getattr(planning, field_name)
                        if diff > 0:
                            value_to_consider += diff
                    if current_month + 1 == months_to_consider:
                        rationale += '>|' + '{0: <16.2f}'.format(value_to_consider)
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

                if consider_wip:
                    if consider_reserved:
                        current_balance = (planning.stock_qty+planning.wip_qty+planning.po_qty) - (planning.late_delivery + value_to_consider)
                    else:
                        current_balance = (planning.stock_qty+planning.wip_qty+planning.po_qty-planning.reserved) - (planning.late_delivery + value_to_consider)
                else:
                    if consider_reserved:
                        current_balance = (planning.stock_qty+planning.po_qty) - (planning.late_delivery + value_to_consider)
                    else:
                        current_balance = (planning.stock_qty+planning.po_qty-planning.reserved_wip) - (planning.late_delivery + value_to_consider)

                # Checking Minimal Quantity
                if current_balance < 0:
                    suggested_qty = planning.product_min_qty - current_balance
                else:
                    if current_balance < planning.product_min_qty:
                        suggested_qty = planning.product_min_qty - current_balance
                    else:
                        suggested_qty = 0

                # Calculates 12 months forecast
                twelve_month_forecast = 0
                for key in range(1,13):
                    field_name = 'qty_month' + str(key)
                    twelve_month_forecast += getattr(planning, field_name)

                # Checking negative quantities x lead time
                if suggested_qty == 0 and planning.balance_neg < 0:
                    date_date_neg = fields.Date.from_string(planning.negative_by)
                    date_date_cur = fields.Date.from_string(datetime.now())
                    days_diff = (date_date_neg - date_date_cur).days
                    if days_diff > planning.delay:
                        if planning.balance < 0:
                            suggested_qty = planning.balance * (-1)
                        else:
                            suggested_qty = planning.balance_neg * (-1)


                required_qty = suggested_qty
                planning.suggested_qty = required_qty
                planning.adjusted_qty = suggested_qty
                planning.six_month_forecast = six_month_forecast
                planning.twelve_month_forecast = twelve_month_forecast
                planning.total_price = required_qty * planning.vendor_price

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
                    if consider_reserved:
                        current_balance = planning.product_qty
                    else:
                        current_balance = planning.product_qty - planning.reserved
                else:
                    if consider_reserved:
                        current_balance = planning.product_qty - planning.wip_qty
                    else:
                        current_balance = planning.product_qty - planning.wip_qty - planning.reserved_wip

                if suggested_qty > current_balance:
                    planning.suggested_qty = required_qty
                    planning.adjusted_qty = suggested_qty
                    planning.purchase_adjusted = planning.product_id.uom_id._compute_quantity(required_qty,
                                                                                              planning.product_id.uom_po_id)
                    planning.purchase_suggested = planning.product_id.uom_id._compute_quantity(suggested_qty,
                                                                                               planning.product_id.uom_po_id)
                    planning.total_price = planning.vendor_price * planning.suggested_qty
                planning.rationale += rationale
            # if not purchase_planning:
            #    print(forecast.product_id.name)
            # else:
            #    print('product already in there.......')

        # Checking changes from previous report:
        mrp_purchase_product = self.env['flsp.mrp.purchase.line'].search(['|',('active', '=', True),('active', '=', False)], order='product_id, active')
        previous_plan = False
        for planning in mrp_purchase_product:  ##delete not used
            if previous_plan:
                if previous_plan.product_id == planning.product_id:
                    if abs(previous_plan.suggested_qty - planning.suggested_qty) > 0.01 or previous_plan.required_by != planning.required_by:
                        planning.new_update = True
            previous_plan = planning

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

    def _get_flattened_totals(self, bom, factor=1, totals=None, level=None, backflush=False):
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
        for line in bom.bom_line_ids:
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
                self._get_flattened_totals(sub_bom, new_factor, totals, level, backflush)
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

    def _include_prod(self, supplier_lead_time, product, rationale, balance, required_by, late_delivery, consider_wip, balance_neg, negative_by, avg_per_sbs, avg_per_ssa, consumption=False, forecast=False, po_qty=0.0, open_demand=0.0, consider_reserved=False):
        if not consumption:
            consumption = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        if not forecast:
            forecast = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        total_forecast = 0
        for item in forecast:
            total_forecast += item

        ret = False
        production_location = self.env['stock.location'].search([('usage', '=', 'production')], limit=1).id
        customer_location = self.env['stock.location'].search([('usage', '=', 'customer')], limit=1).id
        stock_location = self.env['stock.location'].search([('complete_name', '=', 'WH/Stock')]).parent_path
        if not stock_location:
            raise UserError('Stock Location is missing')
        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')]).parent_path
        if not pa_location:
            raise UserError('WIP Stock Location is missing')
        pa_wip_locations = self.env['stock.location'].search([('parent_path', 'like', pa_location + '%')]).ids
        if not pa_wip_locations:
            raise UserError('WIP Stock Location is missing')
        wh_stock_locations = self.env['stock.location'].search([('parent_path', 'like', stock_location + '%')]).ids
        if not wh_stock_locations:
            raise UserError('Stock Location is missing')

        pa_wip_qty = 0
        stock_quant = self.env['stock.quant'].search(
            ['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', product.id)])
        for stock_lin in stock_quant:
            pa_wip_qty += stock_lin.quantity

        stock_quant = self.env['stock.quant'].search(['&', ('product_id', '=', product.id), ('location_id', 'in', pa_wip_locations)])
        stock_reserverd = 0
        wip_reserverd = 0
        for each in stock_quant:
            wip_reserverd += each.reserved_quantity
        stock_quant = self.env['stock.quant'].search(['&', ('product_id', '=', product.id), ('location_id', 'not in', pa_wip_locations)])
        for each in stock_quant:
            stock_reserverd += each.reserved_quantity



        if not balance:
            if consider_wip:
                if consider_reserved:
                    current_balance = product.qty_available
                else:
                    current_balance = product.qty_available - stock_reserverd
            else:
                if consider_reserved:
                    if not product.flsp_is_wip_stock:
                        current_balance = product.qty_available - pa_wip_qty
                    else:
                        current_balance = product.qty_available
                else:
                    if not product.flsp_is_wip_stock:
                        current_balance = product.qty_available - pa_wip_qty - wip_reserverd
                    else:
                        current_balance = product.qty_available - wip_reserverd
            balance = current_balance
        else:
            current_balance = balance

        prod_vendor = self.env['product.supplierinfo'].search([('product_tmpl_id', '=', product.product_tmpl_id.id)],
                                                              limit=1)
        order_point = self.env['stock.warehouse.orderpoint'].search(
            ['&', ('product_id', '=', product.id), ('location_id', 'in', wh_stock_locations)], limit=1)
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
        if multiple > 1 and suggested_qty > 0:
            if multiple > suggested_qty:
                suggested_qty += multiple - suggested_qty
            else:
                if (suggested_qty % multiple) > 0:
                    suggested_qty += multiple - (suggested_qty % multiple)
        # Checking Vendor lead time:
        tmp_delay = supplier_lead_time
        if prod_vendor:
            if prod_vendor.delay:
                if prod_vendor.delay > tmp_delay:
                    tmp_delay = prod_vendor.delay
            if prod_vendor.delay and prod_vendor.delay > 0:
                if not required_by:
                    required_by = datetime.now()
                required_by = required_by - timedelta(days=tmp_delay)

        # check consumption of the component
        six_month_actual = 0
        twelve_month_actual = 0
        six_months_ago = datetime.now() - timedelta(days=180)
        one_year_ago = datetime.now() - timedelta(days=365)

        movements = self.env['stock.move.line'].search(['&', ('state', '=', 'done'), ('product_id', '=', product.id)])
        for move in movements:
            if move.location_dest_id.id in [production_location, customer_location]:
                if move.date > six_months_ago:
                    six_month_actual += move.qty_done
                if move.date > one_year_ago:
                    twelve_month_actual += move.qty_done

        if product.flsp_is_wip_stock:
            qty_stock = product.qty_available
        else:
            qty_stock = product.qty_available - pa_wip_qty


        ret = self.create({'product_tmpl_id': product.product_tmpl_id.id,
                           'product_id': product.id,
                           'description': product.product_tmpl_id.name,
                           'default_code': product.product_tmpl_id.default_code,
                           'suggested_qty': suggested_qty,
                           'adjusted_qty': suggested_qty,
                           'purchase_adjusted': product.uom_id._compute_quantity(suggested_qty, product.uom_po_id),
                           'purchase_suggested': product.uom_id._compute_quantity(suggested_qty, product.uom_po_id),
                           'uom': product.uom_id.id,
                           'purchase_uom': product.uom_po_id.id,
                           'calculated': True,
                           'product_qty': product.qty_available,
                           'reserved' :  stock_reserverd,
                           'reserved_wip' : wip_reserverd,
                           'product_min_qty': min_qty,
                           'product_max_qty': max_qty,
                           'qty_multiple': multiple,
                           'vendor_id': prod_vendor.name.id,
                           'vendor_qty': prod_vendor.min_qty,
                           'delay': tmp_delay,
                           'vendor_price': prod_vendor.price,
                           'total_price': prod_vendor.price * suggested_qty,
                           'stock_qty': qty_stock,
                           'wip_qty': pa_wip_qty,
                           'po_qty': po_qty,
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
                           'late_delivery': late_delivery,
                           'balance_neg': balance_neg,
                           'negative_by': negative_by,
                           'avg_per_sbs': avg_per_sbs,
                           'avg_per_ssa': avg_per_ssa,
                           'six_month_actual': six_month_actual,
                           'twelve_month_actual': twelve_month_actual,
                           'open_demand': open_demand,
                           'source': 'source', })

        return ret
