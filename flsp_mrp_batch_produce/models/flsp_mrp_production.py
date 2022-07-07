# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class flspmrpbatchproduction(models.Model):
    _inherit = 'mrp.production'
    _check_company_auto = True

    flsp_batch_list_ids = fields.One2many('flsp.serialnum', compute="flsp_compute_batch_list", string="My made batch")
    flsp_batch_serial_id = fields.Many2one('flsp.serialnum', string="Serial Batch", domain="['&', ('product_id', '=', product_id), '&', ('serial_count', '>=', product_qty), ('id', 'in', flsp_batch_list_ids)]")
    flsp_is_serial = fields.Boolean(string="Is Serial", compute="_flsp_compute_serial")

    @api.depends('product_id')
    def flsp_compute_batch_list(self):
        flsp_mrp_list = self.env['mrp.production'].search(['&', ('flsp_batch_serial_id', '!=', 'null'),
                                                           '&', ('product_id', '=', self.product_id.id), ('state', '!=', 'cancel')]).flsp_batch_serial_id

        flsp_mrp_list_ids = flsp_mrp_list.ids
        if flsp_mrp_list_ids:
            self.flsp_batch_list_ids = self.env['flsp.serialnum'].search(['&', ('name', '!=', 'null'),
                                                                          '&', ('id', 'not in', flsp_mrp_list_ids),
                                                                          ('product_id', '=', self.product_id.id)])
        else:
            self.flsp_batch_list_ids = False

    @api.depends('product_id')
    def _flsp_compute_serial(self):
        if self.product_id.tracking == 'serial':
            self.flsp_is_serial = True
        else:
            self.flsp_is_serial = False

    def copy(self, default=None):
        copied_mrp = super(flspmrpbatchproduction, self).copy(default=default)

        # Ticket 550: When a MO is duplicated, the batch serial number should be cleared
        copied_mrp.flsp_batch_serial_id = False

        return copied_mrp
