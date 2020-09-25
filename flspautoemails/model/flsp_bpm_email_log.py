# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, UserError


class Flspbpmemaillog(models.Model):
    """
    Set log of emails processed
    """
    _name = 'flspautoemails.bpmemailslog'
    _description = "BPM Emails Log"

    # User fields
    id = fields.Integer(index=True)
    date_sent = fields.Datetime(string="Date Sent")
    bpmemail_id = fields.Many2one('flspautoemails.bpmemails', string="BPM email ID")
    name = fields.Char(string="Template", required=True)
    subject = fields.Char(string="Subject", required=True, help='Python to use dictionary data.')
    email_to = fields.Char(string="To", required=True)
    body = fields.Text(string="Body", required=True)
    status = fields.Selection([('ok', 'success'), ('error', 'error')], string="Status")
    erro_msg = fields.Text(string="Error message", required=True)
