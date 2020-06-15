# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flspchoosedelivery(models.TransientModel):
    _inherit = 'choose.delivery.carrier'
    _check_company_auto = True
    manually_update = fields.Boolean("Manually Update")

'''    def _get_shipment_rate(self):
        vals = self.carrier_id.rate_shipment(self.order_id)
        if vals.get('success'):
            self.delivery_message = vals.get('warning_message', False)
            if self.manually_update:
                self.delivery_price = self.display_price
            else:
                self.delivery_price = vals['price']
                self.display_price = vals['carrier_price']
            return {}
        return {'error_message': vals['error_message']}
'''
