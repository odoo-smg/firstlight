# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FlspTktMsg(models.Model):
    """
        class_name: FlspTktMsg
        model_name: inherits the ticket model and mail for charter
        Purpose:    To add a data sheets to the product
        Date:       Dec/22st/2020/Tuesday
        Author:     Sami Byaruhanga

    """
    _name = 'flspticketsystem.ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'flspticketsystem.ticket']
    _rec_name = "id"

    id = fields.Integer(index=True)
    start_date = fields.Date(string="Request date", default=fields.Date.today, required=True, tracking=True,
        help='Request date is set to default on today\'s date')
    assign_date = fields.Date(string="Assign Date", tracking=True)