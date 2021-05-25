
from odoo import api, fields, models, modules
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    flsp_part_init = fields.Char(string="First Digit Part #", implied_group='product.template.flsp_part_init', default='1')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            flsp_part_init = self.get_flsp_part_init(),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('product.template.flsp_part_init', self.flsp_part_init)

    def get_flsp_part_init(self):
        param_flsp_part_init = self.env['ir.config_parameter'].sudo().get_param('product.template.flsp_part_init')
        if param_flsp_part_init:
            flsp_part = param_flsp_part_init[:1]
        else:
            flsp_part = '1' # default value for flsp_part_init
        return flsp_part
        
    @api.model
    def config_flsp_global_features_for_install(self):
        # update configurations on "Odoo -> Settings" page with selections on each sub pages for FLSP

        # sub page "First Light"
        self.enable_feature('flsp_part_init', 'product.template.flsp_part_init', '1')
        # sub page "Sales", defined in \addons\product\models\res_config_settings.py
        self.enable_feature('group_discount_per_so_line', 'product.group_discount_per_so_line', True)
        self.enable_feature('group_uom', 'uom.group_uom', True)
        self.enable_feature('group_stock_packaging', 'product.group_stock_packaging', True)
        self.enable_feature('group_product_pricelist', 'product.group_product_pricelist', True)
        self.enable_feature('product_pricelist_setting', 'product.product_pricelist_setting', 'advanced')
        self.enable_feature('group_sale_pricelist', 'product.group_sale_pricelist', True)
        # sub page "Sales", defined in \addons\sale\models\res_config_settings.py
        self.enable_feature('group_sale_delivery_address', 'sale.group_delivery_invoice_address', True)
        # sub page "Purchase", defined in \addons\purchase_stock\models\res_config_settings.py
        self.enable_feature('module_stock_dropshipping', 'Dropshipping', True)
        # sub page "Inventory", defined in \addons\stock\models\res_config_settings.py
        self.enable_feature('group_stock_tracking_lot', 'stock.group_tracking_lot', True)
        self.enable_feature('group_stock_production_lot', 'stock.group_production_lot', True)
        self.enable_feature('group_lot_on_delivery_slip', 'stock.group_lot_on_delivery_slip', True)
        self.enable_feature('group_stock_multi_locations', 'stock.group_stock_multi_locations', True)
        # sub page "Invoice", defined in \addons\base_setup\models\res_config_settings.py
        self.enable_feature('group_multi_currency', 'base.group_multi_currency', True)
        # sub page "Invoice", "currency_id", defined in \addons\account\models\res_config_settings.py
        self.currency_id = self.get_flsp_default_currency()

    def enable_feature(self, field_name, name_in_parameters, value):
        # update res.config.settings
        res_config = self.env['res.config.settings']
        res_values = res_config.default_get(list(res_config.fields_get()))
        res_values.update( { field_name: value } )
        res_config.create(res_values).execute()

        # update ir.config_parameter
        self.env['ir.config_parameter'].sudo().set_param(name_in_parameters, value)
        
    def get_flsp_default_currency(self):
        # set CAD(id=4) as an active currencies, keep USD(id=2) as an active currencies, set EUR(id=1) as an inactive one
        currencies = self.env['res.currency'].browse([1, 4])
        currency_eur = currencies[0]
        if currency_eur:
            currency_eur.active = False
        currency_cad = currencies[1]
        if currency_cad and (not currency_cad.active):
            currency_cad.active = True

        # set CAD as default currency
        self.company_id.currency_id = currency_cad.id

        return currency_cad.id
