# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class FlspCustomerBadgeRecord(models.Model):
    _name = 'flsp.customer.badge.record'
    _inherit = ['image.mixin']
    _description = 'FLSP - record of customer badge'

    customer_id = fields.Many2one('res.partner', string="Customer", required='True', readonly=True)
    flsp_cb_id = fields.Many2one('flsp.customer.badge', string="Customer Badge", required='True', readonly=True)
    start_date = fields.Date(string='Start Date', required='True', readonly=True)
    end_date = fields.Date(string='End Date', readonly=True)

