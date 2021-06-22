# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

import logging
_logger = logging.getLogger(__name__)

class FlspMrpProduceFilterLot(models.TransientModel):
    """
        Related classes:
            1) 'mrp.abstract.workorder', defined in \addons\mrp\models\mrp_abstract_workorder.py, with field 'lot_id'
            2) 'mrp.product.produce', defined in \addons\mrp\wizard\mrp_product_produce.py, inherits 'mrp.abstract.workorder'
        Purpose:
            1) inherit model 'mrp.product.produce' to check lot location, move.line location and mrp location 
    """
    
    _inherit = 'mrp.product.produce'

    def do_produce(self):
        # check lot locations before saving the produce
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        mrp_src_location = self.production_id.location_src_id
        for line in self._workorder_line_ids():
            if line.lot_id:
                lot_qty_at_location = self.get_lot_qty_at_location(line.lot_id.id, mrp_src_location.id)
                if float_compare(lot_qty_at_location, line.qty_to_consume, precision_digits=precision_digits) < 0:
                    raise UserError(
                        _(
"""The quantity of lot/SN at the MO's location is smaller than required, and it may result in negative stock.
Location of the Manufacuring Order %s is %s. 
The quantity of the lot/SN %s at the location is %s, but a number of %s is required. """
                        )
                        % (self.production_id.name, mrp_src_location.complete_name, line.lot_id.name, lot_qty_at_location, line.qty_to_consume)
                    )
        super(FlspMrpProduceFilterLot, self).do_produce()

    def get_lot_qty_at_location(self, lot_id, location_id):
        lot_qty = 0
        quants = self.env['stock.quant'].search([('lot_id', '=', lot_id), ('location_id', '=', location_id)])
        for q in quants:
            lot_qty += q.quantity
        return lot_qty
    
class FlspMrpProduceLineFilterLot(models.TransientModel):
    """
        Related classes:
            1) 'mrp.abstract.workorder.line', defined in \addons\mrp\models\mrp_abstract_workorder.py, with field 'lot_id'
            2) 'mrp.product.produce.line', defined in \addons\mrp\wizard\mrp_product_produce.py, inherits 'mrp.abstract.workorder.line'
        Purpose:
            1) inherit model 'mrp.product.produce.line' because abstract model 'mrp.abstract.workorder.line' cannot be used directly
            2) update field 'lot_id' with field parameter 'domain' in order to search lots with additional filters 
            3) add a new filed 'lot_candidates' to get default lot candidats for given product in the MO as the filters cannot be done in the 'domain' directly
    """
    
    _inherit = 'mrp.product.produce.line'

    def _get_default_lots(self):
        res = False
        mo_id = self.env.context.get('default_mo_id')
        if mo_id:
            mo = self.env['mrp.production'].browse(mo_id)
            if mo.exists():
                res = self.env['stock.quant'].search([('location_id', '=', mo.location_src_id.id), ('product_id', '=', self.product_id.id), ('quantity', '>', 0.0), '|', ('company_id', '=', False), ('company_id', '=', self.company_id.id)]).lot_id
        if not res:
            res = self.env['stock.quant'].search([('product_id', '=', self.product_id.id), ('quantity', '>', 0.0), '|', ('company_id', '=', False), ('company_id', '=', self.company_id.id)]).lot_id
        return res
    
    lot_candidates = fields.Many2many('stock.production.lot', string='Lots', default=_get_default_lots)
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', domain="[('id', 'in', lot_candidates)]")
