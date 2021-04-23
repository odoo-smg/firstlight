# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.modules.module import get_module_resource
import base64

class flspcustomerbadge(models.Model):
    _name = 'flsp.customer.badge'
    _inherit = ['image.mixin']
    _description = 'FLSP - customer badge model'

    name = fields.Char(String="Badge Name", required=True)

    image_1920 = fields.Image()
    reward_level = fields.Selection([
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
        ], string='Reward Level', required=True)

    currency_id = fields.Many2one("res.currency", string="Currency", help="Currency of the Annual Program Spend", required=True)
    annual_program_amount = fields.Monetary(string='Annual Program Spend', help="Annual Program Spend for the Reward Level", required=True)

    sale_discount = fields.Float(string='Rewards Pricing Discount (%)', digits='Discount', default=0.0, help="Discount on sale price")
    freight_units_5_to_10_discount = fields.Float(string='Freight Discount with 5-10 units (%)', digits='Discount', default=0.0, help="Frieght discount for orders of from 5 to 10 units")
    freight_units_over_10_discount = fields.Float(string='Freight Discount with more than 10 units (%)', digits='Discount', default=0.0, help="Frieght discount for orders of more than 10 units. 100% Discount means 'Free freight'.")
    
    _sql_constraints = [
         ('name_unique_flsp',
         'UNIQUE(name)',
         "The Name must be unique. Please, check the current list of customer badges."),

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

    def get_image(self, img_name=False):
        # if img_name == False:
        if not img_name:
            return False
        image_path = get_module_resource('flsp-salesorder', 'static/description', img_name)
        return base64.b64encode(open(image_path, 'rb').read())

    @api.onchange('reward_level')
    def _update_badge_image(self):
        if self.reward_level == 'BRONZE':
            self.image_1920 = self.get_image('BronzeDealerBadge.png')
        elif self.reward_level == 'SILVER':
            self.image_1920 = self.get_image('SilverDealerBadge.png')
        elif self.reward_level == 'GOLD':
            self.image_1920 = self.get_image('GoldDealerBadge.png')
        elif self.reward_level == 'PLATINUM':
            self.image_1920 = self.get_image('PlatinumDealerBadge.png')
        else:
            self.image_1920 = False

