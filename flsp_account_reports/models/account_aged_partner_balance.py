# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.tools.misc import format_date
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class report_flsp_account_aged_partner(models.AbstractModel):
    _name = "flsp.account.aged.partner"
    _description = "Aged Partner Balances"
    _inherit = 'flsp.account.report'

    filter_date = {'mode': 'single', 'filter': 'today'}
    filter_unfold_all = False
    filter_partner = True
    order_selected_column = {'default': 0}

    def _get_columns_name(self, options):
        columns = [
            {},
            {'name': _("Due Date"), 'class': 'date', 'style': 'white-space:nowrap;'},
            {'name': _("Journal"), 'class': '', 'style': 'text-align:center; white-space:nowrap;'},
            {'name': _("Account"), 'class': '', 'style': 'text-align:center; white-space:nowrap;'},
            {'name': _("Exp. Date"), 'class': 'date', 'style': 'white-space:nowrap;'},
            {'name': _("As of: %s") % format_date(self.env, options['date']['date_to']), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("1 - 30"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("31 - 60"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("61 - 90"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("91 - 120"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("Older"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("Total"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
        ]
        return columns

    def _get_templates(self):
        templates = super(report_flsp_account_aged_partner, self)._get_templates()
        templates['flsp_main_template'] = 'flsp_account_reports.flsp_template_aged_partner_balance_report'
        try:
            self.env['ir.ui.view'].get_view_id('flsp_account_reports.flsp_template_aged_partner_balance_line_report')
            templates['flsp_line_template'] = 'flsp_account_reports.flsp_template_aged_partner_balance_line_report'
        except ValueError:
            pass
        return templates

    @api.model
    def _get_lines(self, options, line_id=None):
        sign = -1.0 if self.env.context.get('aged_balance') else 1.0
        lines = []
        account_types = [self.env.context.get('account_type')]
        context = {'include_nullified_amount': True}
        if line_id and 'partner_' in line_id:
            # we only want to fetch data about this partner because we are expanding a line
            partner_id_str = line_id.split('_')[1]
            if partner_id_str.isnumeric():
                partner_id = self.env['res.partner'].browse(int(partner_id_str))
            else:
                partner_id = False
            context.update(partner_ids=partner_id)
        results, total, amls = self.env['report.account.report_agedpartnerbalance'].with_context(**context)._flsp_get_partner_move_lines(account_types, self._context['date_to'], 'posted', 30)

        for values in results:
            vals = {
                'id': 'partner_%s' % (values['partner_id'],),
                'name': values['name'],
                'level': 2,
                'columns': [{'name': ''}] * 4 + [{'name': self.format_value(sign * v), 'no_format': sign * v}
                                                 for v in [values['direction'], values['4'],
                                                           values['3'], values['2'],
                                                           values['1'], values['0'], values['total']]],
                'trust': values['trust'],
                'unfoldable': True,
                'unfolded': 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'),
                'partner_id': values['partner_id'],
            }
            lines.append(vals)
            if 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'):
                for line in amls[values['partner_id']]:
                    aml = line['line']
                    if aml.move_id.is_purchase_document():
                        caret_type = 'account.invoice.in'
                    elif aml.move_id.is_sale_document():
                        caret_type = 'account.invoice.out'
                    elif aml.payment_id:
                        caret_type = 'account.payment'
                    else:
                        caret_type = 'account.move'

                    line_date = aml.date_maturity or aml.date
                    if not self._context.get('no_format'):
                        line_date = format_date(self.env, line_date)
                    vals = {
                        'id': aml.id,
                        'name': aml.move_id.name,
                        'class': 'date',
                        'caret_options': caret_type,
                        'level': 4,
                        'parent_id': 'partner_%s' % (values['partner_id'],),
                        'columns': [{'name': v} for v in [format_date(self.env, aml.date_maturity or aml.date), aml.journal_id.code, aml.account_id.display_name, format_date(self.env, aml.expected_pay_date)]] +
                                   [{'name': self.format_value(sign * v, blank_if_zero=True), 'no_format': sign * v} for v in [line['period'] == 6-i and line['amount'] or 0 for i in range(7)]],
                        'action_context': {
                            'default_type': aml.move_id.type,
                            'default_journal_id': aml.move_id.journal_id.id,
                        },
                        'title_hover': self._format_aml_name(aml.name, aml.ref, aml.move_id.name),
                    }
                    lines.append(vals)
        if total and not line_id:
            total_line = {
                'id': 0,
                'name': _('Total'),
                'class': 'total',
                'level': 2,
                'columns': [{'name': ''}] * 4 + [{'name': self.format_value(sign * v), 'no_format': sign * v} for v in [total[6], total[4], total[3], total[2], total[1], total[0], total[5]]],
            }
            lines.append(total_line)
        return lines


class report_flsp_account_aged_receivable(models.AbstractModel):
    _name = "flsp.account.aged.receivable"
    _description = "FLSP Aged Receivable"
    _inherit = "flsp.account.aged.partner"

    def _set_context(self, options):
        ctx = super(report_flsp_account_aged_receivable, self)._set_context(options)
        ctx['account_type'] = 'receivable'
        return ctx

    def _get_report_name(self):
        return _("FLSP Aged Receivable")

    def _get_templates(self):
        templates = super(report_flsp_account_aged_receivable, self)._get_templates()
        templates['flsp_line_template'] = 'flsp_account_reports.flsp_line_template_aged_receivable_report'
        return templates


class report_account_aged_payable(models.AbstractModel):
    _name = "account.aged.payable"
    _description = "Aged Payable"
    _inherit = "flsp.account.aged.partner"

    def _set_context(self, options):
        ctx = super(report_account_aged_payable, self)._set_context(options)
        ctx['account_type'] = 'payable'
        ctx['aged_balance'] = True
        return ctx

    def _get_report_name(self):
        return _("Aged Payable")

    def _get_templates(self):
        templates = super(report_account_aged_payable, self)._get_templates()
        templates['flsp_line_template'] = 'flsp_account_reports.flsp_line_template_aged_payable_report'
        return templates


class FlpsReportAgedPartnerBalance(models.AbstractModel):
    _inherit = "report.account.report_agedpartnerbalance"

    def _flsp_get_partner_move_lines(self, account_type, date_from, target_move, period_length):
        # This method can receive the context key 'include_nullified_amount' {Boolean}
        # Do an invoice and a payment and unreconcile. The amount will be nullified
        # By default, the partner wouldn't appear in this report.
        # The context key allow it to appear
        # In case of a period_length of 30 days as of 2019-02-08, we want the following periods:
        # Name       Stop         Start
        # 1 - 30   : 2019-02-07 - 2019-01-09
        # 31 - 60  : 2019-01-08 - 2018-12-10
        # 61 - 90  : 2018-12-09 - 2018-11-10
        # 91 - 120 : 2018-11-09 - 2018-10-11
        # +120     : 2018-10-10
        ctx = self._context
        periods = {}
        date_from = fields.Date.from_string(date_from)
        start = date_from
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length)
            period_name = str((5-(i+1)) * period_length + 1) + '-' + str((5-i) * period_length)
            period_stop = (start - relativedelta(days=1)).strftime('%Y-%m-%d')
            if i == 0:
                period_name = '+' + str(4 * period_length)
            periods[str(i)] = {
                'name': period_name,
                'stop': period_stop,
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop

        res = []
        total = []
        partner_clause = ''
        cr = self.env.cr
        user_company = self.env.company
        user_currency = user_company.currency_id

        us_currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)

        company_ids = self._context.get('company_ids') or [user_company.id]
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type), date_from, date_from,)
        if ctx.get('partner_ids'):
            partner_clause = 'AND (l.partner_id IN %s)'
            arg_list += (tuple(ctx['partner_ids'].ids),)
        if ctx.get('partner_categories'):
            partner_clause += 'AND (l.partner_id IN %s)'
            partner_ids = self.env['res.partner'].search([('category_id', 'in', ctx['partner_categories'].ids)]).ids
            arg_list += (tuple(partner_ids or [0]),)
        arg_list += (date_from, tuple(company_ids))

        query = '''
            SELECT DISTINCT l.partner_id, res_partner.name AS name, UPPER(res_partner.name) AS UPNAME, CASE WHEN prop.value_text IS NULL THEN 'normal' ELSE prop.value_text END AS trust
            FROM account_move_line AS l
              LEFT JOIN res_partner ON l.partner_id = res_partner.id
              LEFT JOIN ir_property prop ON (prop.res_id = 'res.partner,'||res_partner.id AND prop.name='trust' AND prop.company_id=%s),
              account_account, account_move am
            WHERE (l.account_id = account_account.id)
                AND (l.move_id = am.id)
                AND (am.state IN %s)
                AND (account_account.internal_type IN %s)
                AND (
                        l.reconciled IS FALSE
                        OR l.id IN(
                            SELECT credit_move_id FROM account_partial_reconcile where max_date > %s
                            UNION ALL
                            SELECT debit_move_id FROM account_partial_reconcile where max_date > %s
                        )
                    )
                    ''' + partner_clause + '''
                AND (l.date <= %s)
                AND l.company_id IN %s
            ORDER BY UPPER(res_partner.name)'''
        arg_list = (self.env.company.id,) + arg_list
        cr.execute(query, arg_list)

        partners = cr.dictfetchall()

        # put a total of 0
        for i in range(7):
            total.append(0)

        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
        lines = dict((partner['partner_id'] or False, []) for partner in partners)
        if not partner_ids:
            return [], [], {}

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
            dates_query = '(COALESCE(l.date_maturity,l.date)'

            if periods[str(i)]['start'] and periods[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
            elif periods[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (periods[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (periods[str(i)]['stop'],)
            args_list += (date_from, tuple(company_ids))

            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    AND l.company_id IN %s
                    ORDER BY COALESCE(l.date_maturity, l.date)'''
            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids).with_context(prefetch_fields=False):
                partner_id = line.partner_id.id or False
                if partner_id not in partners_amount:
                    partners_amount[partner_id] = 0.0

                #line_amount = line.company_id.currency_id._convert(line.balance, user_currency, user_company, date_from)
                line_amount = line.amount_currency
                #if print_first and line_amount > 0:
                #tmp = line.company_id.currency_id._convert(line.balance, us_currency_id, user_company, line.date)
                #print("Customer: "+line.partner_id.name[:20]+' ---> before: '+ str(line.balance)+" after: "+str(line_amount) + " date:"+str(date_from)+" move date:"+str(line.date)+'Converted on('+str(line.date)+'): '+str(tmp))
                    #print()
                    #print_first = False
                if user_currency.is_zero(line_amount):
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.max_date <= date_from:
                        #line_amount += partial_line.company_id.currency_id._convert(partial_line.amount, user_currency, user_company, date_from)
                        line_amount += partial_line.amount_currency
                for partial_line in line.matched_credit_ids:
                    if partial_line.max_date <= date_from:
                        #line_amount -= partial_line.company_id.currency_id._convert(partial_line.amount, user_currency, user_company, date_from)
                        line_amount -= partial_line.amount_currency

                if not self.env.company.currency_id.is_zero(line_amount):
                    partners_amount[partner_id] += line_amount
                    lines.setdefault(partner_id, [])
                    lines[partner_id].append({
                        'line': line,
                        'amount': line_amount,
                        'period': i + 1,
                        })
            history.append(partners_amount)

        # This dictionary will store the not due amount of all partners
        undue_amounts = {}
        query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND (COALESCE(l.date_maturity,l.date) >= %s)\
                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                AND (l.date <= %s)
                AND l.company_id IN %s
                ORDER BY COALESCE(l.date_maturity, l.date)'''
        cr.execute(query, (tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from, tuple(company_ids)))
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        for line in self.env['account.move.line'].browse(aml_ids):
            partner_id = line.partner_id.id or False
            if partner_id not in undue_amounts:
                undue_amounts[partner_id] = 0.0
            #line_amount = line.company_id.currency_id._convert(line.balance, user_currency, user_company, date_from)
            line_amount = line.company_id.currency_id._convert(line.balance, us_currency_id, user_company, line.date)
            if user_currency.is_zero(line_amount):
                continue
            for partial_line in line.matched_debit_ids:
                if partial_line.max_date <= date_from:
                    #line_amount += partial_line.company_id.currency_id._convert(partial_line.amount, user_currency, user_company, date_from)
                    line_amount += partial_line.company_id.currency_id._convert(partial_line.amount, us_currency_id, user_company, partial_line.max_date)
            for partial_line in line.matched_credit_ids:
                if partial_line.max_date <= date_from:
                    #line_amount -= partial_line.company_id.currency_id._convert(partial_line.amount, user_currency, user_company, date_from)
                    line_amount -= partial_line.company_id.currency_id._convert(partial_line.amount, us_currency_id, user_company, partial_line.max_date)
            if not self.env.company.currency_id.is_zero(line_amount):
                undue_amounts[partner_id] += line_amount
                lines.setdefault(partner_id, [])
                lines[partner_id].append({
                    'line': line,
                    'amount': line_amount,
                    'period': 6,
                })

        for partner in partners:
            if partner['partner_id'] is None:
                partner['partner_id'] = False
            at_least_one_amount = False
            values = {}
            undue_amt = 0.0
            if partner['partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
                undue_amt = undue_amounts[partner['partner_id']]

            total[6] = total[6] + undue_amt
            values['direction'] = undue_amt
            if not float_is_zero(values['direction'], precision_rounding=self.env.company.currency_id.rounding):
                at_least_one_amount = True

            for i in range(5):
                during = False
                if partner['partner_id'] in history[i]:
                    during = [history[i][partner['partner_id']]]
                # Adding counter
                total[(i)] = total[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
                if not float_is_zero(values[str(i)], precision_rounding=self.env.company.currency_id.rounding):
                    at_least_one_amount = True
            values['total'] = sum([values['direction']] + [values[str(i)] for i in range(5)])
            # Add for total
            total[(i + 1)] += values['total']
            values['partner_id'] = partner['partner_id']
            if partner['partner_id']:
                values['name'] = len(partner['name']) >= 45 and partner['name'][0:40] + '...' or partner['name']
                values['trust'] = partner['trust']
            else:
                values['name'] = _('Unknown Partner')
                values['trust'] = False

            if at_least_one_amount or (self._context.get('include_nullified_amount') and lines[partner['partner_id']]):
                res.append(values)
        return res, total, lines

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        total = []
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        target_move = data['form'].get('target_move', 'all')
        date_from = fields.Date.from_string(data['form'].get('date_from')) or fields.Date.today()

        if data['form']['result_selection'] == 'customer':
            account_type = ['receivable']
        elif data['form']['result_selection'] == 'supplier':
            account_type = ['payable']
        else:
            account_type = ['payable', 'receivable']

        movelines, total, dummy = self._flsp_get_partner_move_lines(account_type, date_from, target_move, data['form']['period_length'])
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_partner_lines': movelines,
            'get_direction': total,
            'company_id': self.env['res.company'].browse(
                data['form']['company_id'][0]),
        }
