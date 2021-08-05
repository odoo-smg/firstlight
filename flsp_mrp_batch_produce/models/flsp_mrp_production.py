# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class flspmrpbatchproduction(models.Model):
    _inherit = 'mrp.production'
    _check_company_auto = True

    flsp_batch_serial_id = fields.Many2one('flsp.serialnum', string="Serial Batch")
    flsp_is_serial = fields.Boolean(string="Is Serial", compute="_flsp_compute_serial")

    @api.depends('product_id')
    def _flsp_compute_serial(self):
        if self.product_id.tracking == 'serial':
            self.flsp_is_serial = True
        else:
            self.flsp_is_serial = False