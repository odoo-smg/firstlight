# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class FlspMrpNegativeForecastWizard(models.TransientModel):
    _name = 'flsp.mrp.negative.forecast.wizard'
    _description = "Wizard: Recalculate MRP Negative Forecasted Report"

    mo_id = fields.Many2one('mrp.production', string="MO", required=True)
    calculate_product_flsp_routes = fields.Boolean(String="Calculate Product FLSP Routes", default=0, help="The calculation makes 'Purcahseable' and 'Manufacturable' update-to-date for each product in the report")
        
    @api.model
    def default_get(self, fields):
        res = super(FlspMrpNegativeForecastWizard, self).default_get(fields)

        default_mo_id = self.env.context.get('default_mo_id')
        if default_mo_id:
            mo = self.env['mrp.production'].browse(default_mo_id)
            if mo.exists():
                res['mo_id'] = mo.id
            else:
                _logger.warning("The REQUIRED MO does NOT exist!")
        else:
            _logger.warning("The REQUIRED 'default_mo_id' is None!")
            
        res = self._convert_to_write(res)
        return res

    def flsp_components_report(self):
        self.ensure_one()

        return self.env['flsp.mrp.comp.wizard'].view_negative_forecast_component(self.mo_id)

    def flsp_components_recalculate(self):
        return self.env['flsp.mrp.comp.wizard'].view_negative_forecast_components_after_recompute(self.mo_id, self.calculate_product_flsp_routes)