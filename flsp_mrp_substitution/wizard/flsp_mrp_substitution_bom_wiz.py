# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class FlspMrpSubsBomWiz(models.TransientModel):
    _name = 'flsp.mrp.sub.bom.wiz'
    _description = "Wizard: BOM Selection"

    product_id = fields.Many2one('product.template', string='Product', readonly=True)
    substitute_id = fields.Many2one('product.product', string='Substitute', readonly=True)
    flsp_mrp_bom_line_ids = fields.One2many('flsp.mrp.sub.bom.line.wiz', 'flsp_mrp_sub_product_id', string='BOMs')
    plm_valid = fields.Boolean(default=False)
    product_substituting = fields.Boolean(default=False)

    @api.model
    def default_get(self, fields):
        res = super(FlspMrpSubsBomWiz, self).default_get(fields)
        product_id = self.env.context.get('product_id')
        substitute_id = self.env.context.get('substitute_id')
        substituting = self.env.context.get('substituting')
        product = self.env['product.template'].browse(product_id)
        if product.exists():
            if 'product_id' in fields:
                res['product_id'] = product.id
            if 'substitute_id' in fields:
                res['substitute_id'] = substitute_id
            if 'plm_valid' in fields:
                res['plm_valid'] = product.flsp_plm_valid
            if 'product_substituting' in fields:
                res['product_substituting'] = substituting

        product_product = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])

        if product_product.exists():
            bom_list = []
            bom_lines = self.env['mrp.bom.line'].search([('product_id', '=', product_product.id)])
            for bom_line in bom_lines:

                # only show active BOMs
                if not bom_line.bom_id.active:
                    continue

                # check in the bom if the product matches with the substitute
                # only because we could have many substitute products for each component.
                active = False
                substitute = self.env["flsp.mrp.substitution.line"].search([('bom_line_id', '=', bom_line.id)])
                if substitute:
                    if substitute.product_substitute_id.id == substitute_id:
                        active = True

                # Checking if the selection was saved before
                bom_substituting = self.env['flsp.mrp.substitution.bom'].search(['&',
                                                                                 ('product_id', '=', product.id),
                                                                                 ('bom_line_id', '=', bom_line.id)])
                if bom_substituting:
                    active = bom_substituting.substituting

                # checking active flag in the main product
                if not substituting:
                    active = False

                bom_list.append([0, 0, {
                    'flsp_mrp_sub_product_id': self.id,
                    'bom_id': bom_line.bom_id.id,
                    'bom_line_id': bom_line.id,
                    'substituting': active,
                    'product_plm_valid': product.flsp_plm_valid,
                }])
                #for each in bom_list:
                #    print(each)
            res['flsp_mrp_bom_line_ids'] = bom_list

        res = self._convert_to_write(res)
        return res


    def flsp_confirm(self):
        self.ensure_one()

        # Checking the saved substituting: This will be confirmed when the ECO is validated.
        for each in self.flsp_mrp_bom_line_ids:
            bom_substituting = self.env['flsp.mrp.substitution.bom'].search(['&',
                                                                              ('bom_line_id', '=', each.bom_line_id.id),
                                                                              ('substitute_id', '=', self.substitute_id.id)])
            active = self.product_substituting
            if bom_substituting:
                bom_substituting.substituting = each.substituting
                if not active:
                    bom_substituting.substituting = False
            else:
                if not active:
                    substituting = False
                else:
                    substituting = each.substituting
                self.env['flsp.mrp.substitution.bom'].create({
                    'substituting': substituting,
                    'substitute_id': self.substitute_id.id,
                    'bom_line_id': each.bom_line_id.id,
                    'product_id': self.product_id.id,
                })


        # Checking for deleted/archived BOMs.
        boms_substituting = self.env['flsp.mrp.substitution.bom'].search([('product_id', '=', self.product_id.id)])
        for each in boms_substituting:
            should_delete = True
            for line in self.flsp_mrp_bom_line_ids:
                if each.bom_line_id.id == line.bom_line_id.id:
                    should_delete = False
            if should_delete:
                each.unlink()

        ## This action should be performed at the Autotmated Actions when the ECO is confirmed.
        ## self.env['flsp.mrp.substitution.bom'].apply_substitution(self.product_id)

        return {'type': 'ir.actions.act_window_close'}


class FlspMRPSubsBomWiz(models.TransientModel):
    _name = 'flsp.mrp.sub.bom.line.wiz'
    _description = "Wizard: BOM Selection"

    substituting = fields.Boolean(default=False)
    flsp_mrp_sub_product_id = fields.Many2one('flsp.mrp.sub.bom.wiz')
    bom_id = fields.Many2one('mrp.bom', string="Bom")
    bom_line_id = fields.Many2one('mrp.bom.line', string="Bom Line")
    product_plm_valid = fields.Boolean(default=False)
