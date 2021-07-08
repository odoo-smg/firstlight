from odoo import models
from odoo.tools.translate import _

import logging
_logger = logging.getLogger(__name__)

class MrpComponentFinishedProductXlsx(models.AbstractModel):
    _name = "report.flsp_mrp_component_finished_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Components x Finished Products XLSX"

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties(
            {"comments": "Created with Python and XlsxWriter from Odoo 13.0"}
        )

        for o in objects:
            self.generate_mrp_introduction(workbook, o)
            self.generate_mrp_component_finished_product(workbook, o)
            
    def generate_mrp_introduction(self, workbook, mo):
        # create introduction sheet
        sheet = workbook.add_worksheet(_(mo.name))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(90)
        
        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 65)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 10)
        sheet.set_column(4, 4, 20)
        sheet.set_column(5, 5, 20)
        
        title_style = workbook.add_format(
            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
        )

        sheet_title = [
                _("Name"),
                _("Finished Product"),
                _("Quantity to Produce"),
                _("UoM"),
                _("Source Document"),
                _("Responsible"),
        ]

        sheet.set_row(0, None, None, {"collapsed": 1})
        sheet.write_row(1, 0, sheet_title, title_style)
        
        sheet.write(2, 0, mo.name)
        sheet.write(2, 1, mo.product_id.display_name or "")
        sheet.write(2, 2, mo.product_qty or 0)
        sheet.write(2, 3, mo.product_uom_id.name)
        sheet.write(2, 4, mo.origin)
        sheet.write(2, 5, mo.user_id.name)

    def generate_mrp_component_finished_product(self, workbook, mo):
        # create sheet for components and finished products
        sheet = workbook.add_worksheet(_("Components_FinishedProducts(FP)"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(90)

        sheet.set_column(0, 0, 65)
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 10)
        sheet.set_column(3, 3, 10)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 10)
        sheet.set_column(7, 7, 10)
        
        title_style = workbook.add_format(
            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
        )

        sheet_title = [
                _("Product"),
                _("Lot/Serial #"),
                _("Qty"),
                _("UoM"),
                _("Location"),
                _("Lot/Serial #(FP)"),
                _("Qty(FP)"),
                _("UoM(FP)"),
        ]

        sheet.set_row(0, None, None, {"collapsed": 1})
        sheet.write_row(1, 0, sheet_title, title_style)
        sheet.freeze_panes(2, 0)
        i = 2
        if mo.move_raw_ids:
            for move_id in mo.move_raw_ids:
                if move_id.move_line_ids:
                    for move_line in move_id.move_line_ids:
                        sheet.write(i, 0, move_line.product_id.display_name or "")
                        sheet.write(i, 1, move_line.lot_id.name or " ")
                        if mo.state == 'done':
                            sheet.write(i, 2, move_line.qty_done or 0)
                        else:
                            sheet.write(i, 2, move_line.product_uom_qty or 0)
                        sheet.write(i, 3, move_line.product_uom_id.name or "")
                        sheet.write(i, 4, move_line.location_id.complete_name or "")
                        sheet.write(i, 5, move_line.lot_produced_ids.name or "")
                        sheet.write(i, 6, move_line.lot_produced_ids.product_qty or 0)
                        sheet.write(i, 7, move_line.lot_produced_ids.product_uom_id.name or "")
                        i += 1
                else:
                    sheet.write(i, 0, move_id.product_id.display_name or "")
                    sheet.write(i, 1, " ")
                    sheet.write(i, 2, move_id.product_uom_qty or 0)
                    sheet.write(i, 3, move_id.product_uom.name or "")
                    sheet.write(i, 4, move_id.location_id.complete_name or "")
                    sheet.write(i, 5, "")
                    sheet.write(i, 6, mo.product_qty or 0)
                    sheet.write(i, 7, mo.product_uom_id.name or "")
                    i += 1
