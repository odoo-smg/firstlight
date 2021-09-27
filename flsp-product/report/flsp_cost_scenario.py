# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api
from datetime import datetime


class FlspMrppurchaseReport(models.Model):
    _name = 'flsp.cost.scenario'
    _auto = False
    _description = 'FLSP Cost Scenario Report'

    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_id = fields.Many2one('product.template', string='Product', readonly=True)
    standard_price = fields.Float(
        'CAD$ Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price', groups="base.group_user",
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the last unit that left the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""")
    flsp_usd_cost = fields.Float(
        'USD$ Cost', compute='_compute_flsp_usd_cost',
        digits='Product Price', groups="base.group_user",
        help="""Converted cost to USD$""")

    uom_id = fields.Many2one('uom.uom', 'UofM')

    flsp_pref_cost = fields.Float('Preferred CAD$ Cost', digits='Product Price')
    flsp_best_cost = fields.Float('Optimistic CAD$ Cost', digits='Product Price')
    flsp_worst_cost = fields.Float('Pessimistic CAD$ Cost', digits='Product Price')

    flsp_usd_pref_cost = fields.Float('Preferred USD Cost', digits='Product Price', compute='_compute_flsp_usd_cost')
    flsp_usd_best_cost = fields.Float('Optimistic USD Cost', digits='Product Price', compute='_compute_flsp_usd_cost')
    flsp_usd_worst_cost = fields.Float('Pessimistic USD Cost', digits='Product Price', compute='_compute_flsp_usd_cost')

    flsp_latest_cost = fields.Float('Latest Cost', digits='Product Price')
    flsp_usd_latest_cost = fields.Float('Latest USD Cost', digits='Product Price')

    flsp_highest_price = fields.Float('Highest Price', digits='Product Price')
    flsp_usd_highest_price = fields.Float('Highest USD Price', digits='Product Price')
    flsp_highest_price_qty = fields.Float('Qty for Highest price', digits='Product Price')

    flsp_lowest_price = fields.Float('Lowest Price', digits='Product Price')
    flsp_usd_lowest_price = fields.Float('Lowest USD Price', digits='Product Price')
    flsp_lowest_price_qty = fields.Float('Qty for Highest price', digits='Product Price')

    @api.depends('standard_price', 'flsp_pref_cost', 'flsp_best_cost', 'flsp_worst_cost')
    def _compute_flsp_usd_cost(self):
        us_currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id
        usd_rate = self.env['res.currency.rate'].search([('currency_id', '=', us_currency_id)],limit=1)
        for each in self:
            each.flsp_usd_cost = each.standard_price * usd_rate.rate
            each.flsp_usd_pref_cost = each.flsp_pref_cost * usd_rate.rate
            each.flsp_usd_best_cost = each.flsp_best_cost * usd_rate.rate
            each.flsp_usd_worst_cost = each.flsp_worst_cost * usd_rate.rate

    def name_get(self):
        return [(
            record.id,
            record.default_code or str(record.id)
        ) for record in self]


    def _compute_standard_price(self):
        #print('calculating cost')
        for each in self:
            each.standard_price = each.product_id.standard_price

    @api.depends('standard_price', 'flsp_pref_cost', 'flsp_best_cost', 'flsp_worst_cost')
    def _compute_flsp_usd_cost(self):
        us_currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id
        usd_rate = self.env['res.currency.rate'].search([('currency_id', '=', us_currency_id)],limit=1)
        for each in self:
            each.flsp_usd_cost = each.standard_price * usd_rate.rate
            each.flsp_usd_pref_cost = each.flsp_pref_cost * usd_rate.rate
            each.flsp_usd_best_cost = each.flsp_best_cost * usd_rate.rate
            each.flsp_usd_worst_cost = each.flsp_worst_cost * usd_rate.rate

    def init(self):
        tools.drop_view_if_exists(self._cr, 'flsp_cost_scenario')

        query = """
        CREATE or REPLACE VIEW flsp_cost_scenario AS (
        select id,
               id as product_id, default_code,
               name as description,
               uom_id,
               flsp_pref_cost,
               flsp_best_cost,
               flsp_worst_cost,
               flsp_latest_cost,
               flsp_usd_latest_cost,
               flsp_highest_price,
               flsp_usd_highest_price,
               flsp_highest_price_qty,
               flsp_lowest_price,
               flsp_usd_lowest_price,
               flsp_lowest_price_qty
        from product_template where active = True
);
        """
        self.env.cr.execute(query)
