# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class Purcahsesupport(models.Model):
    _name = 'report.flsppurchase.auxview'
    _auto = False
    _description = 'Suggestion Support View'

    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
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

    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_flsppurchase_auxview')

        query = """
        CREATE or REPLACE VIEW report_flsppurchase_auxview AS (
        SELECT
            pp.id,
            pp.flsp_bom_level as level_bom,
            pt.default_code,
            pt.type,
            pp.id as product_id,
            pp.product_tmpl_id as product_tmpl_id,
            pp.flsp_suggested_state as state,
            max(qty_in) as curr_ins,
            max(qty_out) as curr_outs,
            max(qty_mo) as qty_mo,
            max(lm.avg_use) as month1_use,
            max(ma2.avg_use) as month2_use,
            max(ma3.avg_use) as month3_use,
            0 as average_use,
            max(rfq.qty_rfq) as qty_rfq,
            pp.flsp_route_buy as route_buy,
            pp.flsp_route_mfg as route_mfg,
            pp.flsp_suggested_qty as suggested_qty,
            pt.name AS description,
            max(sq.quantity) AS product_qty,
            min(swo.product_min_qty) as product_min_qty,
            min(swo.qty_multiple) as qty_multiple
        FROM product_product pp
        inner join product_template pt
        on        pp.product_tmpl_id = pt.id
        left join stock_warehouse_orderpoint swo
        on        swo.product_id = pp.id
        left join (select    sum(sq.quantity) as quantity, product_id
                   from      stock_quant sq
                   left join stock_location location_id
                   on        sq.location_id = location_id.id
                   where     location_id.usage = 'internal'
                   group by product_id) sq
         on    sq.product_id = pp.id
        left join (
                    select product_id, sum(qty_in) as qty_in, sum(qty_out) as qty_out, sum(qty_mo) as qty_mo from (
                    -- purchase order confirmed
                    select product_id, sum(product_qty) as qty_in, 0  as qty_out, 0 as qty_mo from stock_move_line
                    where (location_id not in (select id
                                               from stock_location
                                               where usage = 'production')
                                               and location_dest_id not in (select id from stock_location where usage = 'production') )
                    and    location_dest_id in (select id from stock_location where usage = 'internal')
                    and    done_move = false
                    group by product_id
                    union all
                    -- sale order confirmed and production
                    select sm.product_id, 0 as qty_in, sum(sm.product_qty) as qty_out , 0 as qty_mo
					from      stock_move sm
                    where sm.location_id in (select id from stock_location where usage = 'internal')
                    and sm.state not in ('done', 'cancel')
                    group by sm.product_id
                    union all
                    -- production
                    select product_id, sum(product_qty) as qty_in, 0  as qty_out, 0 as qty_mo
                    from   mrp_production
                    where  state not in ('cancel', 'done', 'draft')
                    group by product_id
                    union all
                    select product_id, 0 as qty_in, 0  as qty_out, sum(product_qty) as qty_mo
                    from   mrp_production
                    where  state = 'draft'
                    group by product_id
                    --union all
                    -- components for production
                    --select product_id, 0 as qty_in, sum(product_qty)  as qty_out
                    --from   stock_move
                    --where  raw_material_production_id in (select id from mrp_production where state not in ('cancel', 'done'))
                    --group by product_id
                    ) A group by product_id
        ) sm -- stock movement
        on     sm.product_id = pp.id
        left join (
                    select product_id, sum(qty_done) as avg_use, to_char(date, 'YYYYMM') as month
                    from stock_move_line
                    where done_move = true
                    and location_id in (select id from stock_location where usage = 'internal')
                    and to_char(date, 'YYYYMM') = to_char((to_date(to_char(current_date, 'YYYYMM')||'01', 'YYYYMMDD') - interval '1 day'), 'YYYYMM')
                    group by product_id, month
                    order by product_id, month
        ) lm --last month
        on     lm.product_id = pp.id
        left join (
                    select product_id, sum(qty_done) as avg_use, to_char(date, 'YYYYMM') as month
                    from stock_move_line
                    where done_move = true
                    and location_id in (select id from stock_location where usage = 'internal')
                    and to_char(date, 'YYYYMM') = to_char((to_date(to_char((to_date(to_char(current_date, 'YYYYMM')||'01', 'YYYYMMDD') - interval '1 day'), 'YYYYMM')||'01', 'YYYYMMDD') - interval '1 day'), 'YYYYMM')
                    group by product_id, month
                    order by product_id, month
        ) ma2 --2 months ago
        on     ma2.product_id = pp.id
        left join (
                    select product_id, sum(qty_done) as avg_use, to_char(date, 'YYYYMM') as month
                    from stock_move_line
                    where done_move = true
                    and location_id in (select id from stock_location where usage = 'internal')
                    and to_char(date, 'YYYYMM') = to_char((to_date(to_char((to_date(to_char((to_date(to_char(current_date, 'YYYYMM')||'01', 'YYYYMMDD') - interval '1 day'), 'YYYYMM')||'01', 'YYYYMMDD') - interval '1 day'), 'YYYYMM')||'01', 'YYYYMMDD') - interval '1 day'), 'YYYYMM')
                    group by product_id, month
                    order by product_id, month
        ) ma3 --3 months ago
        on     ma3.product_id = pp.id
        left join ( select   product_id, sum(product_qty) qty_rfq  from purchase_order, purchase_order_line
                    where    purchase_order_line.order_id = purchase_order.id
                    and      purchase_order.state = 'draft'
                    group by product_id) as rfq
        on     rfq.product_id = pp.id
        where pt.type = 'product'
        group by  pp.id, pt.name, pt.default_code, pp.flsp_route_buy, pp.flsp_route_mfg, pt.type
        );
        """

        self.env.cr.execute(query)
