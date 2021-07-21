# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class FlspStockReportTransactionsXlsx(models.AbstractModel):
    _name = 'report.flsp_stock_report_transactions.transrep_xlsx'
    _inherit = "report.report_xlsx.abstract"
    _description = 'FLSP - Stock Transactions Excel'

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties(
            {"comments": "Created with Python and XlsxWriter from Odoo 13.0"}
        )
        
        self.generate_introduction(workbook, data)
        self.generate_stock_transaction_content(workbook, data)

    def generate_introduction(self, workbook, input_data):
        # create introduction sheet
        sheet = workbook.add_worksheet(_("Transaction Selections"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(90)
        
        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 65)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)
        
        title_style = workbook.add_format(
            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
        )

        sheet_title = [
                _("Location"),
                _("Product"),
                _("Tracking"),
                _("Lot/Serial #"),
        ]

        sheet.set_row(0, None, None, {"collapsed": 1})
        sheet.write_row(1, 0, sheet_title, title_style)

        sheet.write(2, 0, input_data.get('location_id')[1] or "")
        sheet.write(2, 1, input_data.get('product_id')[1] or "")
        sheet.write(2, 2, input_data.get('tracking') or "")
        lot = ""
        if input_data.get('lot_id'):
            lot = input_data.get('lot_id')[1]
        sheet.write(2, 3, lot)

    def generate_stock_transaction_content(self, workbook, input_data):
        # get content data at first
        transactions = self.env['report.flsp_stock_report_transactions.transrep']._get_report_values(False, data=input_data)

        # create sheet for content
        sheet = workbook.add_worksheet(_("Stock Transactions"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(90)

        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 25)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        
        title_style = workbook.add_format(
            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
        )

        sheet_title = [
                _("Date"),
                _("Reference"),
                _("Origin"),
                _("Lot/Serial"),
                _("Quantity"),
                _("Operation"),
                _("Balance"),
        ]

        sheet.set_row(0, None, None, {"collapsed": 1})
        sheet.write_row(1, 0, sheet_title, title_style)
        sheet.freeze_panes(2, 0)
        i = 2
        for trans in transactions.get('data'):
            sheet.write(i, 0, trans[1].strftime('%m/%d/%Y') or "")
            sheet.write(i, 1, trans[2] or "")
            sheet.write(i, 2, trans[3] or "")
            sheet.write(i, 3, trans[6] or "")
            sheet.write(i, 4, trans[7] or 0)
            sheet.write(i, 5, trans[8] or "")
            sheet.write(i, 6, trans[9] or 0)
            i += 1

