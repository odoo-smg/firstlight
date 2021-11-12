# -*- coding: utf-8 -*-

import logging
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, tools

_logger = logging.getLogger(__name__)


class approveeconote(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    @api.model
    def _notify_approveeco(self):
        template = self.env.ref('flspmailecoapproval.mail_eco_products_approve', raise_if_not_found=False)

        if not template:
            print('--------------------------template not found')
            _logger.warning('Template "flspmailecoapproval.mail_eco_products_approve" was not found. Cannot send weekly report.')
            return
        # mail_template_id = 'hr_expense.hr_expense_template_register' if expense.employee_id.user_id else 'hr_expense.hr_expense_template_register_no_user'
        # expense_template = self.env.ref(mail_template_id)
        # rendered_body = template.render({'expense': expense}, engine='ir.qweb')

        #default_company_id = self.default_get(['company_id'])['company_id']
        #default_company_id = self.env['res.company']._company_default_get('account.invoice')
        #products = self.env['product.template'].search([('create_date', '<=', date.today() + relativedelta(days=-7)), '|', ('company_id', '=', False), ('company_id', '=', default_company_id)])
        products = self.env['product.template'].search(['|',('flsp_plm_valid', '=', False),('flsp_acc_valid','=',False)])
        total_prd = self.env['product.template'].search_count(['|',('flsp_plm_valid', '=', False),('flsp_acc_valid','=',False)])
        rendered_body = template.render({'products': products, 'totalprd': total_prd}, engine='ir.qweb')
        body = self.env['mail.thread']._replace_local_links(rendered_body)

        if total_prd > 0:
            self.env['mail.mail'].create({
                'body_html': body,
                'subject': 'Validation Reminder - Daily Report',
                'email_to': 'korymccarthy@smartrendmfg.com;andrewmckay@smartrendmfg.com; edlommen@smartrendmfg.com; stephanieaddy@smartrendmfg.com',
                'auto_delete': True,
            }).send()
        print('************ ECO Reminder - Weekly report - DONE ******************')
