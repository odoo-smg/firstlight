from odoo import models, fields, api, exceptions


class FlspMrpSubstitutionLine(models.Model):
    _name = "flsp.mrp.substitution.line"
    _description = 'Substitution products for BOM'
    _check_company_auto = True

    flsp_bom_id = fields.Many2one('mrp.bom')
    bom_line_id = fields.Many2one('mrp.bom.line', 'Bom Line')
    company_id = fields.Many2one(related='flsp_bom_id.company_id', store=True, index=True, readonly=True)
    sequence = fields.Integer(string='Sequence')
    product_id = fields.Many2one('product.product', 'Component')
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id', readonly=False)
    product_qty = fields.Float('Quantity', digits='Quantity', compute='_compute_product_qty')
    product_uom_id = fields.Many2one('uom.uom', 'UofM', compute='_compute_product_uom_id')
    product_substitute_id = fields.Many2one('product.product', 'Substitute Component', required=True, check_company=True)
    product_substitute_uom_id = fields.Many2one('uom.uom', 'Substitute Unit of Measure')
    product_substitute_qty = fields.Float('Substitute Qty', default=1.0, digits='Product Unit of Measure', required=True)

    @api.model
    def default_get(self, fields):
        res = super(FlspMrpSubstitutionLine, self).default_get(fields)
        if 'product_id' in fields:
            res['product_id'] = False
        return res

    @api.onchange('product_substitute_id')
    def onchange_product_sub_id(self):
        if self.product_substitute_id:
            self.product_substitute_uom_id = self.product_substitute_id.uom_id.id

    @api.depends('product_id')
    def _compute_product_uom_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
        else:
            self.product_uom_id = False

    @api.depends('product_id')
    def _compute_product_qty(self):
        ret_val = 0
        bom_line_id = False
        if self.flsp_bom_id:
            if len(self) == 1:
                for line in self.flsp_bom_id.bom_line_ids:
                    if self.product_id.id == line.product_id.id:
                        ret_val = line.product_qty
                        bom_line_id = line.id
                self.bom_line_id = bom_line_id
                self.product_qty = ret_val
            else:
                for sub_line in self:
                    if sub_line.product_id:
                        if len(self.flsp_bom_id.bom_line_ids) > 0:
                            for line in self.flsp_bom_id.bom_line_ids:
                                if sub_line.product_id.id == line.product_id.id:
                                    sub_line.product_qty = line.product_qty
                                    sub_line.bom_line_id = line.id
                                    ret_val = line.product_qty

                        else:
                            sub_line.product_qty = 0
