# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class flspmrpwipproduction(models.Model):
    _inherit = 'stock.picking'
    _check_company_auto = True

    flsp_mo_wip_id = fields.Many2one('mrp.production', string="MO")
