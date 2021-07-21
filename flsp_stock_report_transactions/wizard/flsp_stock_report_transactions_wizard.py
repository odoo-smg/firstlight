# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class FlspStockReportTransactionsWiz(models.TransientModel):
    _name = 'flsp_stock_report_transactions.wizard'
    _description = "Wizard: Stock Transactions"

    product_id = fields.Many2one('product.product', string='Product')
    location_id = fields.Many2one('stock.location', string='Location')
    lot_id = fields.Many2one('stock.production.lot', string='Lot/Serial')
    tracking = fields.Char(string="Tracking", compute="_compute_tracking")

    @api.depends('product_id')
    def _compute_tracking(self):
        if self.product_id:
            self.tracking = self.product_id.tracking
        else:
            self.tracking = "none"

    def flsp_report(self):
        [data] = self.read()
        return self.env.ref('flsp_stock_report_transactions.transrep').report_action(self, data=data)


        # self.ensure_one()

        # action = self.env.ref('flsp_stock_report_transactions.flsp_stock_report_transaction_action').read()[0]
        # action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        # return action

    def flsp_report_excel(self):
        [data] = self.read()
        return self.env.ref('flsp_stock_report_transactions.action_flsp_stock_transactions_xlsx').report_action(self, data=data)
