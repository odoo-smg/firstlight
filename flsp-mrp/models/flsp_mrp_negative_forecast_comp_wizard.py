# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class FlspMrpNegativeForecastCompWizard(models.TransientModel):
    _name = 'flsp.mrp.comp.wizard'
    _description = "Display component products with negative forecast for the MO"
    
    mo_id = fields.Many2one('mrp.production', string="MO", required=True)
    negative_forecast_components = fields.Many2many('flsp.negative.forecast.stock', string='Negative Forecast Components')
        
    @api.model
    def default_get(self, fields):
        res = super(FlspMrpNegativeForecastCompWizard, self).default_get(fields)

        default_mo_id = self.env.context.get('default_mo_id')
        if default_mo_id:
            mo = self.env['mrp.production'].browse(default_mo_id)
            if mo.exists():
                res['mo_id'] = mo.id
                res['negative_forecast_components'] = self.env['flsp.negative.forecast.stock'].search([('product_id', 'in', mo.move_raw_ids.product_id.ids)])
            else:
                _logger.warning("The REQUIRED MO does NOT exist!")
        else:
            _logger.warning("The REQUIRED 'default_mo_id' is None!")
            
        res = self._convert_to_write(res)
        return res

    @api.model
    def view_negative_forecast_component(self, mo_id):
        view_id = self.env.ref('flsp-mrp.flspmrp_negative_forecast_components_form_view').id
        return {
            'name': 'FLSP - Negative Forecast Components',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flsp.mrp.comp.wizard',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_mo_id': mo_id.id,
            }
        }
        
    @api.model
    def view_negative_forecast_components_after_recompute(self, mo_id, calculateFlspRoutes=True):
        # update data
        self.env['flsp.negative.forecast.stock'].action_calculate_negative_forecast(calculateFlspRoutes)

        # set view for the page to show up
        return self.view_negative_forecast_component(mo_id)