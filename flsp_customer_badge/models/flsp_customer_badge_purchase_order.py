# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import pytz
from datetime import date, datetime, time, timedelta
from datetime import datetime
from dateutil.tz import tzutc
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import logging
_logger = logging.getLogger(__name__)

class FlspPurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'

    flsp_utc_to_local = fields.Char(string='UTC to Local', compute='compute_local_time')

    @api.model
    def compute_local_time(self, user=None):
        for each in self:
            dt = each.date_planned
            if dt:
                # PRINTS LOCAL TIME OF USER
                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
                dt = pytz.utc.localize(dt).astimezone(user_tz)
            if dt:
                each.flsp_utc_to_local = dt.strftime("%m/%d/%Y")
            else:
                each.flsp_utc_to_local = False
        return dt
