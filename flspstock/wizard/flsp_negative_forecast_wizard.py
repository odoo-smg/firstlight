# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class FlspNegativeForecastWizard(models.TransientModel):
    _name = 'flsp.negative.forecast.wizard'
    _description = "Wizard: Recalculate Negative Forecasted Report"

    calculate_product_flsp_routes = fields.Boolean(String="Calculate Product FLSP Routes", default=0, help="The calculation makes 'Purcahseable' and 'Manufacturable' update-to-date for each product in the report")

    def flsp_report(self):
        self.ensure_one()

        return self.env['flsp.negative.forecast.stock'].view_negative_forecast_report()

    def flsp_recalculate(self):
        return self.env['flsp.negative.forecast.stock'].action_view_negative_forecast(self.calculate_product_flsp_routes)
