# -*- coding: utf-8 -*-

from odoo import api, models

class flsp_bomstrcreport(models.AbstractModel):
    _name = 'report.flsp_mrp_report_bom_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        for bom_id in docids:
            bom = self.env['mrp.bom'].browse(bom_id)
            candidates = bom.product_id or bom.product_tmpl_id.product_variant_ids
            quantity = float(data.get('quantity', 1))
            for product_variant_id in candidates:
                if data and data.get('childs'):
                    doc = self._get_pdf_line(bom_id, product_id=product_variant_id, qty=quantity, child_bom_ids=json.loads(data.get('childs')))
                else:
                    doc = self._get_pdf_line(bom_id, product_id=product_variant_id, qty=quantity, unfolded=True)
                doc['report_type'] = 'pdf'
                doc['report_structure'] = data and data.get('report_type') or 'all'
                docs.append(doc)
            if not candidates:
                if data and data.get('childs'):
                    doc = self._get_pdf_line(bom_id, qty=quantity, child_bom_ids=json.loads(data.get('childs')))
                else:
                    doc = self._get_pdf_line(bom_id, qty=quantity, unfolded=True)
                doc['report_type'] = 'pdf'
                doc['report_structure'] = data and data.get('report_type') or 'all'
                docs.append(doc)
        return {
            'doc_ids': docids,
            'doc_model': 'mrp.bom',
            'docs': docs,
        }

    @api.model
    def render_html(self,data=None):
        report_obj = self.env['report']
        print('>>>>>>>>>>.....', report_obj)
        report = report_obj._get_report_from_name('flsp_mrp_report_bom_view')
        print('>>>>>>>>>>', report)
        data_array = []

        docargs = {
            'data':data_array,
            }

        return report_obj.render('flsp_mrp_report_bom_view', docargs)
