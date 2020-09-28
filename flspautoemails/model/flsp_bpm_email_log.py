# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, UserError


class Flspbpmemaillog(models.Model):
    """
    Set emails to the process
    """
    _name = 'flspautoemails.bpmemailslog'
    _description = "BPM Emails Log"

    # User fields
    id = fields.Integer(index=True)
    date_sent = fields.Datetime(string="Date Sent")
    bpmemail_id = fields.Many2one('flspautoemails.bpmemails', string="BPM email ID")
    name = fields.Char(string="Template", )
    subject = fields.Char(string="Subject", help='Python to use dictionary data.')
    email_to = fields.Char(string="To", )
    body = fields.Text(string="Body", )
    status = fields.Selection([('ok', 'success'), ('error', 'error')], string="Status")
    error_msg = fields.Text(string="Error message", )
    object_id = fields.Char(string="Object ID", help='Id of the object sent, saved only in case of error.')
