from odoo import fields, models, api, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from psycopg2 import Error

import logging
_logger = logging.getLogger(__name__)

class FlspQuantReservation(models.Model):
    _inherit = 'stock.quant'

    reservation_lines = fields.Many2many(string="Reservation Lines", comodel_name="stock.move.line", compute="_calc_reservation_lines")

    def _calc_reservation_lines(self):
        for record in self:
            record.reservation_lines = self.env['stock.move.line'].search([
                ('product_id', '=', record.product_id.id), 
                ('location_id', '=', record.location_id.id), 
                ('lot_id', '=', record.lot_id.id), 
                ('package_id', '=', record.package_id.id), 
                ('owner_id', '=', record.owner_id.id), 
                ('product_qty', '>', 0.0)])
        
