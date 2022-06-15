from odoo import models, fields, api, exceptions


class FlspMrpSubstitutionLine(models.Model):
    _name = "flsp.mrp.substitution"
    _description = 'Substitute products for BOMs in the product'

    product_id = fields.Many2one('product.template', 'Component', default=lambda self: self.env.context.get('active_id'))
    product_substitute_id = fields.Many2one('product.product', 'Substitute', required=True)
    ratio = fields.Float("Ratio", required=True, default=1)
    substituting = fields.Boolean("Substituting", default=True)
    expire_date = fields.Date(string="Expire Date", default=False)

    def bom_selection(self):
        action = self.env.ref('flsp_mrp_substitution.launch_flsp_mrp_sub_bom_wiz').read()[0]
        action['context'] = {'product_id': self.product_id.id,
                             'substitute_id': self.product_substitute_id.id,
                             'substituting': self.substituting,}
        return action


class FlspMrpSubsBomLine(models.Model):
    _name = "flsp.mrp.substitution.bom"
    _description = 'BOMs for substitution'

    substituting = fields.Boolean("Substituting", default=True)
    bom_line_id = fields.Many2one('mrp.bom.line', string="Bom Line")
    product_id = fields.Many2one('product.template', string='Product', readonly=True)
    substitute_id = fields.Many2one('product.product', string='Substitute', readonly=True)

    def apply_substitution(self, product_template_id):
        if not product_template_id:
            return

        for substitute in product_template_id.flsp_substitute_ids:
            boms_for_subs = self.env['flsp.mrp.substitution.bom'].search(['&',
                                                                          ('product_id', '=', product_template_id.id),
                                                                          ('substitute_id', '=', substitute.product_substitute_id.id)])
            for sub_bom_line in boms_for_subs:
                print('id: ' + str(sub_bom_line.id) + ' bom id:' + str(sub_bom_line.bom_line_id.id))
                substitution_line = self.env['flsp.mrp.substitution.line'].search(['&',
                                                                                    ('bom_line_id', '=', sub_bom_line.bom_line_id.id),
                                                                                    ('product_substitute_id', '=', substitute.product_substitute_id.id)])
                if not substitution_line:
                    if sub_bom_line.substituting:
                        sub_bom_line.bom_line_id.flsp_substitute = True
                        product_id = self.env['product.product'].search([('product_tmpl_id', '=', sub_bom_line.product_id.id)])
                        self.env['flsp.mrp.substitution.line'].create({
                            'flsp_bom_id': sub_bom_line.bom_line_id.bom_id.id,
                            'bom_line_id': sub_bom_line.bom_line_id.id,
                            'sequence': 1,
                            'product_id': product_id.id,
                            'product_substitute_id': sub_bom_line.substitute_id.id,
                            'product_substitute_qty': sub_bom_line.bom_line_id.product_qty,
                            'product_substitute_uom_id': sub_bom_line.substitute_id.uom_id.id,
                        })
                else:
                    if not sub_bom_line.substituting:
                        sub_bom_line.bom_line_id.flsp_substitute = False
                        substitution_line.unlink()




