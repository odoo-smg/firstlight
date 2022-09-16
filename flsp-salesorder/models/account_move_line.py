# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class flspaccountmoveline(models.Model):
    _inherit = 'account.move.line'

    flsp_customerscode = fields.Many2one('flspstock.customerscode', 'Customer Part Number')

    def _copy_data_extend_business_fields(self, values):
        # OVERRIDE to copy the 'sale_line_ids' field as well.
        super(flspaccountmoveline, self)._copy_data_extend_business_fields(values)
        values['sale_line_ids'] = [(6, None, self.sale_line_ids.ids)]
        values['flsp_customerscode'] = self.flsp_customerscode


class FixMigrationAccount(models.Model):
    _inherit = 'account.move'

    # This action was created during the migration to 15
    # Some xml is calling this action and giving an error
    def button_process_edi_web_services(self):
        print('chekcing')