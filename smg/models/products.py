# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Smgproduct(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    legacy_code = fields.Char(string="Legacy Part #")
    revision_code = fields.Char(string="Revision")


    @api.model
    def _default_nextpart(self):
        self._cr.execute("select max(default_code) as code from product_product where default_code like '1%' and length(default_code) = 10 ")
        retvalue = self._cr.fetchall()
        returned_registre = retvalue[0]
        self.default_code = self._get_next_part(returned_registre[0])
        return self._get_next_part(returned_registre[0])

    # Change description and set it as mandatory
    default_code = fields.Char(string="Internal Reference", default=_default_nextpart, readonly=True)

    # constraints to validate code and description to be unique
    _sql_constraints = [
        ('default_code_name_check_flsp',
         'CHECK(name != default_code)',
         "The Name of the product should not be the product code"),

        ('default_code_unique_flsp',
         'UNIQUE(default_code)',
         "The Product Code must be unique"),

        ('name_unique_flsp',
         'UNIQUE(name)',
         "The Product name must be unique"),
    ]


    @api.model
    def _get_next_part(self, currpartnum):
        retvalue = ''
        if not currpartnum:
            currpartnum = '100000-000'
        if (currpartnum[0:1]!='1'):
            retvalue = '100001-000'
        else:
            retvalue = str(int(currpartnum[0:6])+1)+"-000"
        return retvalue


    @api.onchange('revision_code')
    def revision_code_onchange(self):
        if self.default_code:
            return_val = self.default_code[:6]
        else:
            return_val = self._default_nextpart()[:6]
        if not(self.revision_code):
            return_val = return_val+'-000'
        else:
            if (len(self.revision_code)>3):
                return {'warning': {
                    'title': "Revision -  Attention",
                    'message': "The field Revision cannot be bigger than 3 characters.",
                    },
                }
            return_val = return_val + '-' + ('000' + self.revision_code)[-3:]
        self.default_code = return_val
        return {
            'value': {
                'default_code': return_val
            },
        }
