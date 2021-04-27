# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import Form
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from datetime import date, datetime
from psycopg2.errors import UniqueViolation

import logging
_logger = logging.getLogger(__name__)

@tagged('flsp', 'flspmodel', '-standard')
class TestOnCustomerBadge(TransactionCase):

    def setUp(self):
        """ set up for all test cases """
        # call parent setUp()adge(self):
        super(TestOnCustomerBadge, self).setUp()
        # create referred models used in test cases
        self.currency_model = self.env['res.currency']

    def create_customer_badge(self, name, rewardLevel, currencyId, annualPprogramAmount, saleDiscount, freightDiscount1, freightDiscount2):
        badge_form = Form(self.env['flsp.customer.badge'].with_context(tracking_disable=True))
        badge_form.name = name
        badge_form.reward_level = rewardLevel
        badge_form.currency_id = currencyId
        badge_form.annual_program_amount = annualPprogramAmount
        badge_form.sale_discount = saleDiscount
        badge_form.freight_units_5_to_10_discount = freightDiscount1
        badge_form.freight_units_over_10_discount = freightDiscount2
        return badge_form.save()
        
    def test_create_customer_badge_ok(self):
        """ Test creation of a normal customer badge """
        # prepare test data
        postfix = str(datetime.now())
        aName = 'customerBadge-' + postfix
        aRewardLevel = 'SILVER'
        aCurrency = self.currency_model.search([('name', '=', 'USD')])[0]
        aAnnual_program_amount = 10000
        aSaleDiscount = 5
        aFreight_units_5_to_10_discount = 10
        aFreight_units_over_10_discount = 15

        # create badge cb
        cb = self.create_customer_badge(aName, aRewardLevel, aCurrency, aAnnual_program_amount, aSaleDiscount, aFreight_units_5_to_10_discount, aFreight_units_over_10_discount)

        # validate the result
        self.assertEquals(aName, 
                        cb.name, 
                        "bage name")
        self.assertEquals(aRewardLevel, 
                        cb.reward_level, 
                        "Reward Level")
        self.assertEquals(aCurrency, 
                        cb.currency_id, 
                        "Currency")
        self.assertEquals(aAnnual_program_amount, 
                        cb.annual_program_amount, 
                        "Annual Program Spend")
        self.assertEquals(aSaleDiscount, 
                        cb.sale_discount, 
                        "Rewards Pricing Discount")
        self.assertEquals(aFreight_units_5_to_10_discount, 
                        cb.freight_units_5_to_10_discount, 
                        "Freight Discount with 5-10 units")
        self.assertEquals(aFreight_units_over_10_discount, 
                        cb.freight_units_over_10_discount, 
                        "Freight Discount with more than 10 units")
        
        # add info to make sure the test case is done
        _logger.info("test_create_customer_ok() is done.")
        
    def test_name_absent(self):
        """ Test badge without name """
        # prepare test data
        aRewardLevel = 'SILVER'
        aCurrency = self.currency_model.search([('name', '=', 'USD')])[0]
        aAnnual_program_amount = 10000
        aSaleDiscount = 5
        aFreight_units_5_to_10_discount = 10
        aFreight_units_over_10_discount = 15

        # validate the result
        self.assertRaises(AssertionError, self.create_customer_badge, False, aRewardLevel, aCurrency, aAnnual_program_amount, aSaleDiscount, aFreight_units_5_to_10_discount, aFreight_units_over_10_discount)
        
        # add info to make sure the test case is done
        _logger.info("test_name_absent() is done.")
        
    def test_duplicated_name(self):
        """ Test badge with duplicated name """
        # prepare test data
        postfix = str(datetime.now())
        aName = 'customerBadge-' + postfix
        aRewardLevel = 'SILVER'
        aCurrency = self.currency_model.search([('name', '=', 'USD')])[0]
        aAnnual_program_amount = 10000
        aSaleDiscount = 5
        aFreight_units_5_to_10_discount = 10
        aFreight_units_over_10_discount = 15

        # create badge cb1
        cb1 = self.create_customer_badge(aName, aRewardLevel, aCurrency, aAnnual_program_amount, aSaleDiscount, aFreight_units_5_to_10_discount, aFreight_units_over_10_discount)

        # validate the result
        self.assertRaises(UniqueViolation, self.create_customer_badge, aName, aRewardLevel, aCurrency, aAnnual_program_amount, aSaleDiscount, aFreight_units_5_to_10_discount, aFreight_units_over_10_discount)
        
        # add info to make sure the test case is done
        _logger.info("test_duplicated_name() is done.")
        
    def test_sale_discount_smallerThan0(self):
        """ Test sale_discount < 0 """
        # prepare test data
        postfix = str(datetime.now())
        aName = 'customerBadge-' + postfix
        aRewardLevel = 'SILVER'
        aCurrency = self.currency_model.search([('name', '=', 'USD')])[0]
        aAnnual_program_amount = 10000
        aSaleDiscount = -1
        aFreight_units_5_to_10_discount = 10
        aFreight_units_over_10_discount = 15

        # validate the result
        self.assertRaises(AssertionError, self.create_customer_badge, False, aRewardLevel, aCurrency, aAnnual_program_amount, aSaleDiscount, aFreight_units_5_to_10_discount, aFreight_units_over_10_discount)
        
        # add info to make sure the test case is done
        _logger.info("test_sale_discount_smallerThan0() is done.")

    def test_sale_discount_biggerThan100(self):
        """ Test sale_discount > 100 """
        # prepare test data
        postfix = str(datetime.now())
        aName = 'customerBadge-' + postfix
        aRewardLevel = 'SILVER'
        aCurrency = self.currency_model.search([('name', '=', 'USD')])[0]
        aAnnual_program_amount = 10000
        aSaleDiscount = 101
        aFreight_units_5_to_10_discount = 10
        aFreight_units_over_10_discount = 15

        # validate the result
        self.assertRaises(AssertionError, self.create_customer_badge, False, aRewardLevel, aCurrency, aAnnual_program_amount, aSaleDiscount, aFreight_units_5_to_10_discount, aFreight_units_over_10_discount)
        
        # add info to make sure the test case is done
        _logger.info("test_sale_discount_biggerThan100() is done.")
