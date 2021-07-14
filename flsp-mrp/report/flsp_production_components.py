from odoo import models
from odoo.tools.translate import _

import logging
_logger = logging.getLogger(__name__)

class MrpComponentsXlsx(models.AbstractModel):
    _name = "report.flsp_mrp_components_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Components XLSX"

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties(
            {"comments": "Created with Python and XlsxWriter from Odoo 13.0"}
        )

        for o in objects:
            self.generate_mrp_introduction(workbook, o)
            self.generate_mrp_components(workbook, o)

    
    def generate_mrp_introduction(self, workbook, mo):
        # create introduction sheet
        sheet = workbook.add_worksheet(_(mo.name))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(90)
        
        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 45)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 10)
        sheet.set_column(4, 4, 20)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        
        title_style = workbook.add_format(
            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
        )

        sheet_title = [
                _("Name"),
                _("Product"),
                _("Qty to Produce"),
                _("UoM"),
                _("Bill of Material"),
                _("Source Document"),
                _("Responsible"),
        ]

        sheet.set_row(0, None, None, {"collapsed": 1})
        sheet.write_row(1, 0, sheet_title, title_style)
        
        sheet.write(2, 0, mo.name or "")
        sheet.write(2, 1, mo.product_id.display_name or "")
        sheet.write(2, 2, mo.product_qty or 0)
        sheet.write(2, 3, mo.product_uom_id.name or "")
        sheet.write(2, 4, mo.bom_id.code or "")
        sheet.write(2, 5, mo.origin or "")
        sheet.write(2, 6, mo.user_id.name or "")

    def generate_mrp_components(self, workbook, mo):
        # create sheet for components
        sheet = workbook.add_worksheet(_("Components"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(90)

        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 45)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 10)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 10)
        sheet.set_column(7, 7, 10)
        
        title_style = workbook.add_format(
            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
        )

        sheet_title = [
                _("Part #"),
                _("Name"),
                _("Unit of Measure"),
                _("Backflush"),
                _("Tracking"),
                _("To consume"),
                _("Reserved"),
                _("Consumed"),
        ]

        sheet.set_row(0, None, None, {"collapsed": 1})
        sheet.write_row(1, 0, sheet_title, title_style)
        sheet.freeze_panes(2, 0)
        i = 2
        if mo.move_raw_ids:
            for move_id in mo.move_raw_ids:
                sheet.write(i, 0, move_id.product_id.default_code or "")
                sheet.write(i, 1, move_id.product_id.name or "")
                sheet.write(i, 2, move_id.product_uom.name or "")
                sheet.write(i, 3, move_id.flsp_backflush or "")
                sheet.write(i, 4, move_id.has_tracking or "")
                sheet.write(i, 5, move_id.product_uom_qty or 0)
                sheet.write(i, 6, move_id.reserved_availability or 0)
                sheet.write(i, 7, move_id.quantity_done or 0)
                i += 1
