# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

    
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
