# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields


class Wizard(models.TransientModel):
    """
                Class_Name: Wizard
                Model_Name: flsp.product.delivery.wizard
                Purpose:    To pass the values inputed in the two date fields to the function
                            deliveryReportSearch in the class FlspProductDeliveryReport
                Date:       August.20.2021
                Author:     Kory McCarthy
            """
    _name = "flsp.product.delivery.report.wizard"
    _description = "Report of delivered products"

    startSearch = fields.Datetime(default=fields.Date.today(), required=True)
    endSearch = fields.Datetime(default=fields.Date.today(), required=True)

    def search_deliveries(self):
        """
        This method passes the user given start and end search dates to the main module
        and then load the view for that module
        """
        self.env['flsp.product.delivery.report'].deliveryReportSearch(self.startSearch, self.endSearch)
        action = self.env.ref('flsp_product_delivery_report.flsp_product_delivery_report_action').read()[0]
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action



