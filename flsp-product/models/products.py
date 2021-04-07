# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from odoo.exceptions import ValidationError

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
    default_code = fields.Char(string="Internal Reference", readonly=True)
    # Change default Can be Sold to False
    sale_ok = fields.Boolean('Can be Sold', default=False)

    # New fields to compose the part number
    legacy_code = fields.Char(string="Legacy Part #")
    flsp_part_prefix = fields.Char(string="Part # Prefix", default=_default_nextprefix)
    flsp_part_suffix = fields.Char(string="Part # Suffix", default="000")

    # New fields for sales approval
    flsp_min_qty = fields.Integer(string="Min. Qty Sale", default=1)

    attachment_ids = fields.Many2many('ir.attachment', 'product_attachment_rel','drawing_id', 'attachment_id',
        string='Attachments',
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.')

    # Account review enforcement
    #    if (self.env.uid != 8):
    flsp_acc_valid   = fields.Boolean(string="Accounting Validated", readonly=True, copy=False)

    # constraints to validate code and description to be unique
    _sql_constraints = [
        ('default_code_name_check_flsp6',
         'CHECK(name != default_code)',
         "The Name of the product should not be the product code"),

        ('default_code_unique_flsp6',
         'UNIQUE(default_code)',
         "The Product Code must be unique"),

        #('name_unique_flsp6',
        # 'UNIQUE(name)',
        # "The Product name must be unique"),
    ]

    def button_acc_valid(self):
        prd_prd = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        if prd_prd:
            prd_prd.flsp_acc_valid = True
        return self.write({'flsp_acc_valid': True})

    def button_acc_valid_off(self):
        prd_prd = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        if prd_prd:
            prd_prd.flsp_acc_valid = False
        return self.write({'flsp_acc_valid': False})

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

    #Modified Apr.7th.2021.W by Sami to account for wheather the product has default values
    def copy(self, default=None):
        flsp_default_part_init = self.env['ir.config_parameter'].sudo().get_param('product.template.flsp_part_init')[:1]
        default = dict(default or {})

        # Useful for Products with default values set in this case flsp-eco-reject
        if default:
            prefix = '00000'
            self._cr.execute(
                "select max(flsp_part_suffix) as suffix from product_template where active ='false'")
            table = self._cr.fetchall()
            for line in table:
                if type(line[0]) == str:
                    value = int(line[0])
                    suf = str(value + 1) + ""
                else:
                    suf = '0'
            suffix = suf
            default['default_code'] = '9'+prefix+'-'+suffix
            default['flsp_part_suffix'] = suffix
            default['flsp_part_prefix'] = prefix
            return super(Smgproduct, self).copy(default)

        else:
            # PREFIX INFORMATION
            if not(self.flsp_part_prefix):
                prefix = '00000'
            else:
                prefix = self.flsp_part_prefix

            # SUFFIX INFORMATION
            self._cr.execute(
                "select max(flsp_part_suffix) as suffix from product_template where flsp_part_prefix like '" + self.flsp_part_prefix + "%'")
                # "select max(flsp_part_suffix) as suffix from product_template where flsp_part_prefix like '" + self.flsp_part_prefix + "%' and length(default_code) = 10 ")
            table = self._cr.fetchall()
            for line in table:
                value = int(line[0])
            suf = value

            if not(self.flsp_part_suffix):
                suffix = '000'
            else:
                # suffix = str(int(self.flsp_part_suffix)+1)+""
                suffix = str(suf+1)+""

            suffix = ('000'+str(int(suffix)))[-3:]
            default_init = self.default_code[:1]

            default['default_code'] = default_init+prefix+'-'+suffix
            default['flsp_part_suffix'] = suffix
            default['flsp_part_prefix'] = prefix
            if 'flsp_plm_valid' in self.env['product.template']._fields:
                default['flsp_plm_valid'] = False
            return super(Smgproduct, self).copy(default)


    @api.constrains('name') #,'flsp_part_prefix')
    def _constraint_only_unique_name(self):
        """
            Date:    Nov/19th/2020/Thursday
            Purpose: To create only unique names
                     To raise exception if name is used but prefix don't match
	    Modified:Apr/7th/W to account for whether the product is active
            Author: Sami Byaruhanga
        """
        self._cr.execute('''
            SELECT id pdct_id, name, flsp_part_prefix, default_code, active from product_template

        ''')

        res = self._cr.fetchall() #returns all
        for line in res:
            if line[4]: #accoung for whether the product is active
                if self.name == line[1] and self.flsp_part_prefix != line[2]:
                    raise ValidationError('Name already used on product with default code: ' + line[3] +
                                      '\nTo use this name you must use the matching Part # Prefix: ' + line[2] +
                                      ' and increment the Part # Suffix'
                                      )

