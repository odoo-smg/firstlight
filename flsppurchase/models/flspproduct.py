# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_round


class flsppurchaseproductprd(models.Model):
    _inherit = 'product.product'
    _check_company_auto = True

    flsp_open_po_qty = fields.Float(compute='_compute_flsp_open_po_qty', string='Qty Open PO')
    flsp_bom_level = fields.Integer(string='Bom Level')

    def _flsp_calc_bom_level(self):
        print('Calculating level')
        current_level = 1
        next_level = {current_level: {}}
        print('Level 0')
        all_products = self.env['product.product'].search([])

        for lines in all_products:
            if lines.used_in_bom_count:
                lines.flsp_bom_level = -1
            else:
                lines.flsp_bom_level = current_level
                next_level[current_level][lines.product_tmpl_id.id] = lines

        complete = False
        while not complete and current_level < 10:
            current_level += 1
            print('Level ' + str(current_level) + '******************************************************')
            complete = True
            next_level[current_level] = {}
            for lines in all_products:
                if lines.flsp_bom_level < 0:
                    print('   Product' + str(lines.id))
                    comp_boms = self.env['mrp.bom.line'].search([('product_id', '=', lines.id)])
                    found_level = False
                    for parent_bom in comp_boms:
                        print('      Bom:' + str(parent_bom.bom_id.id))
                        if parent_bom.bom_id.product_tmpl_id.id in next_level[current_level - 1]:
                            lines.flsp_bom_level = current_level
                            next_level[current_level][lines.product_tmpl_id.id] = lines
                            found_level = True
                    if not found_level:
                        complete = found_level

    def _compute_flsp_open_po_qty(self):
        if not self.purchase_ok:
            for product in self:
                product.flsp_open_po_qty = 0.0
        else:
            domain = [
                ('flsp_open_qty', '>', 0),
                ('product_id', 'in', self.ids)
            ]
            order_lines = self.env['purchase.order.line'].search(domain)
            for product in self:
                if not product.id:
                    product.flsp_open_po_qty = 0.0
                    continue
                for line in order_lines:
                    product.flsp_open_po_qty += line.flsp_open_qty
        if not self.flsp_open_po_qty:
            self.flsp_open_po_qty = 0

    def action_view_open_po(self):
        action = self.env.ref('flsppurchase.action_purchase_order_line_all').read()[0]
        action['domain'] = ['&', ('product_id', 'in', self.ids), ('flsp_open_qty', '>', 0)]
        return action


class flsppurchaseproducttmp(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    flsp_open_po_qty = fields.Float(compute='_compute_flsp_open_po_qty', string='Qty Open PO')

    def _compute_flsp_open_po_qty(self):
        if not self.purchase_ok:
            for template in self:
                template.flsp_open_po_qty = 0
        else:
            for template in self:
                template.flsp_open_po_qty = float_round(sum([p.flsp_open_po_qty for p in template.product_variant_ids]), precision_rounding=template.uom_id.rounding)

    def action_view_open_po(self):
        product_prd = self.env['product.product'].search([('product_tmpl_id', 'in', self.ids)])
        action = self.env.ref('flsppurchase.action_purchase_order_line_all').read()[0]
        action['domain'] = ['&', ('product_id', '=', product_prd.ids), ('flsp_open_qty', '>', 0)]
        return action
