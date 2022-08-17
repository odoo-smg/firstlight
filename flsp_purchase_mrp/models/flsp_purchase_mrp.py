from odoo import models, fields, api
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class FlspPurchaseMrp(models.Model):
    _name = 'flsp.purchase.mrp'
    _description = 'FLSP Purchase MRP'

    supplier_lead_time = fields.Integer(string='Supplier Lead Time')
    standard_lead_time = fields.Integer(string='Standard Lead Time')
    standard_queue_time = fields.Integer(string='Standard Queue Time')
    indirect_lead_time = fields.Integer(string='Indirect Lead Time')
    consider_mo_drafts = fields.Boolean(string='Consider MO Drafts')
    consider_wip = fields.Boolean(string='Consider WIP', default=False)
    consider_forecast = fields.Boolean(string='Consider Forecast', default=True)
    consider_so = fields.Boolean(string='Consider Sales Orders', default=True)
    consider_po = fields.Boolean(string='Consider Purchase Orders', default=True)
    consider_mo = fields.Boolean(string='Consider Manufacturing Orders', default=False)
    auto_generated = fields.Boolean(string='Auto Generated', default=False)
    consider_reserved = fields.Boolean(string='Consider Reserved Quantity', default=False)
    date = fields.Datetime(String="Date", default=datetime.now())
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)
    state = fields.Selection([('new', 'New'), ('done', 'Calculated')], default="new", string='Status', readonly=True)
    purchase_mrp_lines = fields.One2many(comodel_name='flsp.purchase.mrp.line', inverse_name='purchase_mrp_id', string="Items")

    def name_get(self):
        return [(
            record.id,
            record.date or str(record.id)
        ) for record in self]

    def action_purchase_mrp_line(self):
        action = self.env.ref('flsp_purchase_mrp.flsp_purchase_mrp_line_action').read()[0]
        action['domain'] = [('purchase_mrp_id', '=', self.id)]
        action['context'] = {'search_default_filter_zero': 1}
        return action

    def run_purchase_mrp(self, product_from=False, product_to=False):
        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id

        ### delete here ########################
        #product_from = 1021  # do not use 0 for start
        #product_to = 1021
        ########################################

        start_time = datetime.now()
        if not product_from or not product_to:
            product_from = 1  # do not use 0 for start
            product_to = 999999
        open_moves = []
        actl_moves = []
        #for each in self:
            #res = self.env['flsp.open.moves'].calculate_purchase_mrp(each, product_from, product_to)
            #open_moves = res[0]
            #actl_moves = res[1]

        finish_open_moves = datetime.now()
        #print('done open moves')
        products_to_process = self.env['product.product'].search(['&', ('id', '>=', product_from), ('id', '<=', product_to)])

        for curr_product in products_to_process:
            if route_buy not in curr_product.route_ids.ids:
                continue
            if not curr_product.default_code:
                continue
            if curr_product.type in ['service', 'consu']:
                continue
            if curr_product:
                open_moves_filtered = self.filter_moves(open_moves, curr_product)
                # Sort by product and then date
                open_moves_filtered.sort(key=lambda x: (x[4].id, x[7]))
                self.process_moves(curr_product, open_moves_filtered)
                #if curr_product.flsp_substitute_ids:
                #    for substitute_product in curr_product.flsp_substitute_ids:
                #        self.process_moves(substitute_product.product_substitute_id, open_moves_filtered)

        #print('done processing the moves')

        finish_process = datetime.now()

        #process the forecast
        for each in self:
            self.process_forecast(product_from, product_to, actl_moves)

        #print('done forecast')

        finish_forecast = datetime.now()

        # Checking changes from previous report and substitute parts:
        purchase_mrp_product = self.env['flsp.purchase.mrp.line'].search(['&', '&', ('purchase_mrp_id', '=', self.id), ('product_id', '>=', product_from), ('product_id', '<=', product_to)])
        for planning in purchase_mrp_product:  ##delete not used
            subs = self.env['flsp.mrp.substitution.line'].search(['|', ('product_id', '=', planning.product_id.id), ('product_substitute_id', '=', planning.product_id.id)])
            for each in subs:
                if not each.flsp_bom_id.active or not each.flsp_bom_id.flsp_bom_plm_valid:
                    continue
                if planning.product_id.id == each.product_id.id:
                    planning.can_be_substituted_by_id = each.product_substitute_id
                    # if planning.suggested_qty > 0:
                    #     plan_sub = self.env['flsp.purchase.mrp.line'].search(['&', ('purchase_mrp_id', '=', self.id), ('product_id', '=', each.product_substitute_id.id)])
                    #     if plan_sub.suggested_qty == 0:
                    #         planning.rationale += "<br/><br/>Demand zeroed.<br/>*** This product can be substituted by: "+each.product_substitute_id.default_code
                    #         planning.suggested_qty = 0
                    #         planning.adjusted_qty = 0
                    #         planning.balance_neg = 0
                    #         planning.negative_by = False

                if planning.product_id.id == each.product_substitute_id.id:
                    planning.substitute_for_id = each.product_id
                    # if planning.suggested_qty > 0:
                    #     plan_sub = self.env['flsp.purchase.mrp.line'].search(['&', ('purchase_mrp_id', '=', self.id), ('product_id', '=', each.product_id.id)])
                    #     if plan_sub.suggested_qty == 0:
                    #         planning.rationale += "</br>Demand zeroed.</br>*** This product can be substituted by: "+each.product_id.default_code
                    #         planning.suggested_qty = 0
                    #         planning.adjusted_qty = 0
                    #         planning.balance_neg = 0
                    #         planning.negative_by = False

        self.state = 'done'
        finish_time = datetime.now()

    # ########################################
    # ######## FORECAST   ####################
    # ########################################
    def process_forecast(self, product_from, product_to, actl_moves):
        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id
        current_date = datetime.now()

        balance_neg = 0
        negative_by = False
        if self.consider_forecast:
            sales_forecast = self.env['flsp.sales.forecast'].search([])
        else:
            sales_forecast = []

        for forecast in sales_forecast:
            forecast._qty_based_off_date()
            forecast_bom = self.env['mrp.bom'].search(
                [('product_tmpl_id', '=', forecast.product_id.product_tmpl_id.id)], limit=1)
            if forecast_bom:
                #_get_flattened_totals(self, bom, factor=1, totals=None, level=None, backflush=False, substitute=False):
                forecast_components = self.env['flsp.open.moves']._get_flattened_totals(forecast_bom, 1, None, None, False, True)
                for component in forecast_components:
                    if component.id < product_from or component.id > product_to:
                        continue
                    if route_buy not in component.route_ids.ids:
                        continue
                    if component.flsp_start_buy:
                        if component.flsp_start_buy > fields.Date.today():
                            continue
                    purchase_planning = self.env['flsp.purchase.mrp.line'].search(
                        ['&', ('product_id', '=', component.id), ('purchase_mrp_id', '=', self.id)], limit=1)
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
                        purchase_line = self._include_prod(self.supplier_lead_time, product, rationale, False, current_date, late_delivery, self.consider_wip, balance_neg, negative_by, 0, 0,
                                                           False, forecasted, 0, 0, self.consider_reserved)
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
                if forecast.product_id.id < product_from or forecast.product_id.id > product_to:
                    continue
                not_postpone = True
                if forecast.product_id.flsp_start_buy:
                    if forecast.product_id.flsp_start_buy > date.today():
                        not_postpone = False
                if not_postpone and forecast.product_id.type == 'product' and route_buy in forecast.product_id.route_ids.ids:

                    purchase_planning = self.env['flsp.purchase.mrp.line'].search(
                        ['&', ('product_id', '=', forecast.product_id.id), ('purchase_mrp_id', '=', self.id)], limit=1)
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
                        purchase_line = self._include_prod(self.supplier_lead_time, product, rationale, False, current_date, late_delivery,
                                                           self.consider_wip, balance_neg, negative_by, 0, 0, False, forecasted, 0, 0, self.consider_reserved)
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

        purchase_planning = self.env['flsp.purchase.mrp.line'].search(['&', '&', ('purchase_mrp_id', '=', self.id), ('product_id', '>=', product_from), ('product_id', '<=', product_to)])
        months = ['', 'January         ', 'February        ', 'March           ', 'April           ',
                  'May             ', 'June            ', 'July            ', 'August          ',
                  'September       ', 'October         ', 'November        ', 'December        ']
        months_a = ['', 'January - Actual', 'February-Actual ', 'March - Actual  ', 'April - Actual  ',
                  'May - Actual    ', 'June - Actual   ', 'July - Actual   ', 'August - Actual ',
                  'September-Actual', 'October - Actual', 'November-Actual ', 'December-Actual ']
        months_o = ['', 'January - Open  ', 'February - Open ', 'March - Open    ', 'April - Open    ',
                  'May - Open      ', 'June - Open     ', 'July - Open     ', 'August - Open   ',
                  'September - Open', 'October - Open  ', 'November - Open ', 'December - Open ']
        next_6_months = []
        next_6_months_2 = []
        key = current_date.month
        count = 1
        for month in months:
            if count > 12:
                break
            if key > 12:
                key = 1
            if count <= 6:
                next_6_months.append(months[key])
            else:
                next_6_months_2.append(months[key])
            key += 1
            count += 1

        for planning in purchase_planning:
            actual_month_consumption = self.filter_actuals(planning.product_id.id)
            #actual_month_consumption = 0
            #if planning.product_id.id in actl_moves:
            #    actual_month_consumption = actl_moves[planning.product_id.id]
            six_month_forecast = 0
            rationale = "<pre>------------------------------------------------------------------------ Forecast ----------------------------------------------------------<br/>"
            next_line = "---------------------------------------------------------------------------------------------------------------------------<br/>"
            rationale += '                    |'
            next_line += '                    |'
            first_month = False
            key = current_date.month
            for month in next_6_months:
                if not first_month:
                    rationale += months_a[key] + "|"
                    rationale += months_o[key] + "|"
                    first_month = str(key)
                else:
                    rationale += month + "|"
            for month in next_6_months_2:
                next_line += month + "|"
            rationale += "<br/>"
            next_line += "<br/>"
            rationale += 'Forecast Consumption|'
            next_line += 'Forecast Consumption|'
            count_to_six = 0

            break_current_month = True
            first_month = False

            for month in next_6_months:
                if break_current_month:
                    # Actual column should have Forecast = 0
                    actual_on_month = actual_month_consumption
                    field_name = 'qty_month' + str(key)
                    forecast_month = getattr(planning, field_name)
                    if actual_on_month <= forecast_month:
                        rationale += '{0: <16.2f}|'.format(actual_on_month)
                    else:
                        rationale += '{0: <16.2f}|'.format(forecast_month)
                    break_current_month = False
                if not first_month:
                    first_month = key
                    field_name = 'qty_month' + str(key)
                    rationale += '{0: <16.2f}|'.format(getattr(planning, field_name)-actual_on_month)
                else:
                    field_name = 'qty_month' + str(key)
                    rationale += '{0: <16.2f}|'.format(getattr(planning, field_name))

                if count_to_six < 6:
                    six_month_forecast += getattr(planning, field_name)
                count_to_six += 1
                key += 1
                if key > 12:
                    key = 1
            for month in next_6_months_2:
                field_name = 'qty_month' + str(key)
                next_line += '{0: <16.2f}|'.format(getattr(planning, field_name))
                if count_to_six < 6:
                    six_month_forecast += getattr(planning, field_name)
                count_to_six += 1
                key += 1
                if key > 12:
                    key = 1
            rationale += '<br/>Actual Consumption  |'
            next_line += '<br/>Actual Consumption  |'
            key = current_date.month
            break_current_month = True
            for month in next_6_months:
                if break_current_month:
                    # Actual consumption on Open column
                    rationale += '{0: <16.2f}|'.format(actual_month_consumption)
                    break_current_month = False
                field_name = 'consumption_month' + str(key)
                rationale += '{0: <16.2f}|'.format(getattr(planning, field_name))
                key += 1
                if key > 12:
                    key = 1
            for month in next_6_months_2:
                field_name = 'consumption_month' + str(key)
                next_line += '{0: <16.2f}|'.format(getattr(planning, field_name))
                key += 1
                if key > 12:
                    key = 1

            rationale += '<br/>Forecasted Arrivals |'
            next_line += '<br/>Forecasted Arrivals |'
            key = current_date.month
            break_current_month = True
            for month in next_6_months:
                if break_current_month:
                    # On Open the forecasted arrival should be 0
                    rationale += '{0: <16.2f}|'.format(0)
                    break_current_month = False
                field_name = 'OpenPO_month' + str(key)
                rationale += '{0: <16.2f}|'.format(getattr(planning, field_name))
                key += 1
                if key > 12:
                    key = 1
            for month in next_6_months_2:
                field_name = 'OpenPO_month' + str(key)
                next_line += '{0: <16.2f}|'.format(getattr(planning, field_name))
                key += 1
                if key > 12:
                    key = 1

            rationale += '<br/>Quantity Change     |'
            next_line += '<br/>Quantity Change     |'
            key = current_date.month
            curr_m = key
            break_current_month = True
            for month in next_6_months:
                if break_current_month:
                    field_name = 'qty_month' + str(first_month)
                    forecast_total = 0 #getattr(planning, field_name)
                    field_name = 'consumption_month' + str(key)
                    consumption_total = 0 #getattr(planning, field_name)
                    field_name = 'OpenPO_month' + str(key)
                    openPO_total = 0 #getattr(planning, field_name)
                    if consumption_total > forecast_total:
                        diff = openPO_total - consumption_total
                    else:
                        diff = openPO_total - forecast_total
                    rationale += '{0: <16.2f}|'.format(diff)
                    break_current_month = False

                #actual_month_consumption
                field_name = 'qty_month' + str(key)
                forecast_total = getattr(planning, field_name)

                field_name = 'consumption_month' + str(key)
                consumption_total = getattr(planning, field_name)
                field_name = 'OpenPO_month' + str(key)
                openPO_total = getattr(planning, field_name)
                #else:
                #    consumption_total = 0
                #    openPO_total = 0

                if consumption_total > forecast_total:
                    diff = openPO_total - consumption_total
                else:
                    if curr_m != key:
                        diff = openPO_total - forecast_total
                    else:
                        if actual_month_consumption < forecast_total:
                            diff = openPO_total - (forecast_total - actual_month_consumption)
                        else:
                            diff = openPO_total
                rationale += '{0: <16.2f}|'.format(diff)
                key += 1
                if key > 12:
                    key = 1

            for month in next_6_months_2:
                field_name = 'qty_month' + str(key)
                diff = getattr(planning, field_name)
                field_name = 'consumption_month' + str(key)
                diff -= getattr(planning, field_name)
                next_line += '{0: <16.2f}|'.format(diff)
                key += 1
                if key > 12:
                    key = 1
            rationale += "<br/>--------------------------------------------------------------------------------------------------------------------------------------------<br/>"
            next_line += "<br/>---------------------------------------------------------------------------------------------------------------------------<br/>"
            months_to_consider = 13
            value_to_consider = 0
            if months_to_consider >= 1:
                months_to_consider += 1
            if months_to_consider <= 0:
                months_to_consider = 1
            rationale += 'Balance             '
            if months_to_consider > 6:
                next_line += 'Balance             '
            key = current_date.month
            count = 1

            total_to_print = False
            month_balance = planning.balance
            month_trigger = -1
            month_values = []
            break_current_month = True
            for current_month in range(13):
                if break_current_month:
                    break_current_month = False
                    rationale += '|' + '{0: <16.2f}'.format(month_balance)
                else:
                    count += 1
                    if current_month < months_to_consider:
                        #actual_month_consumption
                        if curr_m == key:
                            field_name = 'qty_month' + str(key)
                            diff = getattr(planning, field_name)
                            if actual_month_consumption < diff:
                                month_balance -= (getattr(planning, field_name)-actual_month_consumption)
                            field_name = 'consumption_month' + str(key)
                            diff -= getattr(planning, field_name)
                            field_name = 'OpenPO_month' + str(key)
                            diff += getattr(planning, field_name)
                            month_balance += getattr(planning, field_name)

                            if diff > 0:
                                value_to_consider += diff
                            if diff < 0:
                                month_balance += diff
                        else:
                            field_name = 'qty_month' + str(key)
                            diff = getattr(planning, field_name)
                            month_balance -= getattr(planning, field_name)
                            field_name = 'consumption_month' + str(key)
                            diff -= getattr(planning, field_name)
                            field_name = 'OpenPO_month' + str(key)
                            diff += getattr(planning, field_name)
                            month_balance += getattr(planning, field_name)

                            if diff > 0:
                                value_to_consider += diff
                            if diff < 0:
                                month_balance += diff

                        month_values.append(month_balance)
                    if current_month + 1 == months_to_consider:
                        if count <= 6:
                            rationale += '|' + '{0: <16.2f}'.format(month_balance)
                        else:
                            next_line += '|' + '{0: <16.2f}'.format(month_balance)
                    elif current_month < months_to_consider:
                        if count > 13:
                            if not total_to_print:
                                total_to_print = False
                        else:
                            if current_month <= 6:
                                if current_month == 6:
                                    rationale += '|{0: <16.2f}'.format(month_balance)
                                else:
                                    rationale += '|{0: <16.2f}'.format(month_balance)
                            else:
                                next_line += '|{0: <16.2f}'.format(month_balance)
                    else:
                        rationale += '                 '

                    key += 1
                    if key > 12:
                        key = 1
                if month_balance < planning.product_min_qty:
                    if month_trigger == -1:
                        month_trigger = current_month - 1

            if total_to_print:
                next_line += '{0: <16.2f}'.format(month_balance)
            rationale += '<br/>' + next_line
            rationale += '</pre>'

            new_suggested = 0
            if month_trigger >= 0:
                rationale += '<br/>(MSQ) Min. Stock Quantity: '+str(planning.product_min_qty)
                month_name = False
                if month_trigger < 6:
                    month_name = next_6_months[month_trigger]
                else:
                    if month_trigger < 12:
                        month_name = next_6_months_2[month_trigger-6]

                total_until = int(planning.delay / 31)+1

                if month_name:
                    rationale += '<br/>Balance below minimal at month:'+month_name
                else:
                    rationale += '<br/>Balance below minimal at month: out of range because is more than 12 months.'
                count = 0
                start_val = False
                final_val = False
                for each in month_values:
                    count+=1
                    if count-1 == month_trigger:
                        start_val = each
                    if total_until == count:
                        if not final_val:
                            final_val = each

                new_suggested = 0

                rationale += '<br/>(BBM) Balance when below min qty was:'+str(start_val)
                rationale += '<br/>Lead Time is: '+str(planning.delay)+' days ~ '+str(abs(total_until))+" months."

                if total_until > month_trigger and start_val <= planning.product_min_qty and abs(start_val) > 0.001:
                    new_suggested = planning.product_min_qty - start_val
                    rationale += '<br/>The Balance went bellow min before the leadtime, '
                    rationale += '<br/>So, quantity suggested should be (MSQ)-(BBM):'+str(new_suggested)
                else:
                    rationale += '<br/>Quantity available is enough to produce beyond the next order point.'
                    rationale += '<br/>So, quantity suggested should be zero. '
                    new_suggested = 0

            if not planning.required_by:
                if month_trigger >= 0:
                    day_required_by = fields.Date.today().day
                    month_required_by = fields.Date.today().month+month_trigger
                    year_required_by = fields.Date.today().year

                    required_by = fields.Date.today() + relativedelta(months=month_trigger)
                    if month_required_by > 12:
                        month_required_by = month_required_by - 12
                        year_required_by+=1

                    date_time_str = str(day_required_by)+'/'+str(month_required_by)+'/'+str(year_required_by)
                    rationale += '<br/><br/>-->Considering the date when the balance was below min qty as: '+date_time_str

                    required_by = required_by - timedelta(days=planning.delay)
                    rationale += '<br/>After decreasing date with supplier lead-time of: '+str(planning.delay)+' days, the required date should be: '+str(required_by)
                    planning.required_by = required_by
            else:
                required_by = planning.required_by - timedelta(days=planning.delay)
                planning.required_by = required_by

            if self.consider_wip:
                if self.consider_reserved:
                    current_balance = (planning.stock_qty+planning.wip_qty+planning.po_qty-planning.reserved) - (planning.late_delivery + value_to_consider)
                else:
                    current_balance = (planning.stock_qty + planning.wip_qty + planning.po_qty) - (
                                planning.late_delivery + value_to_consider)
            else:
                if self.consider_reserved:
                    current_balance = (planning.stock_qty+planning.po_qty-planning.reserved_wip) - (planning.late_delivery + value_to_consider)
                else:
                    current_balance = (planning.stock_qty+planning.po_qty) - (planning.late_delivery + value_to_consider)

            # Checking Minimal Quantity
            if current_balance < 0:
                suggested_qty = planning.product_min_qty - current_balance
            else:
                if current_balance < planning.product_min_qty:
                    suggested_qty = planning.product_min_qty - current_balance
                else:
                    suggested_qty = 0

            suggested_qty = new_suggested


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

            suggested_qty = new_suggested

            required_qty = suggested_qty
            planning.suggested_qty = required_qty
            planning.adjusted_qty = suggested_qty
            planning.six_month_forecast = six_month_forecast
            planning.twelve_month_forecast = twelve_month_forecast
            planning.total_price = required_qty * planning.vendor_price

            # Checking supplier quantity:
            if suggested_qty > 0.001 and planning.vendor_qty > 0:
                if suggested_qty < planning.vendor_qty:
                    rationale += "<br/><br/> ** Supplier quantity is bigger than the suggested qty."
                    rationale += "<br/>Adjusted quantity has been changed to: " + str(planning.vendor_qty)
                    suggested_qty = planning.vendor_qty

            # checking multiple quantities
            if planning.qty_multiple > 1 and suggested_qty > 0.001:
                rationale += "<br/><br/> ** This product requires multiple quantity of: " + str(planning.qty_multiple)
                if planning.qty_multiple > suggested_qty:
                    suggested_qty += planning.qty_multiple - suggested_qty
                else:
                    if (suggested_qty % planning.qty_multiple) > 0:
                        suggested_qty += planning.qty_multiple - (suggested_qty % planning.qty_multiple)
                rationale += "<br/>Adjusted quantity has been changed to: " + str(suggested_qty)

            #####################################################################################
            # Changed on: 2022-08-17
            # Changed by: Alexandre Sousa
            # Requested by: Cam Quan
            # Approved by: Cam Quan
            # Details on Ticket #846 in Odoo / Issue #710 in Redmine
            ##################################################################################### #710 in Redmine
            if planning.product_id.flsp_start_buy:
                if planning.product_id.flsp_start_buy > fields.Date.today():
                    required_qty = 0
                    suggested_qty = 0
                    rationale += "<br/>This product has been postponed to purchase until: " + str(planning.product_id.flsp_start_buy)
            ##################################################################################### #710 in Redmine

            planning.suggested_qty = required_qty
            planning.adjusted_qty = suggested_qty
            planning.purchase_adjusted = planning.product_id.uom_id._compute_quantity(required_qty,
                                                                                      planning.product_id.uom_po_id)
            planning.purchase_suggested = planning.product_id.uom_id._compute_quantity(suggested_qty,
                                                                                       planning.product_id.uom_po_id)
            planning.total_price = planning.vendor_price * planning.suggested_qty
            planning.rationale += rationale

    def filter_moves(self, moves, product):
        filtered_moves = []
        open_moves = self.env['flsp.open.moves'].search([('product_id', '=', product.id)])
        for move in open_moves:
            if move.type == 'in':
                type = 'In   '
            else:
                type = 'Out  '
            if move.source == 'so':
                source = 'Sales   '
            elif move.source == 'po':
                source = 'Purchase'
            else:
                source = 'MO      '

            filtered_moves.append([len(filtered_moves) + 1, type, source,
                                       move.doc,
                                       move.product_id,
                                       move.qty, move.uom,
                                       move.date, move.level, move.lead_time, move.avg_sbs, move.avg_ssa])
        return filtered_moves

    def filter_actuals(self, product):
        res = 0
        actual = self.env['flsp.current.month.moves'].search([('product_id', '=', product)])
        if actual:
            res = actual.qty
        return res

    def process_moves(self, product, open_moves):
        pa_location = self.env['stock.location'].search([('complete_name', '=', 'WH/PA')]).parent_path
        if not pa_location:
            raise UserError('WIP Stock Location is missing')
        pa_wip_locations = self.env['stock.location'].search([('parent_path', 'like', pa_location + '%')]).ids
        stock_location = self.env['stock.location'].search([('complete_name', '=', 'WH/Stock')]).parent_path
        if not stock_location:
            raise UserError('Stock Location is missing')
        wh_stock_locations = self.env['stock.location'].search([('parent_path', 'like', stock_location + '%')]).ids
        if not wh_stock_locations:
            raise UserError('Stock Location is missing')
        current_date = datetime.now()
        if not pa_wip_locations:
            raise UserError('WIP Stock Location is missing')
        required_by = False
        negative_by = False
        late_delivery = 0
        open_demand = 0
        avg_per_sbs = 0
        avg_per_ssa = 0
        balance_neg = 0
        pa_wip_qty = 0
        stock_reserverd = 0
        wip_reserverd = 0
        po_qty = 0
        consumption = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        openpo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        stock_quant = self.env['stock.quant'].search(['&', ('location_id', 'in', pa_wip_locations), ('product_id', '=', product.id)])
        initial_balance_explanation = ""
        for stock_lin in stock_quant:
            pa_wip_qty += stock_lin.quantity
        stock_quant = self.env['stock.quant'].search(['&', ('product_id', '=', product.id), ('location_id', 'in', pa_wip_locations)])
        for each in stock_quant:
            wip_reserverd += each.reserved_quantity
        stock_quant = self.env['stock.quant'].search(['&', ('location_id', 'in', wh_stock_locations), ('product_id', '=', product.id)])
        for each in stock_quant:
            stock_reserverd += each.reserved_quantity
        stock_reserverd = stock_reserverd

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


        initial_balance_explanation += "<br/>(A) Stock Quantity = " + str(product.qty_available - pa_wip_qty)
        initial_balance_explanation += "<br/>(B) WIP Quantity = " + str(pa_wip_qty)
        initial_balance_explanation += "<br/>(C) Stock Reserved  = " + str(stock_reserverd)
        initial_balance_explanation += "<br/>(D) WIP Reserved  = " + str(wip_reserverd)
        if self.consider_wip:
            initial_balance_explanation += "<br/>You choose to consider WIP for the on hand quantity."
            if not self.consider_reserved:
                initial_balance_explanation += "<br/>You choose to consider reserved quantity of WIP."
                current_balance = product.qty_available
                initial_balance_explanation += "<br/>(E)Initial Balance should be: A+B = " + str(current_balance)
            else:
                initial_balance_explanation += "<br/>You choose not to consider reserved quantity."
                current_balance = product.qty_available - stock_reserverd - wip_reserverd
                initial_balance_explanation += "<br/>(E)Initial Balance should be: (A+B)-(C+D) = " + str(current_balance)
        else:
            initial_balance_explanation += "<br/>You choose not to consider WIP for the on hand quantity."
            if not self.consider_reserved:
                if not product.flsp_is_wip_stock:
                    initial_balance_explanation += "<br/>You choose to consider reserved quantity of Stock."
                    current_balance = product.qty_available - pa_wip_qty
                    initial_balance_explanation += "<br/>(E)Initial Balance should be: A = " + str(current_balance)
                else:
                    initial_balance_explanation += "<br/>This product is set to consider WIP = Stock."
                    initial_balance_explanation += "<br/>You choose to consider reserved quantity of WIP."
                    current_balance = product.qty_available
                    initial_balance_explanation += "<br/>(E)Initial Balance should be: A+B = " + str(current_balance)
            else:
                if not product.flsp_is_wip_stock:
                    initial_balance_explanation += "<br/>You choose not to consider reserved quantity."
                    current_balance = product.qty_available - stock_reserverd
                    initial_balance_explanation += "<br/>(E)Initial Balance should be: (A-C) = " + str(current_balance)
                else:
                    initial_balance_explanation += "<br/>This product is set to consider WIP = Stock."
                    initial_balance_explanation += "<br/>You choose not to consider reserved quantity."
                    current_balance = product.qty_available - stock_reserverd - wip_reserverd
                    initial_balance_explanation += "<br/>(E)Initial Balance should be: (A+B)-(C+D) = " + str(current_balance)

        if len(open_moves) > 0:
            rationale = "<pre>-----------------------------------------------------------------------------------------------------------------"
            rationale += "<br/>                                        | Movement                                               |  AVG"
            rationale += "<br/>DATE        | QTY         |Balance      |Type |Source  |BOM Level|Mfg Lead time| Doc             | SBS  | SA   |"
            rationale += "<br/>------------|-------------|-------------|-----|--------|---------|-------------|-----------------|------|------|"
            rationale += '<br/>            |             | ' + '{0: <12.2f}|'.format(
                current_balance) + '     |        |         |             |Initial Balance  |      |      |'
        else:
            #rationale = "<pre>No open movements for this product."
            rationale = "<pre>"
        initial_balance = current_balance
        late_receipts = 0
        current_date_before = current_date.date() + relativedelta(days=-1)
        for item in open_moves:
            if item:
                if item[4].flsp_start_buy:
                    if item[4].flsp_start_buy > fields.Date.today():
                        continue
                if item[1] == 'In   ':
                    if current_date > item[7]:
                        late_receipts += item[5]
                    # Do not account the past
                    if current_date < item[7]:
                        openpo[item[7].month] += item[5]
                if item[1] == 'Out  ':
                    current_balance -= item[5]
                    # Do not account the past
                    if current_date_before < item[7].date():
                        consumption[item[7].month] += item[5]
                    else:
                        late_delivery += item[5]
                    open_demand += item[5]
                else:
                    current_balance += item[5]
                if not required_by:
                    # Consider only the current month
                    if current_balance < min_qty:
                        if current_date.month == item[7].month:
                            required_by = item[7]
                if current_balance < 0 and not negative_by:
                    if current_date < item[7]:
                        balance_neg = current_balance
                        negative_by = item[7]
                if not item[3]:
                    item[3] = ''
                if item[10] > 0:
                    avg_per_sbs = (avg_per_sbs + item[10]) / 2
                if item[11] > 0:
                    avg_per_ssa = (avg_per_ssa + item[11]) / 2
                if item[2] == "Purchase":
                    po_qty = po_qty + item[5]

                rationale += '<br/>' + item[7].strftime("%Y-%m-%d") + '  | ' + '{:<12.4f}|'.format(
                    item[5]) + ' ' + '{0: <12.2f}|'.format(current_balance) + item[1] + '|' + item[
                                 2] + '|' + '{0: <9}|'.format(item[8]) + '{0: <13}|'.format(item[9]) + item[
                                 3] + '|' + '{0:<6.2f}|'.format(item[10]) + '{0:<6.2f}|'.format(item[11])

        #include a new product
        rationale += "</pre>"
        rationale += initial_balance_explanation
        rationale += "<br/>   (LD) Late Deliveries: " + '{0: <12.2f}'.format(late_delivery)
        rationale += "<br/>   (LP) Late POs: " + '{0: <12.2f}'.format(late_receipts)
        final_balance = initial_balance+late_receipts-late_delivery
        rationale += "<br/>   Balance should be (E-LD+LP): " + '{0: <12.2f}'.format(final_balance)

        purchase_line = self._include_prod(self.supplier_lead_time, product, rationale, final_balance, required_by,
                                       late_delivery, self.consider_wip, balance_neg, negative_by, avg_per_sbs,
                                       avg_per_ssa, consumption, False, po_qty, open_demand, self.consider_reserved, openpo)

    def _include_prod(self, supplier_lead_time, product, rationale, balance, required_by, late_delivery, consider_wip, balance_neg, negative_by, avg_per_sbs, avg_per_ssa, consumption=False, forecast=False, po_qty=0.0, open_demand=0.0, consider_reserved=False, openpo=False):
        if not consumption:
            consumption = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        if not forecast:
            forecast = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        if not openpo:
            openpo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
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
        stock_quant = self.env['stock.quant'].search(['&', ('product_id', '=', product.id), ('location_id', 'in', wh_stock_locations)])
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

        if product.type in ['service', 'consu']:
            return False

        ret = self.env['flsp.purchase.mrp.line'].create({
                           'purchase_mrp_id': self.id,
                           'product_tmpl_id': product.product_tmpl_id.id,
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
                           'OpenPO_month1': openpo[1],
                           'OpenPO_month2': openpo[2],
                           'OpenPO_month3': openpo[3],
                           'OpenPO_month4': openpo[4],
                           'OpenPO_month5': openpo[5],
                           'OpenPO_month6': openpo[6],
                           'OpenPO_month7': openpo[7],
                           'OpenPO_month8': openpo[8],
                           'OpenPO_month9': openpo[9],
                           'OpenPO_month10': openpo[10],
                           'OpenPO_month11': openpo[11],
                           'OpenPO_month12': openpo[12],
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


class FlspPurchaseMrpLine(models.Model):
    _name = 'flsp.purchase.mrp.line'
    _description = 'FLSP purchase MRP Line'

    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True, help="Product / Component - Only products that control stock (Storable products) with the flag Routes = 'to buy' will show up in this report.")
    stock_picking = fields.Many2one('stock.picking', string='Stock Picking', readonly=False)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', readonly=False)
    product_min_qty = fields.Float('Min. Qty', readonly=True, help="When the stock goes below the Min. Quantity specified for this field, the report suggests to buy more.")
    product_max_qty = fields.Float('Max. Qty', readonly=True)
    qty_multiple = fields.Float('Qty Multiple', readonly=True, help="The quantity suggested to buy will be rounded up to this multiple. Ex. If the report suggests to buy 34 of a product multiple of 4 the quantity will be adjusted to 36.")
    product_qty = fields.Float(string='Qty on Hand', readonly=True, help="The total on hand includes WIP+Stock and all reserved quantity. If the product is set to have WIP=Stock the WIP value is already in the total.")
    reserved = fields.Float(string='Qty Reserved', readonly=True, help="Stock only reserved quantity.")
    reserved_wip = fields.Float(string='Qty Reserved WIP', readonly=True, help="WIP only reserved quantity.")
    qty_mo = fields.Float(string='Qty of Draft MO', readonly=True)
    curr_outs = fields.Float(String="Demand", readonly=True,
                             help="Includes all confirmed sales orders and manufacturing orders")
    curr_ins = fields.Float(String="Replenishment", readonly=True,
                            help="Includes all confirmed purchase orders and manufacturing orders")
    average_use = fields.Float(String="Avg Use", readonly=True, help="Average usage of the past 3 months.")
    month1_use = fields.Float(String="2020-06 Usage", readonly=True, help="Total usage of last month.")
    month2_use = fields.Float(String="2020-05 Usage", readonly=True, help="Total usage of 2 months ago.")
    month3_use = fields.Float(String="2020-04 Usage", readonly=True, help="Total usage of 3 months ago.")
    suggested_qty = fields.Float(String="Suggested Qty", readonly=True, help="Quantity required to buy according to the rationale below.")
    adjusted_qty = fields.Float(String="Adjusted Qty", help="This quantity is the result of the required quantity after calculated the multiple and the vendor quantity.")
    purchase_adjusted = fields.Float(string='Adjusted 2nd uom', help="Same as the Required quantity, but using the purchase unit of measure, oposed to the consumption unit of measure.")
    purchase_suggested = fields.Float(String="Suggested 2nd uom", readonly=True, help="Same as the Adjusted Qty but using the purchase unit of measure, oposed to the consumption unit of measure.")
    po_qty = fields.Float(string='Qty Open PO', help="The total quantity of this product with open receipts to be received.")
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

    stock_qty = fields.Float(string='Stock Qty', readonly=True, help="Quantity in WH/Stock and sub-locations. The total here includes the Stock Reserved quantity. Also, the QA quantity.")
    wip_qty = fields.Float(string='WIP Qty', readonly=True, help="Quantity in WH/PA/WIP and sub-locations. The total here includes the WIP Reserved quantity.")
    vendor_id = fields.Many2one('res.partner', string='Supplier', help="Vendor for this product listed in the Purchase price list.")
    vendor_qty = fields.Float(string='Quantity', readonly=True, help="The quantity to purchase from this vendor to benefit from the price. This field will update the adjusted quantity using the required quantity as the initial value.")
    vendor_price = fields.Float(string='Unit Price', readonly=True, help="Price to purchase 1 unit of the product.")
    delay = fields.Integer(string="Delivery Lead Time", help="Lead time in days between the cofirmation of the purchase order and the receipt of the products in your warehouse. This information will be used to decrease the date when the stock goes below the min. quantity.")
    required_by = fields.Date(String="Required by", readonly=True, help="This date is calculated as the rationale below. In the happy path this should be the date the stock quantity goes below the min. quantiy decreased by the number of days listed in the Supplier Delivery Lead Time.")
    balance = fields.Float(string='Balance', readonly=True)
    late_delivery = fields.Float(string='Balance', readonly=True)
    total_price = fields.Float(string='Total Price', readonly=True)

    balance_neg = fields.Float(string='Negative Balance', readonly=True)
    negative_by = fields.Date(String="Negative by", readonly=True)

    avg_per_sbs = fields.Float(string='Avg per SBS', readonly=True)
    avg_per_ssa = fields.Float(string='Avg per SA', readonly=True)

    uom = fields.Many2one('uom.uom', 'Product Unit of Measure', readonly=True, help="Unit of measure for consumption. This is the unit of measure used in all operations with exception of purchasing when the supplier uses a different unit of measure.")
    purchase_uom = fields.Many2one('uom.uom', 'Purchase Unit of Measure', readonly=True, help="Supplier unit of measure. This could eventualy be different of the Standard unit of measure.")

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

    OpenPO_month1 = fields.Float(string='Open PO January')
    OpenPO_month2 = fields.Float(string='Open PO February')
    OpenPO_month3 = fields.Float(string='Open PO March')
    OpenPO_month4 = fields.Float(string='Open PO April')
    OpenPO_month5 = fields.Float(string='Open PO May')
    OpenPO_month6 = fields.Float(string='Open PO June')
    OpenPO_month7 = fields.Float(string='Open PO July')
    OpenPO_month8 = fields.Float(string='Open PO August')
    OpenPO_month9 = fields.Float(string='Open PO September')
    OpenPO_month10 = fields.Float(string='Open PO October')
    OpenPO_month11 = fields.Float(string='Open PO November')
    OpenPO_month12 = fields.Float(string='Open PO December')

    six_month_forecast = fields.Float(string='6 Months Forecast', help="This is the total of the 6 months future sales forecast. The forecast is the expectation of the quantity we will be selling in the future.")
    twelve_month_forecast = fields.Float(string='12 Months Forecast', help="This is the total of the 12 months future sales forecast. The forecast is the expectation of the quantity we will be selling in the future.")

    six_month_actual = fields.Float(string='6 Months Actual', help="The past 6 months Actual is the real consumption of this product in the past 6 months. It does not includes any inventory adjustments.")
    twelve_month_actual = fields.Float(string='12 Months Actual', help="The past 12 months Actual is the real consumption of this product in the past 12 months. It does not includes any inventory adjustments.")

    open_demand = fields.Float(string='Open Demand', help="Is the total of movements of Type Out shown in the list below.")

    active = fields.Boolean(default=True)

    new_update = fields.Boolean(default=False)

    purchase_mrp_id = fields.Many2one('flsp.purchase.mrp', required=True)

    substitute_for_id = fields.Many2one('product.product', string='Substitute for', readonly=True)
    can_be_substituted_by_id = fields.Many2one('product.product', string='Can be Substituted by', readonly=True)

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
                planning.purchase_adjusted = self.product_id.uom_id._compute_quantity(self.adjusted_qty,self.product_id.uom_po_id)
