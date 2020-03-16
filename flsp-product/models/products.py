# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Smgproduct(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    @api.model
    def _default_nextprefix(self):
        flsp_default_part_init = self.env['ir.config_parameter'].sudo().get_param('product.template.flsp_part_init')[:1]
        self._cr.execute("select max(default_code) as code from product_product where default_code like '"+flsp_default_part_init+"%' and length(default_code) = 10 ")
        retvalue = self._cr.fetchall()
        returned_registre = retvalue[0]
        return self._get_next_prefix(returned_registre[0])

    @api.model
    def _next_default_code(self):
        flsp_default_part_init = self.env['ir.config_parameter'].sudo().get_param('product.template.flsp_part_init')[:1]
        self._cr.execute("select max(default_code) as code from product_product where default_code like '"+flsp_default_part_init+"%' and length(default_code) = 10 ")
        retvalue = self._cr.fetchall()
        returned_registre = retvalue[0]
        next_prefix = self._get_next_prefix(returned_registre[0])
        next_suffix = '000'
        return flsp_default_part_init+next_prefix+'-'+next_suffix

    # Change description and set it as mandatory
    default_code = fields.Char(string="Internal Reference", default=_next_default_code, force_save=True)

    # New fields to compose the part number
    legacy_code = fields.Char(string="Legacy Part #")
    flsp_part_prefix = fields.Char(string="Part # Prefix", default=_default_nextprefix)
    flsp_part_suffix = fields.Char(string="Part # Suffix", default="000")


    # constraints to validate code and description to be unique
    _sql_constraints = [
        ('default_code_name_check_flsp6',
         'CHECK(name != default_code)',
         "The Name of the product should not be the product code"),

        ('default_code_unique_flsp6',
         'UNIQUE(default_code)',
         "The Product Code must be unique"),

        ('name_unique_flsp6',
         'UNIQUE(name)',
         "The Product name must be unique"),
    ]


    @api.model
    def _get_next_prefix(self, currpartnum):
        flsp_default_part_init = self.env['ir.config_parameter'].sudo().get_param('product.template.flsp_part_init')[:1]
        retvalue = ''
        if not currpartnum:
            currpartnum = '00001'
        if (currpartnum[0:1]!=flsp_default_part_init):
            retvalue = '00001'
        else:
            retvalue = ('00000'+str(int(currpartnum[1:6])+1))[-5:]
        return retvalue


    @api.onchange('flsp_part_suffix')
    def flsp_part_suffix_onchange(self):
        flsp_default_part_init = self.env['ir.config_parameter'].sudo().get_param('product.template.flsp_part_init')[:1]
        if not(self.flsp_part_suffix):
            suffix = '000'
        else:
            suffix = self.flsp_part_suffix
        if not(self.flsp_part_prefix):
            prefix = '00000'
        else:
            prefix = self.flsp_part_prefix
        return_val = flsp_default_part_init+('00000' + prefix.replace("_", ""))[-5:] + '-' + ('000' + suffix.replace("_", ""))[-3:]
        self.default_code = return_val
        return {
            'value': {
                'default_code': return_val
            },
        }

    @api.onchange('flsp_part_prefix')
    def flsp_part_prefix_onchange(self):
        flsp_default_part_init = self.env['ir.config_parameter'].sudo().get_param('product.template.flsp_part_init')[:1]
        if not(self.flsp_part_suffix):
            suffix = '000'
        else:
            suffix = self.flsp_part_suffix
        if not(self.flsp_part_prefix):
            prefix = '00000'
        else:
            prefix = self.flsp_part_prefix
        return_val = flsp_default_part_init+('00000' + prefix.replace("_", ""))[-5:] + '-' + ('000' + suffix.replace("_", ""))[-3:]
        self.default_code = return_val
        return {
            'value': {
                'default_code': return_val
            },
        }

    def copy(self, default=None):
        flsp_default_part_init = self.env['ir.config_parameter'].sudo().get_param('product.template.flsp_part_init')[:1]
        default = dict(default or {})

        if not(self.flsp_part_suffix):
            suffix = '000'
        else:
            suffix = str(int(self.flsp_part_suffix)+1)+""

        if not(self.flsp_part_prefix):
            prefix = '00000'
        else:
            prefix = self.flsp_part_prefix

        suffix = ('000'+str(int(suffix)))[-3:]

        default_init = self.default_code[:1]

        default['default_code'] = default_init+prefix+'-'+suffix
        default['flsp_part_suffix'] = suffix
        default['flsp_part_prefix'] = prefix
        default['flsp_plm_valid'] = False
        return super(Smgproduct, self).copy(default)
