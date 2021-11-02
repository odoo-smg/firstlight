from odoo import fields, models, api, _
from psycopg2 import Error
import logging
_logger = logging.getLogger(__name__)

class FlspNegativeForecastStock(models.Model):
    _name = 'flsp.negative.forecast.stock'
    _description = "Negative Forecasted Stock"

    product_id = fields.Many2one('product.product', string='Product')
    product_name = fields.Char(related='product_id.display_name', string='Product')
    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    purcahseable = fields.Selection(related='product_id.flsp_route_buy', string='Purcahseable')
    manufacturable = fields.Selection(related='product_id.flsp_route_mfg', string='Manufacturable')
    negative_forecast_qty = fields.Float(string='Negative Qty')
    negative_forecast_date = fields.Date(string='Negative By')
    non_negative_forecast_qty = fields.Float(string='Non Negative Qty')
    non_negative_forecast_date = fields.Date(string='Non Negative By')
    duration = fields.Float(string='Duration', compute='_compute_duration')

    @api.depends('negative_forecast_date', 'non_negative_forecast_date')
    def _compute_duration(self):
        for r in self:
            if r.negative_forecast_date and r.non_negative_forecast_date:
                elapsed_seconds = (r.non_negative_forecast_date - r.negative_forecast_date).total_seconds()
                seconds_in_day = 24 * 60 * 60
                r.duration = elapsed_seconds / seconds_in_day
            else:
                r.duration = False

    @api.model
    def _update_product_flsp_routes(self, calculateFlspRoutes):
        # scan all products and make sure their fields 'flsp_route_buy' and 'flsp_route_mfg' are up-to-date
        if not calculateFlspRoutes:
            return

        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id
        route_mfg = self.env.ref('mrp.route_warehouse0_manufacture').id
        products = self.env['product.product'].search([])
        for prod in products:
            if route_buy in prod.route_ids.ids:
                prod.flsp_route_buy = 'buy'
            else:
                prod.flsp_route_buy = 'na'

            if route_mfg in prod.route_ids.ids:
                prod.flsp_route_mfg = 'mfg'
            else:
                prod.flsp_route_mfg = 'na'

    @api.model
    def _update_report_data(self):
        query_unlink = """ DELETE FROM flsp_negative_forecast_stock"""

        query_create = """
                    WITH
                        neg AS (
                            SELECT product_id, pt.name as description, pt.default_code,  min(date) as date
                            FROM report_stock_quantity
							inner join product_product as pp on pp.id = product_id
							inner join product_template as pt on pt.id = pp.product_tmpl_id
                            WHERE date >= current_date and report_stock_quantity.company_id = %s and product_qty < 0 and report_stock_quantity.state = 'forecast'
                            GROUP BY product_id, pt.name, pt.default_code
                        ),
                        negreport AS (
                            SELECT r.product_id, pt.name as description, pt.default_code, r.date, r.product_qty
                            FROM report_stock_quantity as r,neg
							inner join product_product as pp on pp.id = product_id
							inner join product_template as pt on pt.id = pp.product_tmpl_id
                            WHERE r.product_id = neg.product_id and r.date = neg.date and r.company_id = %s and r.state = 'forecast'
                        ),
                        nonneg AS (
                            SELECT r.product_id, pt.name as description, pt.default_code, min(r.date) as date
                            FROM report_stock_quantity as r,neg
							inner join product_product as pp on pp.id = product_id
							inner join product_template as pt on pt.id = pp.product_tmpl_id
                            WHERE r.product_id = neg.product_id and r.date > neg.date and r.company_id = %s and r.product_qty >= 0 and r.state = 'forecast'
                            GROUP BY r.product_id, pt.name, pt.default_code
                        ),
                        nonnegreport AS (
                            SELECT r.product_id, pt.name as description, pt.default_code, r.date, r.product_qty
                            FROM report_stock_quantity as r,nonneg
							inner join product_product as pp on pp.id = product_id
							inner join product_template as pt on pt.id = pp.product_tmpl_id
                            WHERE r.product_id = nonneg.product_id and r.date = nonneg.date and r.company_id = %s  and r.state = 'forecast'
                        )
                    INSERT INTO flsp_negative_forecast_stock (product_id, description, default_code, negative_forecast_date, negative_forecast_qty, non_negative_forecast_date, non_negative_forecast_qty)
                    SELECT negreport.product_id, negreport.description, negreport.default_code, CAST(negreport.date AS DATE), negreport.product_qty, CAST(nonnegreport.date AS DATE), nonnegreport.product_qty
                    FROM negreport
				    LEFT JOIN nonnegreport
                    ON negreport.product_id = nonnegreport.product_id
                """
        query_create_params = (self.env.company.id, self.env.company.id, self.env.company.id, self.env.company.id)

        try:
            with self.env.cr.savepoint():
                self.env.cr.execute(query_unlink)
                self.env.cr.execute(query_create, query_create_params)
        except Error as e:
            _logger.info("an error occured while updating database 'flsp_negative_forecast_stock': %s", e.pgerror)

    @api.model
    def action_calculate_negative_forecast(self, calculateFlspRoutes=True):
        # update product data
        self._update_product_flsp_routes(calculateFlspRoutes)

        # update report data in DB
        self._update_report_data()

    @api.model
    def view_negative_forecast_report(self):
        action = {
            'name': _('Negative Forecasted Inventory'),
            'res_model': 'flsp.negative.forecast.stock',
            'view_mode': 'tree',
            'type': 'ir.actions.act_window',
            'context': {},
            'help': """
                <p class="o_view_nocontent_empty_folder">No Negative Forecasted Inventory</p>
                """
        }
        return action

    @api.model
    def action_view_negative_forecast(self, calculateFlspRoutes=True):
        # update data
        self.action_calculate_negative_forecast(calculateFlspRoutes)

        # set view for the page to show up
        return self.view_negative_forecast_report()
