
from odoo import api, fields, models


class FlspBomSummarized(models.TransientModel):
    _name = "flsp.bom.summarized.wizard"
    _description = "MRP Summarized BOM"

    @api.model
    def default_get(self, fields):
        res = super(FlspBomSummarized, self).default_get(fields)
        bom_summary = self.env['flsp.bom.summarized'].search([])
        bom_list = []
        for line in bom_summary:
            bom_list.append([0, 0, {
                'product_id': line.product_id.id,
                'bom_id': line.bom_id.id,
                'product_tmpl_id': line.product_tmpl_id.id,
                'product_qty': line.product_qty,
            }])
        res['line_ids'] = bom_list
        res = self._convert_to_write(res)
        return res

    bom_id = fields.Many2one(comodel_name="mrp.bom", string="Starting Bill of Materials")
    product_id = fields.Many2one(comodel_name="product.product",string="Product",domain="[('type', 'in', ['product', 'consu'])]",)
    product_tmpl_id = fields.Many2one(comodel_name="product.template",string="Product Template",related="product_id.product_tmpl_id",)
    product_qty = fields.Float(related="bom_id.product_qty", digits="Product Unit of Measure")
    product_uom_id = fields.Many2one(comodel_name="uom.uom", related="bom_id.product_uom_id")
    location_id = fields.Many2one(comodel_name="stock.location", string="Starting location")
    line_ids = fields.One2many(comodel_name="flsp.bom.summarized.wizard.line", inverse_name="summary_id"
    )

    def confirm(self):
        summarized_list = self.env["flsp.bom.summarized"].search([])
        summarized_list.unlink()

        for line in self.line_ids:
            self.env["flsp.bom.summarized"].create({
                'product_id': line.product_id.id,
                'bom_id': line.bom_id.id,
                'product_tmpl_id': line.product_tmpl_id.id,
                'product_qty': line.product_qty,
            })

        self.do_explode()

        action = self.env.ref('flsp_mrp_summarized_bom.flsp_summarized_bom_action').read()[0]
        # Set ignore_session: read to prevent reading previous options
        action.update({'target': 'main', 'ignore_session': 'read', 'clear_breadcrumb': True})
        return action

    def clean_list(self):
        summarized_list = self.env["flsp.bom.summarized"].search([])
        summarized_list.unlink()
        for line in self.line_ids:
            line.unlink()
        self.line_ids = []
        return {
            "type": "ir.actions.act_window",
            "name": "Summarized Bom",
            "view_mode": "form",
            "res_model": "flsp.bom.summarized.wizard",
            "view_id": self.env.ref(
                "flsp_mrp_summarized_bom.flsp_summarized_bom_view_form"
            ).id,
            "target": "new",
            "res_id": self.id,
        }

    def do_explode(self):
        summarized_list_lines = self.env["flsp.bom.summarized.line"].search([])
        summarized_list_lines.unlink()

        def _create_lines(bom, level=0, factor=1):
            level += 1
            for bom_line in bom.bom_line_ids:
                bom_line_boms = bom_line.product_id.bom_ids
                if bom_line_boms:
                    line_qty = bom_line.product_uom_id._compute_quantity(bom_line.product_qty, bom_line_boms[0].product_uom_id)
                    new_factor = factor * line_qty / bom_line_boms[0].product_qty
                    _create_lines(bom_line_boms[0], level, new_factor)
                else:
                    summarized_list_lines.create({
                            'description': bom_line.product_tmpl_id.name,
                            'default_code': bom_line.product_tmpl_id.default_code,
                            'product_tmpl_id': bom_line.product_tmpl_id.id,
                            'product_id': bom_line.product_id.id,
                            'bom_id': bom_line.bom_id.id,
                            'level_bom': level,
                            'product_qty': bom_line.product_qty*factor,
                            'product_uom': bom_line.product_uom_id.id, })
        for line in self.line_ids:
            _create_lines(line.bom_id, 0, line.product_qty)


class FlspBomSummarizedLine(models.TransientModel):
    _name = "flsp.bom.summarized.wizard.line"
    _description = "MRP Summarized BOM Line"

    summary_id = fields.Many2one(comodel_name="flsp.bom.summarized.wizard")
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    bom_id = fields.Many2one(comodel_name="mrp.bom", string="BOM", required=True)
    product_qty = fields.Float(string="Quantity", required=True, default=1)
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Product Template",
        related="product_id.product_tmpl_id",
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
       if self.product_id:
           self.bom_id = self.env["mrp.bom"]._bom_find(product_tmpl=self.product_id)

class FlspMRPBomSummarized(models.Model):
    _name = "flsp.bom.summarized"
    _description = "MRP Summarized BOM"

    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    bom_id = fields.Many2one(comodel_name="mrp.bom", string="BOM", required=True)
    product_qty = fields.Float(string="Quantity", required=True, default=1)
    product_tmpl_id = fields.Many2one(comodel_name="product.template",string="Product Template",
        related="product_id.product_tmpl_id",
    )

class FlspMRPBomSummarizedLines(models.Model):

    _name = "flsp.bom.summarized.line"
    _description = "MRP Summarized BOM Details"

    description = fields.Char(string='Description', readonly=True)
    default_code = fields.Char(string='Part #', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    bom_id = fields.Many2one(comodel_name="mrp.bom", string="BOM")
    product_qty = fields.Float(string='Qty required', readonly=True)
    product_uom = fields.Many2one(comodel_name="uom.uom", string='UofM', readonly=True)
    level_bom = fields.Integer(string="BOM Level", readonly=True, help="Position of the product inside of a BOM.")

    def name_get(self):
        res = []
        for line in self:
            if line.default_code:
                name = 'Component: ' + line.default_code
            else:
                name = 'Component: ' + str(line.id)
            res.append((line.id, name))
        return res
