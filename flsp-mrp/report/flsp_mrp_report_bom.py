# -*- coding: utf-8 -*-

from odoo import api, models

class student_status_report_probation(models.AbstractModel):

    @api.multi

   def render_html(self,data=None):

        report_obj = self.env['report']

        print('>>>>>>>>>>.....', report_obj)

        report = report_obj._get_report_from_name('obe_reports_hec.report_student_on_probation')

        print('>>>>>>>>>>', report)

        data_array = []

      docargs = {

            'data':data_array,

            }

      return report_obj.render('obe_reports_hec.report_student_on_probation', docargs)
