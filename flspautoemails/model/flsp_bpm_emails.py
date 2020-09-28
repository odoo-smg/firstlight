# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class Flspbpmemails(models.Model):
    """
    Set emails to the process
    """
    _name = 'flspautoemails.bpmemails'
    _description = "BPM Emails"

    # User fields
    id = fields.Integer(index=True)
    email_active = fields.Boolean(string="Email Active")
    description = fields.Char(string="Description", required=True)
    subject = fields.Char(string="Subject", required=True, help='Python to use dictionary data.')
    condition = fields.Text(string="Condition to run", help='Python code to return a condition to run.', default='result=True')
    name = fields.Char(string="Template", required=True)
    system_fields = fields.Text(string="System Fields", help='Python to use dictionary data.')
    extra_emails = fields.Char(string="Extra emails", help='Type the emails with ; to separate them.')
    test_email = fields.Char(string="Test email", help='Type the email to receive by clicking on Send test button.')
    current_user = fields.Boolean(string="Copy Current User")
    dictionary = fields.Text(string="Dictionary", help='Variables to be used on XML. Use "model" to refer to your Self obejct')
    dict_preview = fields.Text(string="Dic. Preview", help='Variables to be used on preview.')
    email_body = fields.Text(string="Email Body", help='Use dictionary data as variables')
    email_preview = fields.Text(string="Email Preview")
    user_ids = fields.Many2many('res.users', 'flspautoemails_bpmemails_users_rel', string="Users To receive",
                    help='Include here the users that must receive email from this template.')

    @api.model
    def get_emails(self, model, context, save_log=False):
        emails_to = ''
        email_to_add = self._rule_eval(self.system_fields, model, context, save_log)
        if email_to_add:
            emails_to = email_to_add
        if self.extra_emails:
            if not emails_to == '':
                emails_to += '; ' + self.extra_emails
            else:
                emails_to = self.extra_emails
        if self.current_user:
            current_email = self.env['res.users'].browse(self._uid).login
            if current_email not in emails_to:
                if not emails_to == '':
                    emails_to += '; ' + current_email
                else:
                    emails_to = current_email
        for email_to_user in self.user_ids:
            if email_to_user.login not in emails_to:
                if not emails_to == '':
                    emails_to += '; ' + email_to_user.login
                else:
                    emails_to = email_to_user.login

        if emails_to == '':
            emails_to = False
        return emails_to

    @api.model
    def _rule_eval(self, rule, model=None, dict=None, save_log=False):
        if rule:
            context = {'model': model,
                       'dictionary': dict,
                'self': self,
                'object': self.id,
                'pool': self.pool,
                'cr': self._cr,
                'uid': self._uid,
                }
            try:
                safe_eval(rule,
                          context,
                          mode='exec',
                          nocopy=True)  # nocopy allows to return 'result'
            except Exception:
                if save_log:
                    log = self.env['flspautoemails.bpmemailslog'].create({
                        'date_sent': datetime.now(),
                        'bpmemail_id': self.id,
                        'name': self.name,
                        'subject': '',
                        'email_to': '',
                        'body': '',
                        'status': 'error',
                        'error_msg': 'Error trying to evaluate the code: ' + rule,
                    })
                    pass
                else:
                    raise ValidationError("Wrong python code defined for BPM Emails="+self.name+". Code:" + rule)
                return False
            return context.get('result', False)

    def update_preview(self):
        context = self._rule_eval(self.dict_preview, self)
        condition = self._rule_eval(self.condition, self, context)
        if not condition:
            self.email_preview = 'condition to run not met'
            return
        email_to = self.get_emails(self, context)
        subject = self._rule_eval(self.subject, self, context)
        if subject:
            body = "<p> Subject: " + subject + "</p>"
        else:
            body = "<p> Subject: **** attention, no subject set ****</p>"
        if email_to:
            body += "<p> Email To: " + email_to + "</p>"
        else:
            body += "<p> Email To: **** attention, no email set ****</p>"
        body += "<p>-----------------------------------------" + "</p>"
        body_calc = self._rule_eval(self.email_body, self, context)
        if body_calc:
            body += self._rule_eval(self.email_body, self, context)

        self.email_preview = body

    def send_email(self, model, template):
        bpm_email = self.env['flspautoemails.bpmemails'].search([('name', '=', template)])
        result = True
        if bpm_email.exists():
            if bpm_email.email_active:
                context = bpm_email._rule_eval(bpm_email.dictionary, model, None, True)
                condition = self._rule_eval(self.condition, model, context, True)
                if not condition:
                    return result
                email_to = bpm_email.get_emails(model, context, True)
                subject = bpm_email._rule_eval(bpm_email.subject, model, context, True)
                body = bpm_email._rule_eval(bpm_email.email_body, model, context, True)

                if email_to and subject and body:
                    self.env['mail.mail'].create({
                        'body_html': body,
                        'subject': subject,
                        'email_to': email_to,
                        'auto_delete': True,
                    }).send()
                    #create a log
                    log = self.env['flspautoemails.bpmemailslog'].create({
                        'date_sent': datetime.now(),
                        'bpmemail_id': bpm_email.id,
                        'name': bpm_email.name,
                        'subject': subject,
                        'email_to': email_to,
                        'body': body,
                        'status': 'ok',
                    })
                    result = True
                else:
                    log_model_id = 0
                    if model.id:
                        log_model_id = model.id
                    #create a log
                    log = self.env['flspautoemails.bpmemailslog'].create({
                        'date_sent': datetime.now(),
                        'bpmemail_id': bpm_email.id,
                        'name': bpm_email.name,
                        'subject': subject,
                        'email_to': email_to,
                        'body': body,
                        'object_id': log_model_id,
                        'status': 'error',
                        'error_msg': 'some of the objects could not be processed',
                    })
                    result = False
        return result

    def send_test(self):
        context = self._rule_eval(self.dict_preview, self)
        email_to = self.test_email
        subject = "Test email ("+self.name+"): "+self._rule_eval(self.subject, self, context)
        body = self._rule_eval(self.email_body, self, context)
        condition = self._rule_eval(self.condition, self, context)
        if condition:
            if email_to:
                self.env['mail.mail'].create({
                    'body_html': body,
                    'subject': subject,
                    'email_to': email_to,
                    'auto_delete': True,
                }).send()
