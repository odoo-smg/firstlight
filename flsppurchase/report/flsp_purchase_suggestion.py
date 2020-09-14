# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class Purcahsesuggestion(models.Model):
    _name = 'report.purchase.suggestion'
    _auto = False
    _description = 'Purchase Suggestion Report'

    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_min_qty = fields.Float('Min. Qty', readonly=True)
    product_qty = fields.Float(string='Qty on Hand', readonly=True)
    curr_ins  = fields.Float(String="Demand", readonly=True, help="Includes all confirmed sales orders and manufacturing orders")
    curr_outs = fields.Float(String="Replenishment", readonly=True, help="Includes all confirmed purchase orders and manufacturing orders")
    average_use = fields.Float(String="Avg Use", readonly=True, help="Average usage of the past 3 months.")
    month1_use = fields.Float(String="2020-06 Usage", readonly=True, help="Total usage of last month.")
    month2_use = fields.Float(String="2020-05 Usage", readonly=True, help="Total usage of 2 months ago.")
    month3_use = fields.Float(String="2020-04 Usage", readonly=True, help="Total usage of 3 months ago.")
    suggested_qty = fields.Float(String="Suggested Qty", readonly=True, help="Quantity suggested to buy or produce.")
    level_bom = fields.Integer(String="BOM Level", compute='_compute_bom_level')
    state = fields.Selection([
        ('Buy', 'Suggested to Buy'),
        ('Ok', 'Acceptable level'),
    ], string='State', readonly=True)

    def init(self):
        print('Creating My view')
        tools.drop_view_if_exists(self._cr, 'report_purchase_suggestion')
        query = """
        CREATE or REPLACE VIEW report_purchase_suggestion AS (
        SELECT
            pp.id,
            -1 as level_bom,
            pt.default_code,
            pp.id as product_id,
            pp.product_tmpl_id as product_tmpl_id,
            'Buy' AS state,
            max(qty_in) as curr_ins,
            max(qty_out) as curr_outs,
            max(lm.avg_use) as month1_use,
            max(ma2.avg_use) as month2_use,
            max(ma3.avg_use) as month3_use,
            0 as average_use,
            0 as suggested_qty,
            pt.name AS description,
            max(sq.quantity) AS product_qty,
            min(swo.product_min_qty) as product_min_qty
        FROM product_product pp
        left join product_template pt
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
                    select product_id, sum(qty_in) as qty_in, sum(qty_out) as qty_out from (
                    -- purchase order confirmed
                    select product_id, sum(product_qty) as qty_in, 0  as qty_out from stock_move_line
                    where (location_id not in (select id
                                               from stock_location
                                               where usage = 'production')
                                               and location_dest_id not in (select id from stock_location where usage = 'production') )
                    and    location_dest_id in (select id from stock_location where usage = 'internal')
                    and    done_move = false
                    group by product_id
                    union all
                    -- sale order confirmed
                    select product_id, 0 as qty_in, sum(product_qty) as qty_out from stock_move_line
                    where (location_id not in (select id
                                               from stock_location
                                               where usage = 'production')
                                               and location_dest_id not in (select id from stock_location where usage = 'production') )
                    and   location_id in (select id from stock_location where usage = 'internal')
                    and    done_move = false
                    group by product_id
                    union all
                    -- production
                    select product_id, sum(product_qty) as qty_in, 0  as qty_out
                    from   mrp_production
                    where  state not in ('cancel', 'done')
                    group by product_id
                    union all
                    -- components for production
                    select product_id, 0 as qty_in, sum(product_qty)  as qty_out
                    from   stock_move
                    where  raw_material_production_id in (select id from mrp_production where state not in ('cancel', 'done'))
                    group by product_id
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
        group by  pp.id, pt.name, pt.default_code
        );
        """
        self.env.cr.execute(query)

    def _compute_bom_level(self):
        print('Calculating level')
        current_level = 1
        next_level = {current_level: {}}
        print('Level 0')
        for lines in self:
            if lines.product_id.used_in_bom_count:
                lines.level_bom = -1
            else:
                lines.level_bom = current_level
                next_level[current_level][lines.product_tmpl_id.id] = lines.product_id


        current_level += 1
        print('Level '+str(current_level)+'******************************************************')
        complete = True
        next_level[current_level] = {}
        for lines in self:
            if lines.level_bom < 0:
                print('   Product' + str(lines.product_id.id) )
                comp_boms = self.env['mrp.bom.line'].search([('product_id', '=', lines.product_id.id)])
                found_level = False
                for parent_bom in comp_boms:
                    print('      Bom:' + str(parent_bom.bom_id.id))
                    if parent_bom.bom_id.product_tmpl_id.id in next_level[current_level-1]:
                        lines.level_bom = current_level
                        next_level[current_level][lines.product_id.product_tmpl_id.id] = lines.product_id
                        found_level = True
                if not found_level:
                    complete = found_level

        '''
        complete = False
        while not complete:
            current_level += 1
            print('Level '+str(current_level)+'******************************************************')
            complete = True
            next_level[current_level] = {}
            for lines in self:
                if lines.level_bom < 0:
                    print('   Product' + str(lines.product_id.id) )
                    comp_boms = self.env['mrp.bom.line'].search([('product_id', '=', lines.product_id.id)])
                    found_level = False
                    for parent_bom in comp_boms:
                        print('      Bom:' + str(parent_bom.bom_id.id))
                        if parent_bom.bom_id.product_tmpl_id.id in next_level[current_level-1]:
                            lines.level_bom = current_level
                            next_level[current_level][lines.product_id.product_tmpl_id.id] = lines.product_id
                            found_level = True
                    if not found_level:
                        complete = found_level

        '''
