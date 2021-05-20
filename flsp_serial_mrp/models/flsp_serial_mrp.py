# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class FlspSerialMRP(models.Model):
    _name = 'flsp.serial.mrp'
    _description = "Serial/Lot into MO"

    mo_id = fields.Many2one('mrp.production', string="MO")
    product_id = fields.Many2one('product.product', string='Product')
    finished_lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', )
    component_id = fields.Many2one('product.product', string='Component')
    component_lot_id = fields.Many2one('stock.production.lot', 'Component Lot/Serial', )
    qty = fields.Float('Qty')
