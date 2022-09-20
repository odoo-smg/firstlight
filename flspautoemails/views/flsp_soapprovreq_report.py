# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import api, models


class ReportSalesbysalesperson(models.AbstractModel):
    _name = 'report.flspautoemails.flsp_rep_soapprovreq_new'
    _description = 'Approval Request'

    @api.model
    def _get_report_values(self, docids, data=None):
        sale_orders = self.env['sale.order'].search([('id', 'in', docids)])

        d_from = date.today()

        return {
            'd_from': d_from,
            'docids': sale_orders,
        }
