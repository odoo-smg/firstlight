# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models


class FlspCostDetailView(models.Model):
    """
        Class_Name: FlspCostDetail
        Model_Name: flsp.cost.detail.view
        Purpose:    Create a view for Cost Detail Report
        Date:       October/12th/Tuesday/2021
        Updated:
        Author:     Alexandre Sousa
    """
    _name = 'flsp.cost.detail.view'
    _auto = False
    _description = 'Cost Detail Report'

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')
    date = fields.Datetime(string="Date", readonly=True)
    location_id = fields.Many2one('stock.location', string='Source', readonly=True)
    location_dest_id = fields.Many2one('stock.location', string='Destination', readonly=True)
    reference = fields.Char(string="Reference", readonly=True)
    origin = fields.Char(string="Origin", readonly=True)
    qty_done = fields.Float(string='Qty Moved', readonly=True)
    price_unit = fields.Float(string='Price Unit', readonly=True)

    product_qty = fields.Float(string='Product Qty', readonly=True)

    value = fields.Float(string='Value', readonly=True)
    unit_cost = fields.Float(string='Valuation Cost', readonly=True)

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    # product_uom = fields.Many2one('uom.uom', 'UOM', readonly=True)

    product_tmpl_id = fields.Many2one('product.template', string='Product Template', readonly=True)  ###

    balance = fields.Float(string='Balance', readonly=True, compute='_compute_balance_cost')
    cost = fields.Float(string='Unit Cost', readonly=True, compute='_compute_balance_cost', digits='Product Price')
    seq = fields.Integer(string='Sequence', readonly=True, compute='_compute_balance_cost')

    stock_move_line_id = fields.Many2one('stock.move.line', string='Move Line Id', readonly=True)
    stock_valuation_layer_id = fields.Many2one('stock.valuation.layer', string='Stock Valuation Layer Id', readonly=True)

    def _compute_balance_cost(self):
        return 0
        prd_id = False
        reg = 1
        total_reg = 0
        for each in self:
            prd_id = each.product_id
            reg = reg + 1
        if prd_id:
            query = "select count(*) as total from flsp_cost_detail where product_id = '" + str(prd_id.id) + "'"
            self._cr.execute(query)
            retvalue = self._cr.fetchall()
            if retvalue:
                print(retvalue[0])
                total_reg = retvalue[0][0]
                print('----------> Here is the total of regs for this product: ' + str(
                    retvalue[0]) + '    Reg is: ' + str(reg))

        product = False
        reg = 1
        print(' ***** getting started *******************************************')
        for line in self.sorted(key=lambda r: r.date):
            if not Counter.product:
                Counter.product = line.product_id
                Counter.reg = 1
                Counter.balance = 0
                Counter.cost = 0
            elif Counter.product != line.product_id:
                Counter.product = line.product_id
                Counter.reg = 1
                Counter.balance = 0
                Counter.cost = 0
            current_balance = 0
            current_cost = 0
            last_balance = Counter.balance
            last_cost = Counter.cost

            if not product:
                product = line.product_id
            if product == line.product_id:
                if last_balance:
                    current_balance = last_balance

                if line.location_id:
                    if "Virtual" in line.location_id.complete_name \
                            or "Partner" in line.location_id.complete_name \
                            or "Rejected" in line.location_id.complete_name:
                        current_balance += line.qty_done
                if line.location_dest_id:
                    if "Virtual" in line.location_dest_id.complete_name \
                            or "Partner" in line.location_dest_id.complete_name \
                            or "Rejected" in line.location_dest_id.complete_name:
                        current_balance -= line.qty_done
                if last_cost:
                    current_cost = last_cost
                if line.picking_type_id.id != 0:
                    if line.picking_type_id.code != "internal":
                        if last_balance + line.product_qty != 0:
                            current_cost = (last_cost * last_balance) + abs(line.value)
                            current_cost = current_cost / (last_balance + line.product_qty)
                else:
                    if "Product value manually modified" in line.reference:
                        print("-----------------------------------------------------------------------------")
                        print(line.reference)
                        print(line.reference.find(' to '))
                        print(line.reference[line.reference.find(' to ') + 4:-1])
                        current_cost = float(line.reference[line.reference.find(' to ') + 4:-1])

                line.cost = current_cost
                line.balance = current_balance
                last_balance = current_balance
                last_cost = current_cost
                Counter.balance = current_balance
                Counter.cost = current_cost
                line.seq = reg

                print('Reg: ' + str(Counter.reg) + '  Calculating date: ' + str(line.date) + '   cost is: ' + str(
                    current_cost) + '    Balance is: ' + str(current_balance))
                if Counter.reg >= total_reg:
                    print('Cleaning the counter')
                    Counter.product = False
                    Counter.reg = 0
                    Counter.balance = 0
                    Counter.cost = 0
                reg = reg + 1
                Counter.reg += 1

            product = line.product_id
        return 0

    # pdct_name = fields.Char()###
    # lot_name = fields.Char()###
    # stck_name = fields.Char()###
    # usage_name = fields.Char()###

    def init(self):
        """
            Purpose: To extract database information and create tree view using the query
        """
        tools.drop_view_if_exists(self._cr, 'flsp_cost_detail_view')

        query = """
        CREATE or REPLACE VIEW flsp_cost_detail_view AS(
        select ROW_NUMBER () OVER (ORDER BY product_id, date) as id, * from (
            select      sml.id as stock_move_line_id,
                        null as stock_valuation_layer_id,
                        sm.origin,
                        sm.picking_type_id,
                        sml.date, sml.location_id, sml.location_dest_id, sml.reference, sml.qty_done,
                        sm.price_unit, sm.product_qty,
                        min(svl.value) as value, min(svl.unit_cost) as unit_cost,
                        sml.product_id, pp.product_tmpl_id
            from		stock_move_line sml
            inner join product_product pp
            on         pp.id = sml.product_id
            and        pp.active = True
            inner join stock_move sm
            on         sml.move_id = sm.id
            left join  stock_valuation_layer svl
            on         svl.stock_move_id = sm.id
            and        svl.stock_valuation_layer_id is null
            and        sm.product_qty = abs(svl.quantity)
            left join  stock_picking_type spt
            on         sm.picking_type_id = spt.id
            where      sml.state = 'done'
			group by    sml.id,
                        sm.origin,
                        sm.picking_type_id,
                        sml.date, sml.location_id, sml.location_dest_id, sml.reference, sml.qty_done,
                        sm.price_unit, sm.product_qty,
                        sml.product_id, pp.product_tmpl_id
            union all

            select      null as stock_move_line_id,
                        svl.id as stock_valuation_layer_id,
                        'Cost Adjustment' as origin, 0 as picking_type_id, svl.create_date as date, null as location_id, null as location_dest_id, description as reference, quantity as qty_done, unit_cost as price_unit, 0, value, unit_cost, product_id, product_tmpl_id
            from stock_valuation_layer svl
            inner join product_product pp
            on         pp.id = svl.product_id
            where (stock_move_id is null or svl.stock_valuation_layer_id is not null)
        ) A
        );
        """
        self.env.cr.execute(query)


class Counter(object):
    reg = False
    balance = False
    cost = False
    product = False
