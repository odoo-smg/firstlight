# -*- coding: utf-8 -*-

import logging
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, tools

_logger = logging.getLogger(__name__)


class newprodemail(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    @api.model
    def _notify_newproducts(self):
        template = self.env.ref('flspmfg.mail_new_products_weekly', raise_if_not_found=False)

        if not template:
            print('--------------------------template not found')
            _logger.warning('Template "flspmfg.mail_new_products_weekly" was not found. Cannot send weekly report.')
            return
        # mail_template_id = 'hr_expense.hr_expense_template_register' if expense.employee_id.user_id else 'hr_expense.hr_expense_template_register_no_user'
        # expense_template = self.env.ref(mail_template_id)
        # rendered_body = template.render({'expense': expense}, engine='ir.qweb')

        #default_company_id = self.default_get(['company_id'])['company_id']
        #default_company_id = self.env['res.company']._company_default_get('account.invoice')
        #products = self.env['product.template'].search([('create_date', '<=', date.today() + relativedelta(days=-7)), '|', ('company_id', '=', False), ('company_id', '=', default_company_id)])
        products = self.env['product.template'].search([('create_date', '>=', date.today() + relativedelta(days=-7))])
        total_prd = self.env['product.template'].search_count([('create_date', '>=', date.today() + relativedelta(days=-7))])

        #rendered_body = template.render({'products': products}, engine='ir.qweb')
        rendered_body = template._render({'products': products}, engine='ir.qweb')
        #body = self.env['mail.thread']._replace_local_links(rendered_body)
        body = self.env['mail.render.mixin']._replace_local_links(rendered_body)

        if total_prd > 0:
            self.env['mail.mail'].create({
                'body_html': body,
                'subject': 'New Products - Weekly Report',
                'email_to': 'alexandresousa@smartrendmfg.com;andrewmckay@smartrendmfg.com',
                'auto_delete': True,
            }).send()
        print('************ New Products - Weekly report - DONE ******************')
