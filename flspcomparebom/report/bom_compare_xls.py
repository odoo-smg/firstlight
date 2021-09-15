from odoo import models


class CompareBomXLS(models.AbstractModel):
    _name = 'report.flspcomparebom.bom_compare_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet("BOM Comparison")
        bold = workbook.add_format({'bold': True})
        sheet.set_column(0, 5, 30)
        sheet.write(0, 0, "BOM 1 Product", bold)
        sheet.write(0, 1, "BOM 1 qty", bold)
        sheet.write(0, 2, "BOM 1 UoM", bold)
        sheet.write(0, 3, "BOM 2 Product", bold)
        sheet.write(0, 4, "BOM 2 qty", bold)
        sheet.write(0, 5, "BOM 2 UoM", bold)
        i=1
        for product in lines.bom_line:
            if(product.product_line_id1.name==False):
                sheet.write(i, 3, '['+str(product.product_line_id2.default_code)+'] '+product.product_line_id2.name, bold)
                sheet.write(i, 4, product.product_line_qty2, bold)
                sheet.write(i, 5, product.uom_id2.name, bold)
            elif(product.product_line_id2.name==False):
                sheet.write(i, 0, '['+str(product.product_line_id1.default_code)+'] ' + product.product_line_id1.name, bold)
                sheet.write(i, 1, product.product_line_qty1, bold)
                sheet.write(i, 2, product.uom_id1.name, bold)
            else:
                sheet.write(i, 0, '['+str(product.product_line_id1.default_code)+'] ' + product.product_line_id1.name, bold)
                sheet.write(i, 1, product.product_line_qty1, bold)
                sheet.write(i, 2, product.uom_id1.name, bold)
                sheet.write(i, 3, '['+str(product.product_line_id2.default_code)+'] ' + product.product_line_id2.name, bold)
                sheet.write(i, 4, product.product_line_qty2, bold)
                sheet.write(i, 5, product.uom_id2.name, bold)
            i+=1
