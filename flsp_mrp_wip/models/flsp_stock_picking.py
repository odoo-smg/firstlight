# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class flspmrpwipproduction(models.Model):
    _inherit = 'stock.picking'

    flsp_mo_wip_id = fields.Many2one('mrp.production', string="MO")
