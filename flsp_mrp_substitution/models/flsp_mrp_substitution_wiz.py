# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import logging

_logger = logging.getLogger(__name__)


class FlspMrpSubstitutionWiz(models.TransientModel):
    _name = 'flsp_mrp_substitution.wiz'
    _description = "Wizard: Product Substitution"

    flsp_bom_id = fields.Many2one('mrp.bom')
    mo_id = fields.Many2one('mrp.production')
    move_id = fields.Many2one('stock.move')
    product_id = fields.Many2one('product.product', 'Product')
    product_qty = fields.Float('Quantity')

    flsp_sub_products_ids = fields.One2many('product.product', string='Substitute Products', compute='_compute_sub_products_ids')

    substitute_id = fields.Many2one('product.product', 'Substitute')
    substitute_qty = fields.Float('Substitute Qty')

    flsp_substitution_line_ids = fields.One2many('flsp_mrp_substitution.wiz.line', 'flsp_bom_id', string='Components')

    @api.onchange('substitute_id')
    def change_substitute_id(self):
        for line in self.flsp_substitution_line_ids:
            if self.substitute_id == line.product_substitute_id:
                self.substitute_qty = line.product_substitute_qty

    @api.model
    def default_get(self, fields):
        res = super(FlspMrpSubstitutionWiz, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        stock_moves = self.env["stock.move"].search([("id", "=", active_id)])
        if stock_moves.exists():
            bom_id = stock_moves.raw_material_production_id.bom_id
            mo_id = stock_moves.raw_material_production_id
            components = self._get_flattened_totals(bom_id)
            prod_ids = []
            for line in components:
                if components[line]['prod'] == stock_moves.product_id:
                    prod_ids.append(components[line]['sub'].id)
            subs_list = self.env["product.product"].search([("id", "in", prod_ids)])
            if 'mo_id' in fields:
                res['mo_id'] = mo_id.id
            if 'move_id' in fields:
                res['move_id'] = stock_moves.id
            if 'flsp_bom_id' in fields:
                res['flsp_bom_id'] = bom_id.id
            if 'flsp_sub_products_ids' in fields:
                res['flsp_sub_products_ids'] = subs_list
            if 'product_id' in fields:
                res['product_id'] = stock_moves.product_id.id
            if 'product_qty' in fields:
                res['product_qty'] = stock_moves.product_uom_qty

            substitution_list = []
            for line in components:
                if components[line]['prod'] == stock_moves.product_id:
                    substitution_list.append([0, 0, {
                    'flsp_bom_id': bom_id.id,
                    'product_id': components[line]['prod'].id,
                    'product_qty': components[line]['qty'],
                    'product_substitute_id': components[line]['sub'].id,
                    'product_substitute_qty': components[line]['sub_qty'],
                }])
            res['flsp_substitution_line_ids'] = substitution_list

        res = self._convert_to_write(res)
        return res

    def apply_chnges(self):
        self.mo_id.button_unreserve()
        stock_move = self.move_id
        stock_move_lines = self.env["stock.move.line"].search([("move_id", "=", stock_move.id)])
        if stock_move_lines.exists():
            raise exceptions.ValidationError("It was not possible to unreserve this item.")
        else:
            #stock_move.create
            new_move = self.env['stock.move'].create({
                'name': 'Substitution',
                'sequence': stock_move.sequence,
                'reference': stock_move.reference,
                'raw_material_production_id': self.mo_id.id,
                'product_id': self.substitute_id.id,
                'product_uom': self.substitute_id.uom_id.id,
                'product_uom_qty': self.substitute_qty*self.mo_id.product_qty,
                'unit_factor': self.substitute_qty,
                'location_id': stock_move.location_id.id,
                'location_dest_id': stock_move.location_dest_id.id,
                'procure_method': stock_move.procure_method,
                #'group_id': stock_move.group_id.id,
                'picking_type_id': stock_move.picking_type_id.id,
                'warehouse_id': stock_move.warehouse_id.id,
                'state': stock_move.state,
            })
            print('-----> Just created:')
            print(new_move.reference)
            print('-----> Used Reference:')
            print(stock_move.reference)
            new_move.reference = stock_move.reference
            self.mo_id.message_post(body='-->> Product Substitution: <br/>'
                                    + ' The product ['+stock_move.product_id.default_code+'] '+ stock_move.product_id.name + '<br/>'
                                    + ' was substituted by ['+self.substitute_id.default_code+'] '+ self.substitute_id.name
                                    , subtype="mail.mt_note")
            stock_move.state = 'draft'
            stock_move.unlink()
            print('-----> After removing the old one:')
            print(new_move.reference)

    def _get_flattened_totals(self, bom_id, factor=1, totals=None, level=None):
        if totals is None:
            totals = {}
        for subs in bom_id.flsp_substitution_line_ids:
            totals[len(totals) + 1] = {'prod': subs.product_id, 'qty': subs.product_qty,
                                       'sub': subs.product_substitute_id, 'sub_qty': subs.product_substitute_qty}
        for line in bom_id.bom_line_ids:
            sub_bom = bom_id._bom_find(product=line.product_id)
            if sub_bom:
                if sub_bom.type == 'phantom':
                    for subs in sub_bom.flsp_substitution_line_ids:
                        totals[len(totals) + 1] = {'prod': subs.product_id, 'qty': subs.product_qty,
                                                   'sub': subs.product_substitute_id, 'sub_qty': subs.product_substitute_qty}
                self._get_flattened_totals(sub_bom, 1, totals, 2)
        return totals

    def _compute_sub_products_ids(self):
        self.flsp_sub_products_ids = self.flsp_sub_products_ids


class FlspMrpSubstitutionLineWiz(models.TransientModel):
    _name = "flsp_mrp_substitution.wiz.line"
    _description = 'Substitution products for MO'
    _check_company_auto = True

    flsp_bom_id = fields.Many2one('flsp_mrp_substitution.wiz')
    product_id = fields.Many2one('product.product', 'Component')
    product_qty = fields.Float('Quantity')
    product_substitute_id = fields.Many2one('product.product', 'Substitute Component')
    product_substitute_qty = fields.Float('Substitute Qty')
