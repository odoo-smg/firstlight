# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Smgproduct(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    @api.model
    def _default_nextprefix(self):
        self._cr.execute("select max(default_code) as code from product_product where default_code like '1%' and length(default_code) = 10 ")
        retvalue = self._cr.fetchall()
        returned_registre = retvalue[0]
        return self._get_next_prefix(returned_registre[0])

    # Change description and set it as mandatory
    default_code = fields.Char(string="Internal Reference", readonly=True)

    # New fields to compose the part number
    legacy_code = fields.Char(string="Legacy Part #")
    flsp_part_prefix = fields.Char(string="Part # Prefix", default=_default_nextprefix)
    flsp_part_suffix = fields.Char(string="Part # Suffix", default="000")

    # New fields to control ECO enforcement
    flsp_eco_enforce = fields.Many2one('mrp.eco', string="ECO", store=False)
    flsp_allow_edit  = fields.Boolean(string="Allow Edit", store=False )

    # constraints to validate code and description to be unique
    _sql_constraints = [
        ('default_code_name_check_flsp5',
         'CHECK(name != default_code)',
         "The Name of the product should not be the product code"),

        ('default_code_unique_flsp5',
         'UNIQUE(default_code)',
         "The Product Code must be unique"),

        ('name_unique_flsp5',
         'UNIQUE(name)',
         "The Product name must be unique"),
    ]


    @api.model
    def _get_next_prefix(self, currpartnum):
        retvalue = ''
        if not currpartnum:
            currpartnum = '00001'
        if (currpartnum[0:1]!='1'):
            retvalue = '00001'
        else:
            retvalue = ('00000'+str(int(currpartnum[1:6])+1))[-5:]
        return retvalue


    @api.onchange('flsp_part_suffix')
    def flsp_part_suffix_onchange(self):
        if not(self.flsp_part_suffix):
            suffix = '000'
        else:
            suffix = self.flsp_part_suffix

        if not(self.flsp_part_prefix):
            prefix = '00000'
        else:
            prefix = self.flsp_part_prefix

        return_val = '1'+('00000' + prefix.replace("_", ""))[-5:] + '-' + ('000' + suffix.replace("_", ""))[-3:]
        self.default_code = return_val
        return {
            'value': {
                'default_code': return_val
            },
        }

    @api.onchange('flsp_part_prefix')
    def flsp_part_prefix_onchange(self):

        if not(self.flsp_part_suffix):
            suffix = '000'
        else:
            suffix = self.flsp_part_suffix

        if not(self.flsp_part_prefix):
            prefix = '00000'
        else:
            prefix = self.flsp_part_prefix

        return_val = '1'+('00000' + prefix.replace("_", ""))[-5:] + '-' + ('000' + suffix.replace("_", ""))[-3:]
        self.default_code = return_val
        return {
            'value': {
                'default_code': return_val
            },
        }

    def copy(self, default=None):
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

        default['default_code'] = '1'+prefix+'-'+suffix
        default['flsp_part_suffix'] = suffix
        default['flsp_part_prefix'] = prefix
        return super(Smgproduct, self).copy(default)
