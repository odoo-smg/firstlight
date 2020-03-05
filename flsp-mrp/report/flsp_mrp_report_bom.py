# -*- coding: utf-8 -*-

from odoo import api, models

class flsp_bomstrcreport(models.AbstractModel):
    _name = 'report.flsp-mrp.flsp_mrp_report_bom_view'

    @api.model
    def render_html(self,data=None):
        report_obj = self.env['report']
        print('>>>>>>>>>>.....', report_obj)
        report = report_obj._get_report_from_name('flsp-mrp.flsp_mrp_report_bom')
        print('>>>>>>>>>>', report)
        data_array = []

        docargs = {
            'data':data_array,
            }

        return report_obj.render('flsp-mrp.flsp_mrp_report_bom', docargs)
