# -*- coding: utf-8 -*-

from odoo import fields, models


class flspcustomerbadge(models.Model):
    _name = 'flsp.customer.badge'

    name = fields.Char(String="Badge Name", required=True)
    reward_level = fields.Selection([
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Sivler'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'platinum'),
        ], string='Reward Level', required=True)

    currency_id = fields.Many2one("res.currency", string="Currency", help="Currency of the program", required=True)
    annual_program_amount = fields.Monetary(string='Annual Program Spend', help="Annual Program Spend for the Reward Level", required=True)

    sale_discount = fields.Float(string='Rewards Pricing Discount (%)', digits='Discount', default=0.0)
    freight_units_5_to_10_discount = fields.Float(string='Freight Discount with 5-10 units (%)', digits='Discount', default=0.0)
    freight_units_over_10_discount = fields.Float(string='Freight Discount with more than 10 units (%)', digits='Discount', default=0.0)
    
    _sql_constraints = [
        ('sale_discount_range',
         'CHECK (sale_discount>=0 AND sale_discount<=100)',
         "The Rewards Pricing Discount must be between 0 and 100"),

         ('freight_units_5_to_10_discount_range',
         'CHECK (freight_units_5_to_10_discount>=0 AND freight_units_5_to_10_discount<=100)',
         "The Freight Discount with from 5 to 10 units must be between 0 and 100"),

         ('freight_units_over_10_discount_range',
         'CHECK (freight_units_over_10_discount>=0 AND freight_units_over_10_discount<=100)',
         "The Freight Discount with more than 10 units must be between 0 and 100"),
    ]
