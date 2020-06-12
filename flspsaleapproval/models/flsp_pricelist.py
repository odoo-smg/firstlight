# -*- coding: utf-8 -*-

from odoo import api, fields, models


class flspsalespricelist(models.Model):
    _inherit = 'product.pricelist'
    _check_company_auto = True

    @api.model
    def _default_sppepp(self):
        return self.env['ir.config_parameter'].sudo().get_param('flsp_sppepp')

    flsp_SPPEPP = fields.Boolean(string="SPPEPP Active", default='_default_sppepp')
    flsp_SPPEPP_pl          = fields.Boolean(string="School PPE Purchase Program", store=True)
    flsp_SPPEPP_leadtime = fields.Selection([   ('4w', '4 Weeks'),
                                                ('10w', '10 Weeks'),
                                                ], string='Lead time', store=True, copy=False, default='10w')
    flsp_sale_type = fields.Selection([
        ('1', 'OEM'),
        ('2', 'Dealer'),
        ('3', 'School'),
        ('4', 'Contractor'),
        ], string='Sale Group',  default='4', required=True)


