# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from datetime import datetime,timedelta
from firstlight.flspautomation.product import FlspProductAutomation

from odoo import tools

import logging
_logger = logging.getLogger(__name__)

@tagged('flsp', 'flspmodel', '-standard')
class TestNegativeForecast(TransactionCase):
    
    def setUp(self):
        """ set up for all test cases """
        # call parent setUp()adge(self):
        super(TestNegativeForecast, self).setUp()
        # create referred models used in test cases
        self.report_stock_quant = self.env['report.stock.quantity']
        self.negative_forecast = self.env['flsp.negative.forecast.stock']
        self.product_auto = FlspProductAutomation(self)

    def create_table(self):
        query = """
CREATE TABLE test_table(
    id        INT,
    product_id        INT,
    state    VARCHAR(20),
    date    date,
    product_qty    DOUBLE PRECISION,
    company_id    INT,
    warehouse_id    INT
)
"""
        self.env.cr.execute(query)

    def drop_table(self):
        tools.drop_view_if_exists(self.env.cr, 'report_stock_quantity')
        self.env.cr.execute(""" 
            DROP TABLE test_table
        """)

        
    def add_forecast_entry_in_report(self, product_id, state, date, product_qty, company_id):
        query = """
                    INSERT INTO test_table(id, product_id, state, date, product_qty, company_id) 
                                    VALUES(100000, %s, %s, %s, %s, %s)
                """
        query_params = (product_id, state, date, product_qty, company_id)
        self.env.cr.execute(query, query_params)

        
    def init_report_stock_quantity(self):
        tools.drop_view_if_exists(self.env.cr, 'report_stock_quantity')
        query = """
                    CREATE or REPLACE VIEW report_stock_quantity AS (
                        SELECT * FROM test_table
                    )
                """
        self.env.cr.execute(query)

    def test_negative_forecast_report(self):
        # test when user inputs different kinds of INVALID 'package_id' in the sql in the method

        # prepare test data
        self.create_table()

        company_id = self.env.company.id
        fmt  = '%Y-%m-%d'
        now = datetime.now()
        # qty of prod_1 is always positive
        prod_1 = self.product_auto.create_typical_product('test_negative_forecast_report', 1.3, 10)
        self.add_forecast_entry_in_report(prod_1.id, 'forecast', datetime.strptime('2021-06-01', fmt), 10, company_id)
        self.add_forecast_entry_in_report(prod_1.id, 'in', now, 1, company_id)
        self.add_forecast_entry_in_report(prod_1.id, 'forecast', now, 11, company_id)
        
        # qty of prod_2 is only negative in past
        prod_2 = self.product_auto.create_typical_product('test_negative_forecast_report', 4, 12)
        self.add_forecast_entry_in_report(prod_2.id, 'forecast', datetime.strptime('2021-06-02', fmt), -5, company_id)
        self.add_forecast_entry_in_report(prod_2.id, 'in', now, 6, company_id)
        self.add_forecast_entry_in_report(prod_2.id, 'forecast', now, 1, company_id)
        
        # qty of prod_3 is negative now
        prod_3 = self.product_auto.create_typical_product('test_negative_forecast_report', 4, -3)
        self.add_forecast_entry_in_report(prod_3.id, 'forecast', now, -3, company_id)
        self.add_forecast_entry_in_report(prod_3.id, 'out', now + timedelta(days = 1) , 3, company_id)
        self.add_forecast_entry_in_report(prod_3.id, 'forecast', now + timedelta(days = 1), -6, company_id)
        
        # qty of prod_4 is postive now , negative tomorrow and then positve later
        prod_4 = self.product_auto.create_typical_product('test_negative_forecast_report', 4, -2)
        self.add_forecast_entry_in_report(prod_4.id, 'forecast', now, 2, company_id)
        self.add_forecast_entry_in_report(prod_4.id, 'out', now + timedelta(days = 1) , 10, company_id)
        self.add_forecast_entry_in_report(prod_4.id, 'forecast', now + timedelta(days = 1), -8, company_id)
        self.add_forecast_entry_in_report(prod_4.id, 'forecast', now + timedelta(days = 22), -8, company_id)
        self.add_forecast_entry_in_report(prod_4.id, 'in', now + timedelta(days = 30), 100, company_id)
        self.add_forecast_entry_in_report(prod_4.id, 'forecast', now + timedelta(days = 30), 92, company_id)
        
        # update view for test
        self.init_report_stock_quantity()

        # call the method and verify
        self.negative_forecast._update_data()

        # verfiy data with prod_3 and prod_4
        neg_forecast_entries = self.negative_forecast.search([])
        self.assertEquals(2, len(neg_forecast_entries), "len of neg_forecast_entries")

        p1 = neg_forecast_entries[0]
        self.assertEquals(prod_3.id, p1.product_id.id, "product_id")
        self.assertEquals(-3, p1.negative_forecast_qty, "negative_forecast_qty")
        self.assertEquals(now.strftime(fmt), p1.negative_forecast_date.strftime(fmt), "negative_forecast_date")
        self.assertEquals(False, p1.non_negative_forecast_qty, "non_negative_forecast_qty")
        self.assertEquals(0, p1.non_negative_forecast_date, "non_negative_forecast_date")
        self.assertEquals(0, p1.duration, "duration")

        p2 = neg_forecast_entries[1]
        self.assertEquals(prod_4.id, p2.product_id.id, "product_id")
        self.assertEquals(-8, p2.negative_forecast_qty, "negative_forecast_qty")
        self.assertEquals((now + timedelta(days = 1)).strftime(fmt), p2.negative_forecast_date.strftime(fmt), "negative_forecast_date")
        self.assertEquals(92, p2.non_negative_forecast_qty, "non_negative_forecast_qty")
        self.assertEquals((now + timedelta(days = 30)).strftime(fmt), p2.non_negative_forecast_date.strftime(fmt), "non_negative_forecast_date")
        self.assertEquals(30-1, p2.duration, "duration")
        
        # clean db
        self.drop_table()

        # add info to make sure the test case is done
        _logger.info("test_negative_forecast_report() is done.")