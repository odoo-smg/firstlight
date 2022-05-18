# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class FlspMrpMO(models.Model):
    _inherit = 'mrp.production'
    _check_company_auto = True

    flsp_mrp_work_center_id = fields.Many2one('flsp.mrp.work.center', string="Work Center", required=True)
