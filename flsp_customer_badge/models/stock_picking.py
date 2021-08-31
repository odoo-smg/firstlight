from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
import logging
_logger = logging.getLogger(__name__)


class flspCustomerBadgestockpicking(models.Model):
    _inherit = 'stock.picking'
    _check_company_auto = True

    # fields for customer badge(cb)
    flsp_cb_id = fields.Many2one(related='partner_id.flsp_cb_id', readonly=True)
    flsp_cb_image = fields.Image(related='flsp_cb_id.image_1920', readonly=True)
    flsp_cb_sale_discount = fields.Float(related='flsp_cb_id.sale_discount', readonly=True)
    flsp_cb_freight_units_5_to_10_discount = fields.Float(related='flsp_cb_id.freight_units_5_to_10_discount', readonly=True)
    flsp_cb_freight_units_over_10_discount = fields.Float(related='flsp_cb_id.freight_units_over_10_discount', readonly=True)
