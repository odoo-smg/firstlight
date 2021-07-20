# Copyright 2018 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class FlattenedBomXlsx(models.AbstractModel):
    _name = "report.mrp_flattened_bom_xlsx.flattened_bom_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Flattened BOM XLSX"

    def print_flattened_bom_lines(self, bom, requirements, sheet, row):
        candidates = bom.product_id or bom.product_tmpl_id.product_variant_ids
        for product_variant_id in candidates:
            self.print_flattened_bom_lines_product(bom, product_variant_id, requirements, sheet, row)

    def print_flattened_bom_lines_product(self, bom, product_variant_id, requirements, sheet, row):
        print('********************print_flattened_bom_lines_product')
        i = row
        sheet.write(i, 0, bom.product_tmpl_id.name or "")
        sheet.write(i, 1, bom.product_tmpl_id.default_code or "")
        sheet.write(i, 2, bom.product_tmpl_id.default_code or "")
        sheet.write(i, 3, bom.display_name or "")
        sheet.write(i, 4, bom.product_qty)
        sheet.write(i, 5, bom.product_uom_id.name or "")
        sheet.write(i, 6, product_variant_id.virtual_available)
        sheet.write(i, 7, product_variant_id.flsp_available_qty)

        sheet.write(i, 8, bom.product_tmpl_id.standard_price or "")

        sheet.write(i, 9, bom.code or "")
        sheet.write(i, 10, bom.flsp_bom_plm_valid or "")
        sheet.write(i, 11, bom.product_tmpl_id.legacy_code or "")
        sheet.write(i, 12, bom.product_tmpl_id.flsp_plm_valid or "")
        sheet.write(i, 13, bom.product_tmpl_id.tracking or "")
        sheet.write(i, 14, bom.type or "")
        if 'flsp_backflush' in self.env['product.template']._fields:
            sheet.write(i, 15, bom.product_tmpl_id.flsp_backflush or "")
        if 'flsp_mrp_bttn' in self.env['product.template']._fields:
            sheet.write(i, 16, bom.product_tmpl_id.flsp_mrp_bttn or "")

        i += 1
        for product, total_qty in requirements.items():
            sheet.write(i, 1, total_qty['prod'].default_code or "")
            sheet.write(i, 2, total_qty['level']*"|---"+total_qty['prod'].default_code or 0)
            sheet.write(i, 3, total_qty['prod'].display_name or "")
            sheet.write(i, 4, total_qty['total'] or 0.0)
            sheet.write(i, 5, total_qty['prod'].uom_id.name or "")
            sheet.write(i, 6, total_qty['prod'].virtual_available or 0.0)
            sheet.write(i, 7, total_qty['prod'].flsp_available_qty or 0.0)

            sheet.write(i, 8, total_qty['prod'].standard_price or "")

            sheet.write(i, 9, total_qty['bom'] or "")
            sheet.write(i, 10, total_qty['bom_plm'] or "")
            sheet.write(i, 11, total_qty['prod'].legacy_code or "")
            sheet.write(i, 12, total_qty['prod'].flsp_plm_valid or "")
            sheet.write(i, 13, total_qty['prod'].tracking or "")
            sheet.write(i, 14, total_qty['type'] or "")
            if 'flsp_backflush' in self.env['product.template']._fields:
                sheet.write(i, 15, total_qty['prod'].flsp_backflush or "")
            if 'flsp_mrp_bttn' in self.env['product.template']._fields:
                sheet.write(i, 16, total_qty['prod'].flsp_mrp_bttn or "")
            i += 1
        return i

    def generate_xlsx_report(self, workbook, data, objects):
        print('********************generate_xlsx_report')
        workbook.set_properties(
            {"comments": "Created with Python and XlsxWriter from Odoo 13.0"}
        )
        sheet = workbook.add_worksheet(_("Flattened BOM"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(90)
        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 30)
        sheet.set_column(3, 3, 40)
        sheet.set_column(4, 5, 10)
        sheet.set_column(6, 7, 15)

        sheet.set_column(8, 8, 10)

        sheet.set_column(9, 9, 25)
        sheet.set_column(10, 10, 10)
        sheet.set_column(11, 11, 10)
        sheet.set_column(12, 12, 10)
        sheet.set_column(13, 13, 10)
        if 'flsp_backflush' in self.env['product.template']._fields:
            sheet.set_column(14, 14, 10)
        # if 'flsp_mrp_bttn' in self.env['product.template']._fields:
        #     sheet.set_column(12, 12, 11)
        title_style = workbook.add_format(
            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
        )

        # if 'flsp_backflush' and 'flsp_mrp_bttn' in self.env['product.template']._fields:
        if 'flsp_backflush' in self.env['product.template']._fields:
            sheet_title = [
                _("BOM Name"),
                _("Part#"),
                _("Indented Part#"),
                _("Product Name"),
                _("Quantity"),
                _("UoM"),
                _("Forecasted Qty"),
                _("Available Qty"),

                _("cost"),

                _("BOM Reference"),
                _("BOM PLM"),
                _("Legacy Part#"),
                _("Part PLM"),
                _("Tracking"),
                _("Type"),
                _("Backflush"),
                # _("MRP Valid"),
            ]
        else:
            sheet_title = [
                _("BOM Name"),
                _("Part#"),
                _("Indented Part#"),
                _("Product Name"),
                _("Quantity"),
                _("Unit of Measure"),
                _("Forecasted Qty"),
                _("Available Qty"),

                _("Cost"),

                _("BOM Reference"),
                _("BOM PLM"),
                _("Legacy Part#"),
                _("Part PLM"),
                _("Tracking"),
                _("Type"),
            ]

        sheet.set_row(0, None, None, {"collapsed": 1})
        sheet.write_row(1, 0, sheet_title, title_style)
        sheet.freeze_panes(2, 0)
        i = 2

        for o in objects:
            # We need to calculate the totals for the BoM qty and UoM:
            starting_factor = o.product_uom_id._compute_quantity(
                o.product_qty, o.product_tmpl_id.uom_id, round=False
            )
            totals = o._get_flattened_totals(factor=starting_factor)
            # one example of totals: {1: {'total': 1.0, 'level': 1, 'bom': '20210526182104', 'type': 'normal', 'bom_plm': True, 'track': 'none', 'prod': product.product(56,)}, 2: {'total': 1.0, 'level': 2, 'bom': '', 'type': '', 'bom_plm': '', 'track': 'none', 'prod': product.product(44,)}, 3: {'total': 1.0, 'level': 2, 'bom': '', 'type': '', 'bom_plm': '', 'track': 'none', 'prod': product.product(43,)}} 
            i = self.print_flattened_bom_lines(o, totals, sheet, i)
